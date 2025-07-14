#!/bin/bash
# 물품 관리 시스템 실행 스크립트

echo "=== 물품 관리 시스템 시작 ==="

# 가상환경 활성화 (옵션)
# source venv/bin/activate

# 1. 데이터베이스 초기화
echo "1. 데이터베이스 초기화 중..."
python database.py

if [ $? -eq 0 ]; then
    echo "✅ 데이터베이스 초기화 완료"
else
    echo "❌ 데이터베이스 초기화 실패"
    exit 1
fi

# 2. MCP 서버 백그라운드 실행
echo "2. MCP 서버 시작 중..."
python mcp_server.py &
MCP_PID=$!

# 서버 시작 대기
sleep 3

echo "✅ MCP 서버 시작됨 (PID: $MCP_PID)"

# 3. Streamlit 클라이언트 실행
echo "3. Streamlit 클라이언트 시작 중..."
echo "브라우저에서 http://localhost:8501 을 열어주세요"

streamlit run streamlit_client.py

# 종료 시 MCP 서버도 종료
echo "시스템 종료 중..."
kill $MCP_PID
echo "✅ 모든 서비스가 종료되었습니다"
