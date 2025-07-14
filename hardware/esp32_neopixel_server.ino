/*
 * ESP32 NeoPixel LED 제어 서버
 * 물품 관리 시스템에서 HTTP 요청을 받아 LED를 제어합니다.
 * 
 * 필요한 라이브러리:
 * - Adafruit NeoPixel
 * - WiFi
 * - ArduinoJson
 * - AsyncTCP
 * - ESPAsyncWebServer
 */

#include <WiFi.h>
#include <ESPAsyncWebServer.h>
#include <ArduinoJson.h>
#include <Adafruit_NeoPixel.h>

// WiFi 설정
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// NeoPixel 설정
#define LED_PIN 2        // ESP32의 GPIO 2번 핀
#define LED_COUNT 25     // 5x5 그리드 = 25개 LED
#define BRIGHTNESS 50    // 밝기 (0-255)

// 객체 생성
Adafruit_NeoPixel strip(LED_COUNT, LED_PIN, NEO_GRB + NEO_KHZ800);
AsyncWebServer server(80);

// LED 상태 관리
bool ledStates[LED_COUNT] = {false};
unsigned long ledTimers[LED_COUNT] = {0};
uint32_t ledColors[LED_COUNT] = {0};

void setup() {
  Serial.begin(115200);
  
  // NeoPixel 초기화
  strip.begin();
  strip.show(); // 모든 LED 끄기
  strip.setBrightness(BRIGHTNESS);
  
  // WiFi 연결
  WiFi.begin(ssid, password);
  Serial.print("WiFi 연결 중");
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  
  Serial.println();
  Serial.print("WiFi 연결됨! IP 주소: ");
  Serial.println(WiFi.localIP());
  
  // CORS 헤더 설정
  DefaultHeaders::Instance().addHeader("Access-Control-Allow-Origin", "*");
  DefaultHeaders::Instance().addHeader("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS");
  DefaultHeaders::Instance().addHeader("Access-Control-Allow-Headers", "Content-Type");
  
  // LED 제어 엔드포인트
  server.on("/led_control", HTTP_POST, [](AsyncWebServerRequest *request){}, NULL, 
    [](AsyncWebServerRequest *request, uint8_t *data, size_t len, size_t index, size_t total) {
      handleLEDControl(request, data, len);
    });
  
  // 상태 확인 엔드포인트
  server.on("/status", HTTP_GET, [](AsyncWebServerRequest *request){
    StaticJsonDocument<200> doc;
    doc["device"] = "ESP32 NeoPixel Controller";
    doc["ip"] = WiFi.localIP().toString();
    doc["led_count"] = LED_COUNT;
    doc["brightness"] = BRIGHTNESS;
    doc["wifi_rssi"] = WiFi.RSSI();
    
    String response;
    serializeJson(doc, response);
    request->send(200, "application/json", response);
  });
  
  // OPTIONS 요청 처리 (CORS)
  server.on("/led_control", HTTP_OPTIONS, [](AsyncWebServerRequest *request){
    request->send(200);
  });
  
  server.begin();
  Serial.println("HTTP 서버 시작됨");
}

void loop() {
  // LED 타이머 확인 및 자동 끄기
  unsigned long currentTime = millis();
  
  for (int i = 0; i < LED_COUNT; i++) {
    if (ledStates[i] && currentTime >= ledTimers[i]) {
      // 시간이 지나면 LED 끄기
      ledStates[i] = false;
      strip.setPixelColor(i, 0); // 끄기
    }
  }
  
  strip.show();
  delay(100);
}

void handleLEDControl(AsyncWebServerRequest *request, uint8_t *data, size_t len) {
  StaticJsonDocument<1024> doc;
  DeserializationError error = deserializeJson(doc, data, len);
  
  if (error) {
    StaticJsonDocument<100> errorDoc;
    errorDoc["success"] = false;
    errorDoc["error"] = "JSON 파싱 오류";
    
    String response;
    serializeJson(errorDoc, response);
    request->send(400, "application/json", response);
    return;
  }
  
  String action = doc["action"];
  
  if (action == "highlight") {
    handleHighlightAction(request, doc);
  } else if (action == "turn_off_all") {
    handleTurnOffAllAction(request);
  } else {
    StaticJsonDocument<100> errorDoc;
    errorDoc["success"] = false;
    errorDoc["error"] = "알 수 없는 액션";
    
    String response;
    serializeJson(errorDoc, response);
    request->send(400, "application/json", response);
  }
}

void handleHighlightAction(AsyncWebServerRequest *request, StaticJsonDocument<1024> &doc) {
  JsonArray ledIndices = doc["led_indices"];
  JsonObject color = doc["color"];
  int duration = doc["duration"] | 5; // 기본값 5초
  
  // RGB 색상 추출
  int r = color["r"] | 0;
  int g = color["g"] | 0;
  int b = color["b"] | 255; // 기본값 파란색
  
  uint32_t pixelColor = strip.Color(r, g, b);
  unsigned long currentTime = millis();
  unsigned long endTime = currentTime + (duration * 1000);
  
  // 지정된 LED들 켜기
  for (JsonVariant ledIndex : ledIndices) {
    int index = ledIndex.as<int>();
    
    if (index >= 0 && index < LED_COUNT) {
      ledStates[index] = true;
      ledTimers[index] = endTime;
      ledColors[index] = pixelColor;
      strip.setPixelColor(index, pixelColor);
    }
  }
  
  strip.show();
  
  // 응답 생성
  StaticJsonDocument<300> response;
  response["success"] = true;
  response["action"] = "highlight";
  response["led_count"] = ledIndices.size();
  response["duration"] = duration;
  response["color"]["r"] = r;
  response["color"]["g"] = g;
  response["color"]["b"] = b;
  
  String responseStr;
  serializeJson(response, responseStr);
  request->send(200, "application/json", responseStr);
  
  Serial.print("LED 하이라이트: ");
  Serial.print(ledIndices.size());
  Serial.print("개 LED, 색상: RGB(");
  Serial.print(r); Serial.print(",");
  Serial.print(g); Serial.print(",");
  Serial.print(b); Serial.print("), 지속시간: ");
  Serial.print(duration); Serial.println("초");
}

void handleTurnOffAllAction(AsyncWebServerRequest *request) {
  // 모든 LED 끄기
  for (int i = 0; i < LED_COUNT; i++) {
    ledStates[i] = false;
    ledTimers[i] = 0;
    ledColors[i] = 0;
    strip.setPixelColor(i, 0);
  }
  
  strip.show();
  
  StaticJsonDocument<100> response;
  response["success"] = true;
  response["action"] = "turn_off_all";
  response["message"] = "모든 LED가 꺼졌습니다";
  
  String responseStr;
  serializeJson(response, responseStr);
  request->send(200, "application/json", responseStr);
  
  Serial.println("모든 LED 끄기");
}

// 부팅 시 LED 테스트 (선택사항)
void testLEDs() {
  Serial.println("LED 테스트 시작");
  
  // 빨간색으로 순차 점등
  for (int i = 0; i < LED_COUNT; i++) {
    strip.setPixelColor(i, strip.Color(255, 0, 0));
    strip.show();
    delay(100);
  }
  
  delay(1000);
  
  // 모든 LED 끄기
  for (int i = 0; i < LED_COUNT; i++) {
    strip.setPixelColor(i, 0);
  }
  strip.show();
  
  Serial.println("LED 테스트 완료");
}
