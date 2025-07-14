"""
ESP32 LED 제어 모듈
NeoPixel LED 스트립을 제어하여 물품 위치를 표시합니다.
"""

import json
import asyncio
import aiohttp
from typing import List, Dict, Any, Optional
from models import LEDControl

class ESP32Controller:
    """ESP32 NeoPixel LED 제어 클래스"""
    
    def __init__(self, esp32_ip: str = "192.168.1.100", port: int = 80):
        self.esp32_ip = esp32_ip
        self.port = port
        self.base_url = f"http://{esp32_ip}:{port}"
        
        # 그리드 설정 (예: 5x5 그리드)
        self.grid_rows = 5
        self.grid_cols = 5
        self.grid_mapping = self._create_grid_mapping()
    
    def _create_grid_mapping(self) -> Dict[str, int]:
        """그리드 위치를 LED 인덱스로 매핑"""
        mapping = {}
        led_index = 0
        
        for row in range(self.grid_rows):
            row_letter = chr(ord('A') + row)  # A, B, C, D, E
            for col in range(1, self.grid_cols + 1):
                position = f"{row_letter}{col}"  # A1, A2, ..., E5
                mapping[position] = led_index
                led_index += 1
        
        return mapping
    
    def position_to_led_index(self, position: str) -> Optional[int]:
        """그리드 위치를 LED 인덱스로 변환"""
        return self.grid_mapping.get(position.upper())
    
    def color_name_to_rgb(self, color_name: str) -> tuple:
        """색상 이름을 RGB 값으로 변환"""
        colors = {
            "red": (255, 0, 0),
            "green": (0, 255, 0),
            "blue": (0, 0, 255),
            "yellow": (255, 255, 0),
            "purple": (255, 0, 255),
            "cyan": (0, 255, 255),
            "white": (255, 255, 255),
            "orange": (255, 165, 0),
            "pink": (255, 192, 203),
            "off": (0, 0, 0)
        }
        return colors.get(color_name.lower(), (0, 0, 255))  # 기본값: 파란색
    
    async def control_leds(self, led_control: LEDControl) -> Dict[str, Any]:
        """LED 제어 명령을 ESP32로 전송"""
        try:
            # 위치를 LED 인덱스로 변환
            led_indices = []
            for position in led_control.positions:
                led_index = self.position_to_led_index(position)
                if led_index is not None:
                    led_indices.append(led_index)
            
            if not led_indices:
                return {
                    "success": False,
                    "error": "No valid LED positions found",
                    "message": "유효한 LED 위치를 찾을 수 없습니다."
                }
            
            # RGB 색상 변환
            rgb_color = self.color_name_to_rgb(led_control.color)
            
            # ESP32로 전송할 명령 구성
            command = {
                "action": "highlight",
                "led_indices": led_indices,
                "color": {
                    "r": rgb_color[0],
                    "g": rgb_color[1],
                    "b": rgb_color[2]
                },
                "duration": led_control.duration,
                "positions": led_control.positions
            }
            
            # ESP32로 HTTP 요청 전송
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/led_control",
                    json=command,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "success": True,
                            "data": {
                                "command": command,
                                "esp32_response": result
                            },
                            "message": f"LED 제어 완료: {len(led_indices)}개 LED가 {led_control.color} 색상으로 {led_control.duration}초간 켜집니다."
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "error": f"ESP32 응답 오류: {response.status}",
                            "message": f"ESP32에서 오류가 발생했습니다: {error_text}"
                        }
        
        except aiohttp.ClientTimeout:
            return {
                "success": False,
                "error": "Timeout",
                "message": "ESP32 연결 시간 초과"
            }
        except aiohttp.ClientError as e:
            return {
                "success": False,
                "error": f"Connection error: {str(e)}",
                "message": f"ESP32 연결 오류: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "message": f"예상치 못한 오류: {str(e)}"
            }
    
    async def turn_off_all_leds(self) -> Dict[str, Any]:
        """모든 LED 끄기"""
        try:
            command = {"action": "turn_off_all"}
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/led_control",
                    json=command,
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    if response.status == 200:
                        return {
                            "success": True,
                            "message": "모든 LED가 꺼졌습니다."
                        }
                    else:
                        return {
                            "success": False,
                            "message": "LED 끄기 실패"
                        }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"LED 제어 오류: {str(e)}"
            }
    
    async def get_status(self) -> Dict[str, Any]:
        """ESP32 상태 확인"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/status",
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    if response.status == 200:
                        status = await response.json()
                        return {
                            "success": True,
                            "data": status,
                            "message": "ESP32 연결 정상"
                        }
                    else:
                        return {
                            "success": False,
                            "message": "ESP32 상태 확인 실패"
                        }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"ESP32 연결 실패: {str(e)}"
            }

# 시뮬레이션용 가상 ESP32 컨트롤러
class MockESP32Controller(ESP32Controller):
    """개발/테스트용 가상 ESP32 컨트롤러"""
    
    def __init__(self):
        super().__init__("127.0.0.1", 8080)
        self.led_states = {}  # LED 상태 저장
    
    async def control_leds(self, led_control: LEDControl) -> Dict[str, Any]:
        """가상 LED 제어 (시뮬레이션)"""
        try:
            # 위치를 LED 인덱스로 변환
            led_indices = []
            for position in led_control.positions:
                led_index = self.position_to_led_index(position)
                if led_index is not None:
                    led_indices.append(led_index)
                    # 가상 LED 상태 저장
                    self.led_states[led_index] = {
                        "position": position,
                        "color": led_control.color,
                        "duration": led_control.duration
                    }
            
            if not led_indices:
                return {
                    "success": False,
                    "error": "No valid LED positions found",
                    "message": "유효한 LED 위치를 찾을 수 없습니다."
                }
            
            # 시뮬레이션 지연
            await asyncio.sleep(0.5)
            
            return {
                "success": True,
                "data": {
                    "led_indices": led_indices,
                    "positions": led_control.positions,
                    "color": led_control.color,
                    "duration": led_control.duration,
                    "simulation": True
                },
                "message": f"[시뮬레이션] LED 제어 완료: {len(led_indices)}개 LED가 {led_control.color} 색상으로 {led_control.duration}초간 켜집니다."
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"시뮬레이션 오류: {str(e)}"
            }
    
    async def turn_off_all_leds(self) -> Dict[str, Any]:
        """모든 가상 LED 끄기"""
        self.led_states.clear()
        await asyncio.sleep(0.1)
        
        return {
            "success": True,
            "message": "[시뮬레이션] 모든 LED가 꺼졌습니다."
        }
    
    async def get_status(self) -> Dict[str, Any]:
        """가상 ESP32 상태"""
        return {
            "success": True,
            "data": {
                "device": "Mock ESP32",
                "ip": "127.0.0.1",
                "led_count": self.grid_rows * self.grid_cols,
                "active_leds": len(self.led_states),
                "grid_size": f"{self.grid_rows}x{self.grid_cols}",
                "simulation": True
            },
            "message": "[시뮬레이션] ESP32 연결 정상"
        }

# 컨트롤러 팩토리
def create_esp32_controller(simulation_mode: bool = True) -> ESP32Controller:
    """ESP32 컨트롤러 생성"""
    if simulation_mode:
        return MockESP32Controller()
    else:
        # 실제 ESP32 IP 주소로 변경 필요
        return ESP32Controller("192.168.1.100")

if __name__ == "__main__":
    # 테스트 코드
    async def test_led_control():
        controller = create_esp32_controller(simulation_mode=True)
        
        # 상태 확인
        status = await controller.get_status()
        print("ESP32 상태:", status)
        
        # LED 제어 테스트
        led_control = LEDControl(
            positions=["A1", "A2", "B1"],
            duration=5,
            color="blue"
        )
        
        result = await controller.control_leds(led_control)
        print("LED 제어 결과:", result)
        
        # 모든 LED 끄기
        await asyncio.sleep(2)
        off_result = await controller.turn_off_all_leds()
        print("LED 끄기 결과:", off_result)
    
    # 테스트 실행
    asyncio.run(test_led_control())
