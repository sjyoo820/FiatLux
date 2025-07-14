#!/usr/bin/env python3
"""
Gemini Flash 2.5 통합 테스트 스크립트
"""

import asyncio
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

async def test_gemini_integration():
    """Gemini 통합 테스트"""
    print("🤖 Gemini Flash 2.5 통합 테스트 시작\n")
    
    # 기본 import 테스트
    try:
        import google.generativeai as genai
        print("✅ google-generativeai 라이브러리 로드 성공")
    except ImportError:
        print("❌ google-generativeai 라이브러리가 없습니다.")
        print("설치 명령: pip install google-generativeai")
        return
    
    # Gemini 에이전트 테스트
    try:
        from gemini_agent import GeminiItemAgent
        print("✅ GeminiItemAgent 로드 성공")
        
        # 에이전트 초기화
        agent = GeminiItemAgent()
        
        if agent.use_llm:
            print("✅ Gemini LLM 연결 성공!")
        else:
            print("⚠️ Gemini LLM 연결 실패 - API 키를 확인하세요")
            print("   .env 파일에 GOOGLE_AI_API_KEY를 설정하세요")
        
        # 테스트 쿼리들
        test_queries = [
            "노트북을 찾아줘",
            "전자기기 목록을 보여줘",
            "마우스 위치를 LED로 표시해줘",
            "모든 물품을 조회해줘",
            "카테고리를 알려줘"
        ]
        
        print("\n📝 테스트 쿼리 실행:")
        for i, query in enumerate(test_queries, 1):
            print(f"\n{i}. 질문: '{query}'")
            
            try:
                result = await agent.process_query(query)
                
                print(f"   결과: {result.get('success', False)}")
                print(f"   메시지: {result.get('message', 'N/A')}")
                
                if agent.use_llm and result.get('llm_message'):
                    print(f"   🤖 LLM 응답: {result['llm_message']}")
                
                processing_mode = result.get('processing_mode', '알 수 없음')
                print(f"   처리 방식: {processing_mode}")
                
                if result.get('success') and result.get('data', {}).get('items'):
                    item_count = len(result['data']['items'])
                    print(f"   발견된 물품: {item_count}개")
                
            except Exception as e:
                print(f"   ❌ 오류: {str(e)}")
        
        # 일반 채팅 테스트 (LLM이 활성화된 경우)
        if agent.use_llm:
            print("\n💬 일반 채팅 테스트:")
            
            chat_queries = [
                "안녕하세요! 이 시스템에 대해 설명해주세요",
                "물품을 잃어버렸을 때 어떻게 찾을 수 있나요?",
            ]
            
            for query in chat_queries:
                print(f"\n질문: '{query}'")
                try:
                    response = await agent.chat_with_gemini(query)
                    print(f"🤖 답변: {response}")
                except Exception as e:
                    print(f"❌ 채팅 오류: {str(e)}")
        
        print("\n✅ 모든 테스트가 완료되었습니다!")
        
    except ImportError as e:
        print(f"❌ GeminiItemAgent 로드 실패: {str(e)}")
    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {str(e)}")

def check_api_key():
    """API 키 확인"""
    print("🔑 API 키 확인:")
    
    api_key = os.getenv("GOOGLE_AI_API_KEY")
    if not api_key:
        print("❌ GOOGLE_AI_API_KEY 환경 변수가 설정되지 않았습니다.")
        print("\n설정 방법:")
        print("1. .env 파일을 열어주세요")
        print("2. GOOGLE_AI_API_KEY=your_actual_api_key_here 로 수정하세요")
        print("3. Google AI Studio (https://aistudio.google.com/app/apikey)에서 API 키를 발급받으세요")
        return False
    elif api_key == "your_google_ai_api_key_here":
        print("⚠️ 기본값이 설정되어 있습니다. 실제 API 키로 변경해주세요.")
        return False
    else:
        print("✅ API 키가 설정되어 있습니다.")
        print(f"   키 미리보기: {api_key[:10]}...{api_key[-10:]}")
        return True

if __name__ == "__main__":
    print("🧪 Gemini Flash 2.5 물품 관리 시스템 테스트\n")
    
    # API 키 확인
    has_api_key = check_api_key()
    print()
    
    # 메인 테스트 실행
    try:
        asyncio.run(test_gemini_integration())
    except KeyboardInterrupt:
        print("\n테스트가 사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"\n❌ 테스트 실행 오류: {str(e)}")
    
    if not has_api_key:
        print("\n💡 팁: API 키를 설정하면 더 정교한 자연어 처리가 가능합니다!")
        print("   현재는 기본 규칙 기반 모드로 동작합니다.")
