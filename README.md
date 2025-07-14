# 스마트 물품 관리 시스템

## 📁 정리된 프로젝트 구조

```
smart-inventory-system/
├── 📂 backend/                    # 백엔드 서비스들
│   ├── 📂 api/                    # REST API 서버
│   │   └── rest_api.py           # FastAPI REST 서버 (포트 8001)
│   ├── 📂 mcp/                    # MCP 서버
│   │   └── mcp_server.py         # FastMCP 서버 (포트 8000)
│   ├── 📂 database/               # 데이터베이스 관리
│   │   └── database.py           # SQLite 데이터베이스 CRUD
│   ├── 📂 models/                 # 데이터 모델
│   │   └── models.py             # Pydantic 모델 정의
│   ├── 📂 controllers/            # 컨트롤러 및 에이전트
│   │   ├── gemini_agent.py       # Gemini LLM AI 에이전트
│   │   └── esp32_controller.py   # ESP32 LED 제어
│   └── 📂 tests/                  # 테스트 파일들
│       ├── test_gemini.py        # Gemini API 테스트
│       └── test_system.py        # 시스템 통합 테스트
├── 📂 frontend/                   # 프론트엔드 인터페이스
│   ├── 📂 nextjs-inventory/       # Next.js 웹 애플리케이션
│   │   ├── src/
│   │   │   ├── components/       # React 컴포넌트
│   │   │   ├── pages/            # Next.js 페이지
│   │   │   ├── types/            # TypeScript 타입
│   │   │   ├── lib/              # API 클라이언트
│   │   │   └── styles/           # 스타일 시트
│   │   └── ... (Next.js 설정 파일들)
│   └── streamlit_client.py       # Streamlit AI 챗봇 (포트 8501)
├── 📂 hardware/                   # 하드웨어 펌웨어
│   └── esp32_neopixel_server.ino # Arduino ESP32 펌웨어
├── 📂 scripts/                    # 유틸리티 스크립트
│   └── start_system.sh           # 전체 시스템 시작 스크립트
├── 📂 docs/                       # 문서
│   └── README.md                 # 전체 프로젝트 문서
├── 🗃️ items.db                    # SQLite 데이터베이스 파일
├── ⚙️ .env                        # 환경 변수 (API 키 등)
└── 📋 requirements.txt            # Python 의존성
```

## 🎯 시스템 아키텍처

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Next.js Web   │    │  Streamlit AI   │    │   ESP32 LED     │
│   Frontend      │    │   Chatbot       │    │   Controller    │
│  localhost:3000 │    │  localhost:8501 │    │   (Hardware)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
          │                       │                       │
          │ HTTP REST              │ MCP stdio             │ HTTP
          ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI       │    │   MCP Server    │    │   SQLite DB     │
│   REST Server   │◄──►│   FastMCP       │◄──►│   Database      │
│ backend/api/    │    │ backend/mcp/    │    │   items.db      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 시스템 시작 가이드

### 📋 시작 순서

1. **백엔드 서버들 시작**

   ```bash
   cd smart-inventory-system
   
   # 1. REST API 서버 (포트 8001)
   python backend/api/rest_api.py &
   
   # 2. MCP 서버 (포트 8000)
   python backend/mcp/mcp_server.py &
   
   # 3. Streamlit 챗봇 (포트 8501)
   streamlit run frontend/streamlit_client.py &
   ```

2. **Next.js 프론트엔드 시작**

   ```bash
   cd frontend/nextjs-inventory
   npm run dev
   ```

3. **전체 시스템 자동 시작**

   ```bash
   ./scripts/start_system.sh
   ```

### 🌐 접속 URL

| 서비스 | URL | 설명 |
|--------|-----|------|
| 🌐 Next.js 웹앱 | <http://localhost:3000> | 메인 시각적 관리 인터페이스 |
| 🤖 AI 챗봇 | <http://localhost:8501> | Streamlit 자연어 대화 인터페이스 |
| 📚 API 문서 | <http://localhost:8001/docs> | FastAPI Swagger 문서 |
| 🔍 Health Check | <http://localhost:8001/health> | 시스템 상태 확인 |

