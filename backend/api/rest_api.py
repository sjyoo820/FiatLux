"""
REST API 서버 for Next.js Frontend
FastAPI 기반의 간단한 REST API 엔드포인트를 제공
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from database import ItemDatabase
from models import Item, LEDControl
from esp32_controller import ESP32Controller

# FastAPI 앱 생성
app = FastAPI(
    title="Inventory Management API",
    description="물품 관리 시스템 REST API",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 데이터베이스 및 컨트롤러 초기화
db = ItemDatabase()
esp32 = ESP32Controller()

# 요청/응답 모델
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
    grid_position: str

class CategoryResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

# 루트 엔드포인트
@app.get("/")
async def root():
    return {"message": "Inventory Management API", "status": "running"}

# Health Check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "database": "connected"}

# 모든 물품 조회
@app.get("/items", response_model=List[Item])
async def get_all_items():
    try:
        items = db.get_all_items()
        return [Item(**item) for item in items]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 물품 검색
@app.get("/items/search", response_model=List[Item])
async def search_items(q: str):
    try:
        items = db.search_items(q)
        return [Item(**item) for item in items]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 특정 물품 조회
@app.get("/items/{item_id}", response_model=Item)
async def get_item(item_id: int):
    try:
        item = db.get_item_by_id(item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        return Item(**item)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 물품 추가
@app.post("/items", response_model=Item)
async def create_item(item: ItemCreate):
    try:
        # 새 물품 데이터 준비
        item_data = {
            'name': item.name,
            'description': item.description,
            'category': item.category,
            'grid_position': item.grid_position
        }
        
        # 데이터베이스에 추가
        item_id = db.add_item(**item_data)
        
        # 추가된 물품 반환
        new_item = db.get_item_by_id(item_id)
        return Item(**new_item)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 물품 수정
@app.put("/items/{item_id}", response_model=Item)
async def update_item(item_id: int, item: ItemUpdate):
    try:
        # 기존 물품 확인
        existing_item = db.get_item_by_id(item_id)
        if not existing_item:
            raise HTTPException(status_code=404, detail="Item not found")
        
        # 업데이트할 데이터 준비
        update_data = {}
        if item.name is not None:
            update_data['name'] = item.name
        if item.description is not None:
            update_data['description'] = item.description
        if item.category is not None:
            update_data['category'] = item.category
        if item.grid_position is not None:
            update_data['grid_position'] = item.grid_position
        
        # 데이터베이스 업데이트
        db.update_item(item_id, **update_data)
        
        # 업데이트된 물품 반환
        updated_item = db.get_item_by_id(item_id)
        return Item(**updated_item)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 물품 삭제
@app.delete("/items/{item_id}")
async def delete_item(item_id: int):
    try:
        # 기존 물품 확인
        existing_item = db.get_item_by_id(item_id)
        if not existing_item:
            raise HTTPException(status_code=404, detail="Item not found")
        
        # 데이터베이스에서 삭제
        db.delete_item(item_id)
        
        return {"message": "Item deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 카테고리 목록 조회
@app.get("/categories", response_model=List[CategoryResponse])
async def get_categories():
    try:
        categories = db.get_categories()
        return [
            CategoryResponse(
                id=idx + 1,
                name=category,
                description=f"{category} 카테고리"
            )
            for idx, category in enumerate(categories)
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# LED 하이라이트
@app.post("/highlight")
async def highlight_position(request: HighlightRequest):
    try:
        # LED 제어 객체 생성
        led_control = LEDControl(
            grid_position=request.grid_position,
            action="highlight",
            color="red",
            duration=5.0
        )
        
        # ESP32 컨트롤러로 전송
        result = await esp32.highlight_position(led_control)
        
        return {
            "message": f"Position {request.grid_position} highlighted",
            "result": result
        }
    except Exception as e:
        print(f"LED highlight error: {e}")
        # LED 실패는 치명적이지 않으므로 200 반환
        return {
            "message": f"Position {request.grid_position} highlight requested",
            "error": str(e)
        }

# 서버 실행 함수
def run_server():
    print("🚀 REST API 서버 시작...")
    print("📡 URL: http://localhost:8001")
    print("📚 API 문서: http://localhost:8001/docs")
    print("🔄 CORS 허용: localhost:3000, localhost:3001")
    
    uvicorn.run(
        "rest_api:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    run_server()
