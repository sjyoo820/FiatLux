# 물품 관리 시스템 v2.0

이 프로젝트는 DB에 저장된 물품 정보를 조회하고 LED로 위치를 표시하는 물품 관리 시스템입니다.

🤖 **Gemini Flash 2.5 LLM 연동**으로 더욱 정교한 자연어 처리를 지원합니다!

## 구성 요소

- `mcp_server.py`: FastMCP 기반 서버 (물품 조회 기능)
- `streamlit_client.py`: Streamlit 기반 웹 클라이언트
- `gemini_agent.py`: 🤖 Gemini Flash 2.5 LLM 에이전트
- `database.py`: SQLite 데이터베이스 관리
- `models.py`: 데이터 모델 정의
- `esp32_controller.py`: ESP32 LED 제어
- `esp32_neopixel_server.ino`: ESP32 아두이노 코드

## 새로운 기능 (v2.0)

- 🤖 **Gemini Flash 2.5 LLM 연동**: 자연스러운 대화형 인터페이스
- 🧠 **고급 의도 분석**: 복잡한 문장도 정확하게 이해
- 💬 **문맥 이해**: "책상 위에 있는 노트북 찾아줘" 같은 자연스러운 질문
- 🎯 **스마트 검색**: 유사 단어 및 관련 용어 자동 매칭
- 🔄 **백업 모드**: API 키 없이도 기본 기능 사용 가능

## 설치 및 실행

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. 환경 설정

`.env` 파일에 Google AI API 키를 설정하세요:

```bash
GOOGLE_AI_API_KEY=your_actual_api_key_here
```

API 키 발급: [Google AI Studio](https://aistudio.google.com/app/apikey)

### 3. 데이터베이스 초기화

```bash
python database.py
```

### 4. 시스템 테스트

```bash
# 기본 시스템 테스트
python test_system.py

# Gemini 연동 테스트
python test_gemini.py
```

### 5. 실행

```bash
# 자동 실행 (권장)
./start_system.sh

# 또는 수동 실행
streamlit run streamlit_client.py
```

## 사용법

### 🤖 Gemini LLM 모드 (API 키 설정 시)

**자연어 질문 예시:**
- "책상 위에 있는 노트북 찾아줘"
- "전자기기 중에서 충전 가능한 것들 보여줘"
- "빨간색 펜이 어디에 있는지 LED로 표시해줘"
- "A1부터 A3 구역에 있는 물품들 알려줘"
- "무선 마우스의 정확한 위치를 알고 싶어"

### ⚡ 기본 모드 (API 키 미설정 시)

**간단한 질문 예시:**
- "노트북 어디 있어?"
- "전자기기 목록 보여줘"
- "마우스 위치 LED로 표시해줘"
- "모든 물품 보여줘"
- "카테고리 알려줘"

## 기능

- 🔍 **스마트 물품 검색**: 자연어로 물품 찾기
- 💡 **LED 위치 표시**: ESP32 NeoPixel로 시각적 위치 안내
- 📊 **실시간 통계**: 물품 수, 카테고리 현황
- 🏷️ **카테고리 필터링**: 전자기기, 문구류, 도서 등
- 🤖 **AI 챗봇**: Gemini LLM 기반 대화형 인터페이스
- 📱 **웹 인터페이스**: 반응형 웹 UI (http://localhost:8501)

## ESP32 하드웨어 연동

### 필요 부품
- ESP32 개발 보드
- WS2812B NeoPixel LED 스트립 (25개, 5x5 그리드)
- 점퍼 와이어, 브레드보드

### 아두이노 설정
1. `esp32_neopixel_server.ino` 파일을 아두이노 IDE로 열기
2. WiFi SSID/Password 설정
3. LED 핀 번호 확인 (기본: GPIO 2)
4. ESP32에 업로드

### 실제 하드웨어 연결
`esp32_controller.py`에서 시뮬레이션 모드를 비활성화:
```python
esp32_controller = create_esp32_controller(simulation_mode=False)
```