## 📋 주요 컴포넌트 역할

### 🖥️ 백엔드 서비스 (`backend/`)

| 디렉토리 | 파일 | 역할 | 포트 |
|----------|------|------|------|
| `api/` | `rest_api.py` | FastAPI REST 서버 | 8001 |
| `mcp/` | `mcp_server.py` | FastMCP 프로토콜 서버 | 8000 |
| `database/` | `database.py` | SQLite 데이터베이스 관리 | - |
| `models/` | `models.py` | Pydantic 데이터 모델 | - |
| `controllers/` | `gemini_agent.py` | Gemini LLM AI 에이전트 | - |
| `controllers/` | `esp32_controller.py` | ESP32 LED 제어 | - |
| `tests/` | `test_*.py` | 단위 및 통합 테스트 | - |

### 🌐 프론트엔드 (`frontend/`)

| 디렉토리 | 파일/폴더 | 역할 | 포트 |
|----------|-----------|------|------|
| `nextjs-inventory/` | Next.js 프로젝트 | 시각적 웹 관리 인터페이스 | 3000 |
| `.` | `streamlit_client.py` | AI 챗봇 인터페이스 | 8501 |

## 🔧 기타 (`hardware/`, `scripts/`, `docs/`)

| 디렉토리 | 파일 | 역할 |
|----------|------|------|
| `hardware/` | `esp32_neopixel_server.ino` | Arduino ESP32 펌웨어 |
| `scripts/` | `start_system.sh` | 전체 시스템 시작 스크립트 |
| `docs/` | `README.md` | 프로젝트 문서 |

## 🔧 개발 환경 설정

### Python 환경

```bash
# 가상환경 생성 (선택사항)
python -m venv venv
source venv/bin/activate  # macOS/Linux

# 의존성 설치
pip install -r requirements.txt
```

### Node.js 환경

```bash
# Next.js 프로젝트로 이동
cd frontend/nextjs-inventory

# 의존성 설치
npm install
```

### 환경 변수 설정

```bash
# .env 파일 생성 (루트 디렉토리에)
cp .env.example .env

# Gemini API 키 설정
GOOGLE_API_KEY=your_gemini_api_key_here
```

## 🔍 시스템 상태 확인

### 실행 중인 서비스 확인

```bash
# 포트 사용 확인
lsof -i :3000  # Next.js
lsof -i :8000  # MCP 서버  
lsof -i :8001  # REST API
lsof -i :8501  # Streamlit

# 프로세스 확인
ps aux | grep python
ps aux | grep node
```

### 접속 테스트

- ✅ Next.js: 브라우저에서 그리드 화면 확인
- ✅ REST API: FastAPI 문서 페이지 접속
- ✅ Streamlit: AI 챗봇 인터페이스 확인
- ✅ Health: `{"status": "healthy"}` 응답 확인

## 🛠️ 트러블슈팅

### 포트 충돌 해결

```bash
# 사용 중인 프로세스 종료
sudo lsof -ti:8000 | xargs kill -9
sudo lsof -ti:8001 | xargs kill -9
sudo lsof -ti:8501 | xargs kill -9
```

### 데이터베이스 초기화

```bash
# SQLite 데이터베이스 재생성
rm items.db
python backend/database/database.py
```

### 의존성 재설치

```bash
# Python 의존성
pip install -r requirements.txt --force-reinstall

# Node.js 의존성  
cd frontend/nextjs-inventory
rm -rf node_modules package-lock.json
npm install
```

## 📈 향후 개선사항

- [ ] Docker 컨테이너화
- [ ] CI/CD 파이프라인 구축
- [ ] 로깅 시스템 개선
- [ ] 모니터링 대시보드 추가
- [ ] 데이터베이스 마이그레이션 스크립트
- [ ] 단위 테스트 커버리지 확대

## 🤝 기여하기

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

---

**개발팀**: 2025년 유연화 프로젝트팀  
**라이센스**: MIT License
