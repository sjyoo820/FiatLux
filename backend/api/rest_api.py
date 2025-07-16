#!/usr/bin/env python3
"""
Inventory Management REST API
--------------------------------
Next.js 프론트엔드를 위해 FastAPI 로 간단한 CRUD + LED 하이라이트 엔드포인트를 제공합니다.
"""

from typing import List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import ItemDatabase
from models import Item, LEDControl
from esp32_controller import create_esp32_controller

# ────────────────────────────────
# 기본 설정
# ────────────────────────────────
app = FastAPI(
    title="Inventory Management API",
    description="물품 관리 시스템 REST API",
    version="1.0.0",
)

# CORS – 프론트엔드 포트 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 공용 인스턴스
db: ItemDatabase = ItemDatabase()
esp32 = create_esp32_controller(simulation_mode=True)

# ────────────────────────────────
# pydantic 요청 모델
# ────────────────────────────────
class ItemCreate(BaseModel):
    name: str
    description: Optional[str] = None
    category: str
    grid_position: str


class ItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    grid_position: Optional[str] = None


class HighlightRequest(BaseModel):
    """LED 하이라이트 요청 바디"""
    positions: List[str]         # ex) ["A1", "A2"]
    duration: Optional[int] = 5  # 초
    color: Optional[str] = "blue"


class CategoryResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None


# ────────────────────────────────
# 기본 & 헬스체크
# ────────────────────────────────
@app.get("/")
async def root():
    return {"message": "Inventory Management API", "status": "running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "database": "connected"}


# ────────────────────────────────
# CRUD 엔드포인트
# ────────────────────────────────
@app.get("/items", response_model=List[Item])
async def get_all_items():
    try:
        return db.get_all_items()           # 이미 Item 객체 리스트
    except Exception as e:                  # noqa: BLE001
        raise HTTPException(500, str(e))    # noqa: B904


@app.get("/items/search", response_model=List[Item])
async def search_items(q: str):
    try:
        return db.search_items(q)           # 이미 Item 객체 리스트
    except Exception as e:                  # noqa: BLE001
        raise HTTPException(500, str(e))


@app.get("/items/{item_id}", response_model=Item)
async def get_item(item_id: int):
    item = db.get_item_by_id(item_id)
    if not item:
        raise HTTPException(404, "Item not found")
    return item


@app.post("/items", response_model=Item, status_code=201)
async def create_item(item: ItemCreate):
    try:
        item_id = db.add_item(**item.model_dump())
        return db.get_item_by_id(item_id)
    except Exception as e:                  # noqa: BLE001
        raise HTTPException(500, str(e))


@app.put("/items/{item_id}", response_model=Item)
async def update_item(item_id: int, patch: ItemUpdate):
    if not db.get_item_by_id(item_id):
        raise HTTPException(404, "Item not found")

    try:
        db.update_item(item_id, **patch.model_dump(exclude_none=True))
        return db.get_item_by_id(item_id)
    except Exception as e:                  # noqa: BLE001
        raise HTTPException(500, str(e))


@app.delete("/items/{item_id}", status_code=204)
async def delete_item(item_id: int):
    if not db.get_item_by_id(item_id):
        raise HTTPException(404, "Item not found")

    db.delete_item(item_id)
    return None                             # FastAPI 204 응답


# ────────────────────────────────
# 카테고리
# ────────────────────────────────
@app.get("/categories", response_model=List[CategoryResponse])
async def get_categories():
    try:
        cats = db.get_categories()
        return [
            CategoryResponse(
                id=i + 1,
                name=c,
                description=f"{c} 카테고리",
            )
            for i, c in enumerate(cats)
        ]
    except Exception as e:                  # noqa: BLE001
        raise HTTPException(500, str(e))


# ────────────────────────────────
# LED 하이라이트
# ────────────────────────────────
@app.post("/highlight")
async def highlight_position(req: HighlightRequest):
    """
    LED 스트립에서 주어진 위치(들)를 색상으로 하이라이트합니다.
    """
    try:
        led_ctrl = LEDControl(
            positions=req.positions,
            duration=req.duration,
            color=req.color,
        )
        esp32_result = await esp32.control_leds(led_ctrl)

        return {
            "success": esp32_result.get("success", False),
            "esp32_result": esp32_result,
        }
    except Exception as e:                  # noqa: BLE001
        # LED 실패는 치명적이지 않으므로 200 OK 반환
        return {
            "success": False,
            "error": str(e),
        }


# ────────────────────────────────
# 로컬 실행
# ────────────────────────────────
def run():
    print("🚀 REST API 서버 시작 (http://localhost:8001)")
    uvicorn.run(
        "backend.api.rest_api:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info",
    )


if __name__ == "__main__":
    run()

