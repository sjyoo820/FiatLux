import streamlit as st
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime

# 직접 import
from database import ItemDatabase
from esp32_controller import create_esp32_controller
from models import LEDControl, Item
from mcp_server import parse_grid_position

# Gemini 에이전트 import (기본 에이전트의 백업)
try:
    from gemini_agent import GeminiItemAgent as ItemAgent
    GEMINI_AVAILABLE = True
except ImportError:
    print("⚠️ Gemini 라이브러리가 없습니다. 기본 에이전트를 사용합니다.")
    GEMINI_AVAILABLE = False
    
    # 기본 에이전트 정의 (백업용)
    class ItemAgent:
        def __init__(self):
            self.db = ItemDatabase()
            self.esp32_controller = create_esp32_controller(simulation_mode=True)
        
        async def process_query(self, user_input: str) -> Dict[str, Any]:
            """사용자 입력을 처리하고 적절한 동작을 수행합니다."""
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
            keywords = []
            for word in user_input.split():
                if len(word) > 1 and word not in ["어디", "있나", "찾아", "검색", "해줘"]:
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
                    "processing_mode": "기본 모드"
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
                    "processing_mode": "기본 모드"
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
                    "processing_mode": "기본 모드"
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "message": "카테고리 조회 중 오류가 발생했습니다."
                }
        
        async def _handle_led_query(self, user_input: str) -> Dict[str, Any]:
            """LED 제어 쿼리를 처리합니다."""
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
                
                positions = parse_grid_position(item.grid_position)
                
                led_control = LEDControl(
                    positions=positions,
                    duration=duration,
                    color=color
                )
                
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
                    "processing_mode": "기본 모드"
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "message": "LED 제어 중 오류가 발생했습니다."
                }

# Streamlit 앱 설정
st.set_page_config(
    page_title="물품 관리 시스템",
    page_icon="📦",
    layout="wide"
)

# 세션 상태 초기화
if "agent" not in st.session_state:
    st.session_state.agent = ItemAgent()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# 메인 UI
st.title("📦 물품 관리 시스템")
if GEMINI_AVAILABLE:
    st.markdown("🤖 **Gemini Flash 2.5 LLM 연동** - 고급 자연어 처리 지원")
else:
    st.markdown("⚡ **기본 모드** - 규칙 기반 처리")

st.markdown("LLM 에이전트를 통한 스마트 물품 조회 및 위치 표시")

# 사이드바 - 서버 상태 및 설정
with st.sidebar:
    st.header("⚙️ 설정")
    
    # Gemini API 키 설정
    if GEMINI_AVAILABLE:
        st.subheader("🤖 Gemini LLM 설정")
        
        # API 키 입력
        api_key = st.text_input(
            "Google AI API Key", 
            type="password",
            help="Google AI Studio에서 발급받은 API 키를 입력하세요"
        )
        
        if api_key and st.button("🔄 LLM 연결 업데이트"):
            try:
                # 새로운 에이전트 생성
                from gemini_agent import GeminiItemAgent
                new_agent = GeminiItemAgent(api_key=api_key)
                st.session_state.agent = new_agent
                st.success("✅ Gemini LLM 연결이 업데이트되었습니다!")
                st.experimental_rerun()
            except Exception as e:
                st.error(f"❌ LLM 연결 실패: {str(e)}")
        
        # 현재 LLM 상태 표시
        if hasattr(st.session_state.agent, 'use_llm'):
            if st.session_state.agent.use_llm:
                st.success("✅ Gemini LLM 활성화")
            else:
                st.warning("⚠️ 기본 모드 (API 키 필요)")
    else:
        st.warning("⚠️ Gemini 라이브러리 미설치")
        if st.button("📦 라이브러리 설치 안내"):
            st.code("pip install google-generativeai python-dotenv")
    
    st.markdown("---")
    
    # 시스템 상태 확인
    if st.button("🔗 시스템 상태 확인"):
        with st.spinner("시스템 상태 확인 중..."):
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                # 데이터베이스 상태 확인
                result = loop.run_until_complete(
                    st.session_state.agent.esp32_controller.get_status()
                )
                loop.close()
                
                if result.get("success"):
                    st.success("✅ 시스템 연결 정상!")
                    st.json(result.get("data", {}))
                else:
                    st.error(f"❌ 시스템 연결 실패: {result.get('message', '알 수 없는 오류')}")
            except Exception as e:
                st.error(f"❌ 연결 오류: {str(e)}")
    
    st.markdown("---")
    
    # 빠른 작업 버튼들
    st.header("🚀 빠른 작업")
    
    if st.button("📋 모든 물품 보기"):
        with st.spinner("물품 목록 조회 중..."):
            try:
                result = st.session_state.agent._handle_get_all_items()
                
                st.session_state.chat_history.append({
                    "type": "system",
                    "message": "모든 물품 조회",
                    "result": result,
                    "timestamp": datetime.now()
                })
                st.experimental_rerun()
            except Exception as e:
                st.error(f"오류: {str(e)}")
    
    if st.button("🏷️ 카테고리 보기"):
        with st.spinner("카테고리 조회 중..."):
            try:
                result = st.session_state.agent._handle_get_categories()
                
                st.session_state.chat_history.append({
                    "type": "system",
                    "message": "카테고리 조회",
                    "result": result,
                    "timestamp": datetime.now()
                })
                st.experimental_rerun()
            except Exception as e:
                st.error(f"오류: {str(e)}")

# 메인 컨텐츠 영역
col1, col2 = st.columns([2, 1])

