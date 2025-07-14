#!/usr/bin/env python3
"""
물품 관리 시스템 MCP 서버
FastMCP를 사용하여 물품 조회 기능을 제공합니다.
"""

import json
from typing import List, Optional, Dict, Any
from fastmcp import FastMCP
from pydantic import BaseModel
from database import ItemDatabase
from models import Item, ItemSearch, ItemResponse, LEDControl
from esp32_controller import create_esp32_controller

# MCP 서버 초기화
mcp = FastMCP("Item Management System")

# 데이터베이스 인스턴스
db = ItemDatabase()

# ESP32 컨트롤러 인스턴스 (시뮬레이션 모드)
esp32_controller = create_esp32_controller(simulation_mode=True)

class SearchItemsArgs(BaseModel):
    """물품 검색 도구 인자"""
    query: str
    category: Optional[str] = None

class GetItemByIdArgs(BaseModel):
    """ID로 물품 조회 도구 인자"""
    item_id: int

class GetAllItemsArgs(BaseModel):
    """모든 물품 조회 도구 인자"""
    pass

class GetCategoriesArgs(BaseModel):
    """카테고리 조회 도구 인자"""
    pass

class HighlightItemLocationArgs(BaseModel):
    """물품 위치 강조 도구 인자"""
    item_id: int
    duration: Optional[int] = 5
    color: Optional[str] = "blue"

@mcp.tool()
def search_items(args: SearchItemsArgs) -> Dict[str, Any]:
    """
    물품을 이름이나 설명으로 검색합니다.
    
    Args:
        query: 검색할 물품명 또는 설명 키워드
        category: 필터링할 카테고리 (선택사항)
    
    Returns:
        검색된 물품 목록과 총 개수
    """
    try:
        items = db.search_items(args.query, args.category)
        
        result = {
            "items": [item.model_dump() for item in items],
            "total_count": len(items),
            "query": args.query,
            "category": args.category
        }
        
        return {
            "success": True,
            "data": result,
            "message": f"'{args.query}' 검색 결과: {len(items)}개 물품을 찾았습니다."
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "물품 검색 중 오류가 발생했습니다."
        }

@mcp.tool()
def get_item_by_id(args: GetItemByIdArgs) -> Dict[str, Any]:
    """
    ID로 특정 물품의 상세 정보를 조회합니다.
    
    Args:
        item_id: 조회할 물품의 ID
    
    Returns:
        물품 상세 정보
    """
    try:
        item = db.get_item_by_id(args.item_id)
        
        if item:
            return {
                "success": True,
                "data": item.model_dump(),
                "message": f"물품 '{item.name}'의 정보를 조회했습니다."
            }
        else:
            return {
                "success": False,
                "error": "Item not found",
                "message": f"ID {args.item_id}에 해당하는 물품을 찾을 수 없습니다."
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "물품 조회 중 오류가 발생했습니다."
        }

@mcp.tool()
def get_all_items(args: GetAllItemsArgs) -> Dict[str, Any]:
    """
    모든 물품의 목록을 조회합니다.
    
    Returns:
        전체 물품 목록
    """
    try:
        items = db.get_all_items()
        
        return {
            "success": True,
            "data": {
                "items": [item.model_dump() for item in items],
                "total_count": len(items)
            },
            "message": f"총 {len(items)}개의 물품을 조회했습니다."
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "물품 목록 조회 중 오류가 발생했습니다."
        }

@mcp.tool()
def get_categories(args: GetCategoriesArgs) -> Dict[str, Any]:
    """
    모든 물품 카테고리 목록을 조회합니다.
    
    Returns:
        카테고리 목록
    """
    try:
        categories = db.get_categories()
        
        return {
            "success": True,
            "data": {
                "categories": categories,
                "count": len(categories)
            },
            "message": f"총 {len(categories)}개의 카테고리를 조회했습니다."
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "카테고리 조회 중 오류가 발생했습니다."
        }

@mcp.tool()
async def highlight_item_location(args: HighlightItemLocationArgs) -> Dict[str, Any]:
    """
    특정 물품의 위치를 LED로 강조 표시합니다.
    
    Args:
        item_id: 강조할 물품의 ID
        duration: LED를 켜둘 시간(초, 기본값: 5)
        color: LED 색상 (기본값: "blue")
    
    Returns:
        LED 제어 결과
    """
    try:
        item = db.get_item_by_id(args.item_id)
        
        if not item:
            return {
                "success": False,
                "error": "Item not found",
                "message": f"ID {args.item_id}에 해당하는 물품을 찾을 수 없습니다."
            }
        
        # 그리드 위치 파싱 (예: "A1-A4" -> ["A1", "A2", "A3", "A4"])
        positions = parse_grid_position(item.grid_position)
        
        led_control = LEDControl(
            positions=positions,
            duration=args.duration,
            color=args.color
        )
        
        # ESP32 LED 제어 실행
        esp32_result = await esp32_controller.control_leds(led_control)
        
        return {
            "success": esp32_result.get("success", False),
            "data": {
                "item": item.model_dump(),
                "led_control": led_control.model_dump(),
                "positions": positions,
                "esp32_result": esp32_result.get("data", {})
            },
            "message": esp32_result.get("message", f"물품 '{item.name}'의 위치({item.grid_position}) LED 제어를 시도했습니다."),
            "esp32_status": esp32_result
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "LED 제어 중 오류가 발생했습니다."
        }

def parse_grid_position(grid_position: str) -> List[str]:
    """
    그리드 위치 문자열을 개별 위치 리스트로 파싱합니다.
    
    예시:
    - "A1" -> ["A1"]
    - "A1-A4" -> ["A1", "A2", "A3", "A4"]
    - "B2-B3" -> ["B2", "B3"]
    """
    if "-" not in grid_position:
        return [grid_position]
    
    start_pos, end_pos = grid_position.split("-")
    
    # 문자와 숫자 분리
    start_letter = start_pos[0]
    start_number = int(start_pos[1:])
    end_letter = end_pos[0]
    end_number = int(end_pos[1:])
    
    positions = []
    
    if start_letter == end_letter:
        # 같은 행에서 범위
        for i in range(start_number, end_number + 1):
            positions.append(f"{start_letter}{i}")
    else:
        # 다른 행으로 확장 (복잡한 경우는 단순화)
        positions = [start_pos, end_pos]
    
    return positions

if __name__ == "__main__":
    # MCP 서버 실행
    print("물품 관리 시스템 MCP 서버를 시작합니다...")
    print("사용 가능한 도구:")
    print("- search_items: 물품 검색")
    print("- get_item_by_id: ID로 물품 조회")
    print("- get_all_items: 모든 물품 조회")
    print("- get_categories: 카테고리 조회")
    print("- highlight_item_location: 물품 위치 LED 강조")
    
    # FastMCP 서버 실행 (기본 STDIO 모드)
    mcp.run()
