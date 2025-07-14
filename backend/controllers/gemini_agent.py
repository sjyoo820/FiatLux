"""
Gemini Flash 2.5 LLM을 사용한 고급 물품 관리 에이전트
"""

import os
import json
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import google.generativeai as genai
from dotenv import load_dotenv

from database import ItemDatabase
from esp32_controller import create_esp32_controller
from models import LEDControl, Item
from mcp_server import parse_grid_position

# 환경 변수 로드
load_dotenv()

class GeminiItemAgent:
    """Gemini Flash 2.5를 사용한 스마트 물품 관리 에이전트"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.db = ItemDatabase()
        self.esp32_controller = create_esp32_controller(simulation_mode=True)
        
        # Gemini 설정
        api_key = api_key or os.getenv("GOOGLE_AI_API_KEY")
        if not api_key or api_key == "your_google_ai_api_key_here":
            print("⚠️ Google AI API 키가 설정되지 않았습니다. 기본 규칙 기반 모드로 동작합니다.")
            self.use_llm = False
        else:
            try:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
                self.use_llm = True
                print("✅ Gemini Flash 2.5 연결 성공!")
            except Exception as e:
                print(f"⚠️ Gemini 연결 실패: {str(e)}. 기본 모드로 동작합니다.")
                self.use_llm = False
        
        # 시스템 프롬프트
        self.system_prompt = """
당신은 물품 관리 시스템의 AI 어시스턴트입니다. 사용자의 자연어 질문을 분석하여 적절한 작업을 수행해야 합니다.

사용 가능한 기능:
1. 물품 검색 (search_items): 키워드로 물품 찾기
2. 전체 물품 조회 (get_all_items): 모든 물품 목록 보기
3. 카테고리 조회 (get_categories): 물품 카테고리 목록 보기
4. LED 위치 표시 (highlight_led): 특정 물품의 위치를 LED로 표시

응답 형식:
{
    "intent": "search_items|get_all_items|get_categories|highlight_led",
    "parameters": {
        "query": "검색 키워드 (search_items용)",
        "item_name": "물품명 (highlight_led용)",
        "category": "카테고리 (선택사항)"
    },
    "user_message": "사용자에게 보여줄 친근한 응답 메시지"
}

사용자 질문 예시와 응답:
- "노트북 어디 있어?" → intent: "search_items", parameters: {"query": "노트북"}
- "모든 물품 보여줘" → intent: "get_all_items"
- "카테고리 알려줘" → intent: "get_categories"
- "마우스 위치 LED로 표시해줘" → intent: "highlight_led", parameters: {"item_name": "마우스"}

항상 JSON 형식으로만 응답하세요.
"""
    
    async def process_query(self, user_input: str) -> Dict[str, Any]:
        """사용자 입력을 처리하고 적절한 동작을 수행합니다."""
        if self.use_llm:
            return await self._process_with_llm(user_input)
        else:
            return await self._process_with_rules(user_input)
    
    async def _process_with_llm(self, user_input: str) -> Dict[str, Any]:
        """Gemini LLM을 사용한 고급 처리"""
        try:
            # 현재 물품 목록을 컨텍스트로 제공
            items = self.db.get_all_items()
            categories = self.db.get_categories()
            
            context = f"""
현재 시스템에 등록된 물품들:
{json.dumps([item.model_dump() for item in items], ensure_ascii=False, indent=2)}

카테고리: {categories}