with col1:
    st.header("💬 AI 챗봇")
    
    # 채팅 인터페이스
    chat_container = st.container()
    
    with chat_container:
        # 채팅 히스토리 표시
        for chat in st.session_state.chat_history:
            with st.chat_message("user" if chat["type"] == "user" else "assistant"):
                st.write(f"**[{chat['timestamp'].strftime('%H:%M:%S')}]** {chat['message']}")
                
                if "result" in chat:
                    result = chat["result"]
                    if result.get("success"):
                        if "data" in result:
                            data = result["data"]
                            
                            # 물품 목록 표시
                            if "items" in data:
                                items = data["items"]
                                if items:
                                    st.write(f"📦 **{len(items)}개 물품 발견:**")
                                    for item in items:
                                        with st.expander(f"{item['name']} - 위치: {item['grid_position']}"):
                                            st.write(f"**설명:** {item['description']}")
                                            st.write(f"**카테고리:** {item.get('category', 'N/A')}")
                                            
                                            # LED 제어 버튼
                                            if st.button(f"💡 위치 표시", key=f"led_{item['id']}_{chat['timestamp']}"):
                                                with st.spinner("LED 제어 중..."):
                                                    try:
                                                        loop = asyncio.new_event_loop()
                                                        asyncio.set_event_loop(loop)
                                                        led_result = loop.run_until_complete(
                                                            st.session_state.agent.highlight_item_location(
                                                                item["id"], 10, "blue"
                                                            )
                                                        )
                                                        loop.close()
                                                        
                                                        if led_result.get("success"):
                                                            st.success(led_result.get("message"))
                                                        else:
                                                            st.error(led_result.get("message"))
                                                    except Exception as e:
                                                        st.error(f"LED 제어 오류: {str(e)}")
                                else:
                                    st.write("검색 결과가 없습니다.")
                            
                            # 카테고리 목록 표시
                            elif "categories" in data:
                                categories = data["categories"]
                                st.write(f"🏷️ **{len(categories)}개 카테고리:**")
                                for cat in categories:
                                    st.write(f"- {cat}")
                        
                        # 성공 메시지
                        if result.get("message"):
                            st.info(result["message"])
                        
                        # LLM 메시지 (있다면)
                        if result.get("llm_message"):
                            st.success(f"🤖 {result['llm_message']}")
                        
                        # 처리 모드 표시
                        if result.get("processing_mode"):
                            st.caption(f"처리 방식: {result['processing_mode']}")
                    else:
                        st.error(f"❌ {result.get('message', '알 수 없는 오류')}")
    
    # 사용자 입력
    user_input = st.chat_input("물품에 대해 무엇이든 물어보세요... (예: '노트북 어디 있어?', '전자기기 보여줘')")
    
    if user_input:
        # 사용자 메시지 추가
        st.session_state.chat_history.append({
            "type": "user",
            "message": user_input,
            "timestamp": datetime.now()
        })
        
        # AI 응답 처리
        with st.spinner("AI가 답변을 생성하고 있습니다..."):
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(
                    st.session_state.agent.process_query(user_input)
                )
                loop.close()
                
                # AI 응답 추가
                st.session_state.chat_history.append({
                    "type": "assistant",
                    "message": f"'{user_input}'에 대한 검색 결과입니다.",
                    "result": result,
                    "timestamp": datetime.now()
                })
                
                st.experimental_rerun()
                
            except Exception as e:
                st.error(f"오류가 발생했습니다: {str(e)}")

with col2:
    st.header("📊 시스템 정보")
    
    # 실시간 통계
    with st.spinner("통계 로딩 중..."):
        try:
            # 전체 물품 수
            all_items_result = st.session_state.agent._handle_get_all_items()
            
            # 카테고리 수
            categories_result = st.session_state.agent._handle_get_categories()
            
            if all_items_result.get("success"):
                total_items = all_items_result.get("data", {}).get("total_count", 0)
                st.metric("총 물품 수", total_items)
            
            if categories_result.get("success"):
                total_categories = categories_result.get("data", {}).get("count", 0)
                st.metric("카테고리 수", total_categories)
                
        except Exception as e:
            st.error(f"통계 로딩 실패: {str(e)}")
    
    st.markdown("---")
    
    # 도움말
    st.header("❓ 사용법")
    
    if GEMINI_AVAILABLE and hasattr(st.session_state.agent, 'use_llm') and st.session_state.agent.use_llm:
        st.markdown("""
        **🤖 Gemini LLM 모드**
        
        **자연어 질문 예시:**
        - "책상 위에 있는 노트북 찾아줘"
        - "전자기기 중에서 충전 가능한 것들 보여줘"
        - "빨간색 펜이 어디에 있는지 LED로 표시해줘"
        - "A1부터 A3 구역에 있는 물품들 알려줘"
        - "무선 마우스의 정확한 위치를 알고 싶어"
        
        **고급 기능:**
        - 🧠 문맥 이해 (복잡한 문장 처리)
        - 🎯 의도 분석 (정확한 작업 판별)
        - 💬 자연스러운 대화
        - 🔍 스마트 검색 (유사 단어 매칭)
        """)
    else:
        st.markdown("""
        **⚡ 기본 모드**
        
        **질문 예시:**
        - "노트북 어디 있어?"
        - "전자기기 목록 보여줘"
        - "마우스 위치 LED로 표시해줘"
        - "모든 물품 보여줘"
        - "카테고리 알려줘"
        """)
    
    st.markdown("""
    **공통 기능:**
    - 🔍 자연어 물품 검색
    - 💡 LED 위치 표시
    - 📋 전체 목록 조회
    - 🏷️ 카테고리별 필터링
    """)

# 페이지 하단 정보
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        물품 관리 시스템 v2.0 | 🤖 Gemini Flash 2.5 + FastMCP + Streamlit + SQLite
    </div>
    """,
    unsafe_allow_html=True
)
