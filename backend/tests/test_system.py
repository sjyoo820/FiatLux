#!/usr/bin/env python3
"""
물품 관리 시스템 테스트 스크립트
MCP 서버의 기능들을 테스트합니다.
"""

import asyncio
import json
from database import ItemDatabase
from esp32_controller import create_esp32_controller
from models import LEDControl, Item

async def test_database():
    """데이터베이스 기능 테스트"""
    print("=== 데이터베이스 테스트 ===")
    
    db = ItemDatabase()
    
    # 1. 모든 물품 조회
    all_items = db.get_all_items()
    print(f"총 물품 수: {len(all_items)}")
    
    # 2. 검색 테스트
    search_results = db.search_items("노트북")
    print(f"'노트북' 검색 결과: {len(search_results)}개")
    
    for item in search_results:
        print(f"  - {item.name}: {item.grid_position}")
    
    # 3. 카테고리 조회
    categories = db.get_categories()
    print(f"카테고리: {categories}")
    
    print()

async def test_esp32_controller():
    """ESP32 컨트롤러 테스트"""
    print("=== ESP32 컨트롤러 테스트 ===")
    
    controller = create_esp32_controller(simulation_mode=True)
    
    # 1. 상태 확인
    status = await controller.get_status()
    print(f"ESP32 상태: {status['message']}")
    
    # 2. LED 제어 테스트
    led_control = LEDControl(
        positions=["A1", "A2", "B1"],
        duration=3,
        color="red"
    )
    
    result = await controller.control_leds(led_control)
    print(f"LED 제어 결과: {result['message']}")
    
    # 3. 모든 LED 끄기
    await asyncio.sleep(1)
    off_result = await controller.turn_off_all_leds()
    print(f"LED 끄기 결과: {off_result['message']}")
    
    print()

async def test_integration():
    """통합 테스트 - 물품 검색 → LED 제어"""
    print("=== 통합 테스트 ===")
    
    db = ItemDatabase()
    controller = create_esp32_controller(simulation_mode=True)
    
    # 1. 물품 검색
    items = db.search_items("키보드")
    if items:
        item = items[0]
        print(f"찾은 물품: {item.name} (위치: {item.grid_position})")
        
        # 2. 그리드 위치 파싱
        from mcp_server import parse_grid_position
        positions = parse_grid_position(item.grid_position)
        print(f"LED 위치: {positions}")
        
        # 3. LED 제어
        led_control = LEDControl(
            positions=positions,
            duration=5,
            color="blue"
        )
        
        result = await controller.control_leds(led_control)
        print(f"LED 제어: {result['message']}")
    else:
        print("물품을 찾을 수 없습니다.")
    
    print()

async def test_mcp_server_tools():
    """MCP 서버 도구 직접 테스트"""
    print("=== MCP 서버 도구 테스트 ===")
    
    # 실제 MCP 서버 기능을 직접 구현해서 테스트
    from database import ItemDatabase
    from esp32_controller import create_esp32_controller
    from models import LEDControl
    from mcp_server import parse_grid_position
    
    db = ItemDatabase()
    esp32_controller = create_esp32_controller(simulation_mode=True)
    
    # 1. 물품 검색 테스트
    search_results = db.search_items("마우스")
    print(f"검색 테스트: '마우스' 검색 결과 {len(search_results)}개")
    
    # 2. 모든 물품 조회 테스트
    all_items = db.get_all_items()
    print(f"전체 조회 테스트: 총 {len(all_items)}개 물품 조회")
    
    # 3. 카테고리 조회 테스트
    categories = db.get_categories()
    print(f"카테고리 테스트: {len(categories)}개 카테고리 조회")
    
    # 4. LED 제어 테스트
    if search_results:
        item = search_results[0]
        positions = parse_grid_position(item.grid_position)
        
        led_control = LEDControl(
            positions=positions,
            duration=3,
            color="green"
        )
        
        led_result = await esp32_controller.control_leds(led_control)
        print(f"LED 제어 테스트: {led_result['message']}")
    else:
        print("LED 제어 테스트: 마우스를 찾을 수 없어 스킵")
    
    print()

def test_grid_position_parsing():
    """그리드 위치 파싱 테스트"""
    print("=== 그리드 위치 파싱 테스트 ===")
    
    from mcp_server import parse_grid_position
    
    test_cases = [
        "A1",      # 단일 위치
        "A1-A4",   # 같은 행 범위
        "B2-B3",   # 짧은 범위
        "C1-C5",   # 긴 범위
        "D3",      # 단일 위치 (숫자)
    ]
    
    for case in test_cases:
        result = parse_grid_position(case)
        print(f"  {case} → {result}")
    
    print()

async def main():
    """모든 테스트 실행"""
    print("🧪 물품 관리 시스템 테스트 시작\n")
    
    try:
        # 1. 데이터베이스 테스트
        await test_database()
        
        # 2. 그리드 위치 파싱 테스트
        test_grid_position_parsing()
        
        # 3. ESP32 컨트롤러 테스트
        await test_esp32_controller()
        
        # 4. 통합 테스트
        await test_integration()
        
        # 5. MCP 서버 도구 테스트
        await test_mcp_server_tools()
        
        print("✅ 모든 테스트가 완료되었습니다!")
        
    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