사용자 질문: {user_input}
"""
            
            # Gemini에게 질의
            response = await asyncio.get_event_loop().run_in_executor(
                None, 
                lambda: self.model.generate_content(self.system_prompt + "\n\n" + context)
            )
            
            # JSON 응답 파싱
            try:
                result_text = response.text.strip()
                # JSON 블록에서 추출
                if "```json" in result_text:
                    result_text = result_text.split("```json")[1].split("```")[0].strip()
                elif "```" in result_text:
                    result_text = result_text.split("```")[1].strip()
                
                llm_result = json.loads(result_text)
                
                # LLM 결과에 따라 적절한 동작 수행
                intent = llm_result.get("intent")
                parameters = llm_result.get("parameters", {})
                user_message = llm_result.get("user_message", "처리 중입니다...")
                
                if intent == "search_items":
                    query = parameters.get("query", user_input)
                    result = self._handle_search_query(query)
                elif intent == "get_all_items":
                    result = self._handle_get_all_items()
                elif intent == "get_categories":
                    result = self._handle_get_categories()
                elif intent == "highlight_led":
                    item_name = parameters.get("item_name", user_input)
                    result = await self._handle_led_query(item_name)
                else:
                    # 기본 검색
                    result = self._handle_search_query(user_input)
                
                # LLM의 친근한 메시지 추가
                if result.get("success"):
                    result["llm_message"] = user_message
                
                return result
                
            except json.JSONDecodeError as e:
                print(f"LLM JSON 파싱 오류: {e}")
                print(f"응답 텍스트: {response.text}")
                # 백업: 규칙 기반 처리
                return await self._process_with_rules(user_input)
                
        except Exception as e:
            print(f"LLM 처리 오류: {e}")
            # 백업: 규칙 기반 처리
            return await self._process_with_rules(user_input)
    
    async def _process_with_rules(self, user_input: str) -> Dict[str, Any]:
        """규칙 기반 기본 처리 (LLM 백업용)"""
        user_input_lower = user_input.lower()
        
        # 간단한 의도 분류
        if any(keyword in user_input_lower for keyword in ["찾아", "검색", "어디", "위치"]):
            return self._handle_search_query(user_input)
        elif any(keyword in user_input_lower for keyword in ["모든", "전체", "목록", "리스트"]):
            return self._handle_get_all_items()
        elif any(keyword in user_input_lower for keyword in ["카테고리", "분류", "종류"]):
            return self._handle_get_categories()
        elif "켜" in user_input_lower or "led" in user_input_lower or "표시" in user_input_lower:
            return await self._handle_led_query(user_input)
        else:
            return self._handle_search_query(user_input)
    
    def _handle_search_query(self, user_input: str) -> Dict[str, Any]:
        """검색 쿼리를 처리합니다."""
        # 간단한 키워드 추출
        keywords = []
        for word in user_input.split():
            if len(word) > 1 and word not in ["어디", "있나", "찾아", "검색", "해줘", "위치"]:
                keywords.append(word)
        
        if keywords:
            query = " ".join(keywords)
        else:
            query = user_input
        
        try:
            items = self.db.search_items(query)
            return {
                "success": True,
                "data": {
                    "items": [item.model_dump() for item in items],
                    "total_count": len(items),
                    "query": query
                },
                "message": f"'{query}' 검색 결과: {len(items)}개 물품을 찾았습니다.",
                "processing_mode": "LLM" if self.use_llm else "규칙 기반"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "물품 검색 중 오류가 발생했습니다."
            }
    
    def _handle_get_all_items(self) -> Dict[str, Any]:
        """모든 물품을 조회합니다."""
        try:
            items = self.db.get_all_items()
            return {
                "success": True,
                "data": {
                    "items": [item.model_dump() for item in items],
                    "total_count": len(items)
                },
                "message": f"총 {len(items)}개의 물품을 조회했습니다.",
                "processing_mode": "LLM" if self.use_llm else "규칙 기반"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "물품 목록 조회 중 오류가 발생했습니다."
            }
    
    def _handle_get_categories(self) -> Dict[str, Any]:
        """카테고리를 조회합니다."""
        try:
            categories = self.db.get_categories()
            return {
                "success": True,
                "data": {
                    "categories": categories,
                    "count": len(categories)
                },
                "message": f"총 {len(categories)}개의 카테고리를 조회했습니다.",
                "processing_mode": "LLM" if self.use_llm else "규칙 기반"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "카테고리 조회 중 오류가 발생했습니다."
            }
    
    async def _handle_led_query(self, user_input: str) -> Dict[str, Any]:
        """LED 제어 쿼리를 처리합니다."""
        # 물품명 추출하여 검색 후 LED 제어
        search_result = self._handle_search_query(user_input)
        
        if search_result.get("success") and search_result.get("data", {}).get("items"):
            items = search_result["data"]["items"]
            if items:
                first_item = items[0]
                item_id = first_item["id"]
                
                led_result = await self.highlight_item_location(item_id, 10, "blue")
                return led_result
        
        return {
            "success": False,
            "message": "LED로 표시할 물품을 찾을 수 없습니다."
        }
    
    async def highlight_item_location(self, item_id: int, duration: int = 5, color: str = "blue") -> Dict[str, Any]:
        """특정 물품의 위치를 LED로 강조 표시합니다."""
        try:
            item = self.db.get_item_by_id(item_id)
            
            if not item:
                return {
                    "success": False,
                    "error": "Item not found",
                    "message": f"ID {item_id}에 해당하는 물품을 찾을 수 없습니다."
                }
            
            # 그리드 위치 파싱
            positions = parse_grid_position(item.grid_position)
            
            led_control = LEDControl(
                positions=positions,
                duration=duration,
                color=color
            )
            
            # ESP32 LED 제어 실행
            esp32_result = await self.esp32_controller.control_leds(led_control)
            
            return {
                "success": esp32_result.get("success", False),
                "data": {
                    "item": item.model_dump(),
                    "led_control": led_control.model_dump(),
                    "positions": positions,
                    "esp32_result": esp32_result.get("data", {})
                },
                "message": esp32_result.get("message", f"물품 '{item.name}'의 위치({item.grid_position}) LED 제어를 시도했습니다."),
                "esp32_status": esp32_result,
                "processing_mode": "LLM" if self.use_llm else "규칙 기반"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "LED 제어 중 오류가 발생했습니다."
            }
    
    async def chat_with_gemini(self, user_input: str, context: str = "") -> str:
        """일반적인 채팅을 위한 Gemini 호출"""
        if not self.use_llm:
            return "죄송합니다. LLM 기능이 비활성화되어 있습니다."
        
        try:
            prompt = f"""
당신은 물품 관리 시스템의 친근한 AI 어시스턴트입니다.
사용자의 질문에 도움이 되고 친근한 방식으로 답변해주세요.

{context}

사용자: {user_input}
어시스턴트:"""
            
            response = await asyncio.get_event_loop().run_in_executor(
                None, 
                lambda: self.model.generate_content(prompt)
            )
            
            return response.text
        except Exception as e:
            return f"답변 생성 중 오류가 발생했습니다: {str(e)}"

# 하위 호환성을 위한 별칭
ItemAgent = GeminiItemAgent
