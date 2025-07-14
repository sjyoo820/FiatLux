from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class Item(BaseModel):
    """물품 정보 모델"""
    id: Optional[int] = None
    name: str
    description: str
    grid_position: str  # 예: "A1-A4" 또는 "B2"
    category: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class ItemSearch(BaseModel):
    """물품 검색 요청 모델"""
    query: str
    category: Optional[str] = None

class ItemResponse(BaseModel):
    """물품 검색 응답 모델"""
    items: List[Item]
    total_count: int

class LEDControl(BaseModel):
    """LED 제어 모델"""
    positions: List[str]  # 켤 LED 위치들
    duration: Optional[int] = 5  # 켜둘 시간(초)
    color: Optional[str] = "blue"  # LED 색상
