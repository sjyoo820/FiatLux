import sqlite3
import os
from datetime import datetime
from typing import List, Optional, Dict
from models import Item

class ItemDatabase:
    def __init__(self, db_path: str = "items.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """데이터베이스 초기화 및 테이블 생성"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                grid_position TEXT NOT NULL,
                category TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 샘플 데이터 추가 (테이블이 비어있을 때만)
        cursor.execute("SELECT COUNT(*) FROM items")
        if cursor.fetchone()[0] == 0:
            sample_items = [
                ("노트북", "MacBook Pro 16인치", "A1-A2", "전자기기"),
                ("마우스", "로지텍 무선 마우스", "A3", "전자기기"),
                ("키보드", "기계식 키보드", "B1-B3", "전자기기"),
                ("펜", "볼펜 (검은색)", "C1", "문구류"),
                ("노트", "A4 노트", "C2-C3", "문구류"),
                ("USB 케이블", "USB-C 케이블", "D1", "전자기기"),
                ("헤드폰", "노이즈 캔슬링 헤드폰", "D2-D4", "전자기기"),
                ("스마트폰", "iPhone 15 Pro", "E1", "전자기기"),
                ("충전기", "스마트폰 충전기", "E2", "전자기기"),
                ("책", "파이썬 프로그래밍", "F1-F2", "도서")
            ]
            
            cursor.executemany(
                "INSERT INTO items (name, description, grid_position, category) VALUES (?, ?, ?, ?)",
                sample_items
            )
        
        conn.commit()
        conn.close()
    
    def search_items(self, query: str, category: Optional[str] = None) -> List[Item]:
        """물품 검색"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        sql = """
            SELECT id, name, description, grid_position, category, created_at, updated_at
            FROM items
            WHERE (name LIKE ? OR description LIKE ?)
        """
        params = [f"%{query}%", f"%{query}%"]
        
        if category:
            sql += " AND category = ?"
            params.append(category)
        
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        conn.close()
        
        items: List[Item] = []
        for row in rows:
            items.append(
                Item(
                    id=row[0],
                    name=row[1],
                    description=row[2],
                    grid_position=row[3],
                    category=row[4],
                    created_at=row[5],
                    updated_at=row[6]
                )
            )
        
        return items
    
    def get_item_by_id(self, item_id: int) -> Optional[Dict]:
        """특정 ID의 물품 조회"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM items WHERE id = ?", (item_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'name': row[1],
                'description': row[2],
                'category': row[3],
                'grid_position': row[4]
            }
        return None
    
    def add_item(self, name: str, description: Optional[str], category: str, grid_position: str) -> int:
        """새 물품 추가"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO items (name, description, category, grid_position) VALUES (?, ?, ?, ?)",
            (name, description, category, grid_position)
        )
        
        item_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return item_id
    
    def update_item(self, item_id: int, **kwargs) -> bool:
        """물품 정보 수정"""
        if not kwargs:
            return False
            
        # SET 절 구성
        set_clauses = []
        values = []
        
        for key, value in kwargs.items():
            if key in ['name', 'description', 'category', 'grid_position']:
                set_clauses.append(f"{key} = ?")
                values.append(value)
        
        if not set_clauses:
            return False
        
        query = f"UPDATE items SET {', '.join(set_clauses)} WHERE id = ?"
        values.append(item_id)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(query, values)
        conn.commit()
        conn.close()
        
        return cursor.rowcount > 0
    
    def delete_item(self, item_id: int) -> bool:
        """물품 삭제"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM items WHERE id = ?", (item_id,))
        conn.commit()
        conn.close()
        
        return cursor.rowcount > 0
    
    def get_all_items(self) -> List[Item]:
        """모든 물품 조회"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, description, grid_position, category, created_at, updated_at
            FROM items ORDER BY name
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        items: List[Item] = []
        for row in rows:
            items.append(
                Item(
                    id=row[0],
                    name=row[1],
                    description=row[2],
                    grid_position=row[3],
                    category=row[4],
                    created_at=row[5],
                    updated_at=row[6]
                )
            )
        
        return items
    
    def get_categories(self) -> List[str]:
        """모든 카테고리 조회"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT DISTINCT category FROM items WHERE category IS NOT NULL")
        rows = cursor.fetchall()
        conn.close()
        
        return [row[0] for row in rows]

if __name__ == "__main__":
    # 데이터베이스 초기화 테스트
    db = ItemDatabase()
    print("데이터베이스가 초기화되었습니다.")
    
    # 샘플 검색 테스트
    items = db.search_items("노트북")
    print(f"'노트북' 검색 결과: {len(items)}개")
    
    for item in items:
        print(f"- {item.name}: {item.grid_position}")
