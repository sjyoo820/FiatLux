# 스마트 물품 관리 시스템 - Next.js Frontend

## 프로젝트 개요

이 프로젝트는 5x8 그리드에서 물품의 위치를 시각적으로 관리하고, LED로 위치를 표시해주는 스마트 물품 관리 시스템의 웹 프론트엔드입니다.

## 주요 기능

### 🎯 핵심 기능
- **5x8 그리드 시각화**: 체스판 형태의 그리드에서 물품 위치를 실시간으로 확인
- **물품 검색**: 이름, 설명, 위치로 빠른 검색
- **물품 관리**: 추가, 수정, 삭제 기능
- **카테고리별 색상 구분**: 각 카테고리마다 다른 색상으로 시각적 구분
- **LED 하이라이트**: 선택된 물품의 실제 위치를 LED로 표시
- **AI 챗봇 연동**: Streamlit 챗봇과 연결 버튼

### 📊 시각화 기능
- 실시간 그리드 상태 표시
- 물품 위치 하이라이트
- 카테고리별 범례
- 그리드 사용률 통계

## 시스템 아키텍처

### 📊 전체 시스템 구조

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
│  localhost:8001 │    │  localhost:8000 │    │   (물품 저장)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 🎯 역할 분리

#### Next.js Frontend (이 프로젝트)
- **목적**: 시각적 물품 관리 인터페이스
- **통신**: FastAPI REST 서버와 HTTP 통신
- **기능**: 5x8 그리드 시각화, CRUD 작업, 실시간 UI

#### Streamlit AI Chatbot
- **목적**: 자연어 기반 물품 조회
- **통신**: MCP 서버와 stdio 통신
- **기능**: AI 에이전트, 음성 명령, 대화형 인터페이스

#### 왜 이렇게 분리했나요?
1. **사용자 경험**: 시각적 관리 vs 대화형 조회
2. **기술 스택**: React 웹 UI vs Python AI 에이전트
3. **확장성**: 각각 독립적으로 개발/배포 가능

## 기술 스택

### Frontend
- **Next.js 14**: React 기반 웹 프레임워크
- **TypeScript**: 타입 안정성을 위한 정적 타입 체크
- **Tailwind CSS**: 유틸리티 퍼스트 CSS 프레임워크
- **Framer Motion**: 애니메이션 및 인터랙션

### Backend 연동
- **FastAPI REST 서버**: Next.js 전용 HTTP API (포트 8001)
- **FastMCP 서버**: Streamlit AI 챗봇 전용 MCP 서버 (포트 8000)
- **SQLite**: 공유 물품 데이터베이스
- **Gemini LLM**: AI 에이전트 연동 (Streamlit에서만 사용)
- **ESP32**: LED 제어

## 🚀 전체 시스템 시작 가이드

### 📋 시작 순서

1. **Python 백엔드 서버들 시작**
   ```bash
   cd /Users/loopin51/Desktop/개발/2025유연화
   
   # 1. REST API 서버 (포트 8001)
   python rest_api.py &
   
   # 2. MCP 서버 (포트 8000) 
   python mcp_server.py &
   
   # 3. Streamlit 챗봇 (포트 8501)
   streamlit run streamlit_client.py &
   ```

2. **Next.js 프론트엔드 시작**
   ```bash
   cd nextjs-inventory
   npm run dev
   ```

3. **접속 URL들**
   - 🌐 **Next.js 웹앱**: <http://localhost:3000>
   - 🤖 **AI 챗봇**: <http://localhost:8501>
   - 📚 **API 문서**: <http://localhost:8001/docs>

### 🔧 개발 환경 설정

#### Python 환경
```bash
# 가상환경 생성 (선택사항)
python -m venv venv
source venv/bin/activate  # macOS/Linux

# 의존성 설치
pip install -r requirements.txt
```

#### Node.js 환경
```bash
# Node.js 버전 확인 (18+ 필요)
node --version

# 의존성 설치
cd nextjs-inventory
npm install
```

#### 환경 변수 설정
```bash
# .env 파일 생성
cp .env.example .env

# Gemini API 키 설정
GOOGLE_API_KEY=your_gemini_api_key_here
```

## 설치 및 실행

### 사전 요구사항
- Node.js 18 이상
- npm 또는 yarn
- 백엔드 MCP 서버 실행 중

### 설치
```bash
cd nextjs-inventory
npm install
```

### 개발 서버 실행
```bash
npm run dev
```

브라우저에서 http://localhost:3000 접속

### 빌드
```bash
npm run build
npm start
```

## 📁 전체 프로젝트 구조

### 🏗️ 루트 디렉토리 (`/Users/loopin51/Desktop/개발/2025유연화/`)

```
2025유연화/
├── 📁 nextjs-inventory/           # Next.js 프론트엔드 (이 프로젝트)
├── 🐍 mcp_server.py              # FastMCP 서버 (MCP 프로토콜)
├── 🐍 rest_api.py                # FastAPI REST 서버 (HTTP API)
├── 🐍 streamlit_client.py        # Streamlit AI 챗봇 클라이언트
├── 🐍 gemini_agent.py            # Gemini LLM AI 에이전트
├── 🐍 database.py                # SQLite 데이터베이스 관리
├── 🐍 models.py                  # Pydantic 데이터 모델
├── 🐍 esp32_controller.py        # ESP32 LED 제어
├── 🔧 esp32_neopixel_server.ino  # Arduino ESP32 펌웨어
├── 🗃️ items.db                   # SQLite 데이터베이스 파일
├── ⚙️ .env                       # 환경 변수 (API 키 등)
├── 📋 requirements.txt           # Python 의존성
├── 🚀 start_system.sh            # 전체 시스템 시작 스크립트
├── 🧪 test_gemini.py             # Gemini API 테스트
├── 🧪 test_system.py             # 시스템 통합 테스트
└── 📖 README.md                  # 전체 프로젝트 문서
```

### 🌐 Next.js 프론트엔드 구조 (`nextjs-inventory/`)

```
nextjs-inventory/
├── src/
│   ├── components/              # React 컴포넌트
│   │   ├── InventoryGrid.tsx    # 5x8 그리드 시각화 컴포넌트
│   │   ├── SearchInterface.tsx  # 검색 인터페이스 컴포넌트
│   │   └── ItemManager.tsx      # 물품 관리 CRUD 컴포넌트
│   ├── pages/                   # Next.js 페이지
│   │   └── index.tsx            # 메인 페이지 (통합 인터페이스)
│   ├── types/                   # TypeScript 타입 정의
│   │   └── index.ts             # 전체 타입 인터페이스
│   ├── lib/                     # 유틸리티 라이브러리
│   │   └── api.ts               # REST API 클라이언트
│   └── styles/                  # 스타일 시트
│       └── globals.css          # 전역 CSS (Tailwind 포함)
├── .next/                       # Next.js 빌드 결과물
├── node_modules/                # Node.js 의존성
├── package.json                 # Node.js 프로젝트 설정
├── package-lock.json            # 의존성 잠금 파일
├── next.config.js               # Next.js 설정
├── tailwind.config.js           # Tailwind CSS 설정
├── tsconfig.json               # TypeScript 설정
├── postcss.config.js           # PostCSS 설정
├── next-env.d.ts               # Next.js 타입 정의
└── README.md                   # 프론트엔드 문서 (이 파일)
```

## 프로젝트 구조

## 주요 컴포넌트

### InventoryGrid
- 5x8 그리드 시각화
- 카테고리별 색상 구분
- 물품 위치 하이라이트
- 실시간 애니메이션

### SearchInterface
- 텍스트 검색 기능
- 카테고리 필터
- 검색 결과 하이라이트
- 디바운싱 구현

### ItemManager
- 물품 CRUD 기능
- 폼 유효성 검사
- 실시간 데이터 동기화

## API 연동

### 백엔드 서버

- **REST API**: <http://localhost:8001> (Next.js 전용)
- **MCP 서버**: <http://localhost:8000> (Streamlit 전용)
- **Streamlit 챗봇**: <http://localhost:8501>

### API 엔드포인트 (REST API)

- `GET /items` - 모든 물품 조회
- `POST /items` - 물품 추가
- `PUT /items/{id}` - 물품 수정
- `DELETE /items/{id}` - 물품 삭제
- `GET /categories` - 카테고리 목록
- `POST /highlight` - LED 하이라이트

## 설정

### 환경 변수

```env
NEXT_PUBLIC_API_URL=http://localhost:8001
NEXT_PUBLIC_STREAMLIT_URL=http://localhost:8501
```

### Tailwind CSS 설정
- 커스텀 그리드 스타일
- 카테고리별 색상 정의
- 반응형 디자인

## 사용법

### 1. 그리드 뷰
- 메인 화면에서 5x8 그리드 확인
- 물품 클릭시 상세 정보 표시
- LED 하이라이트 자동 활성화

### 2. 검색 기능
- 검색 탭에서 물품 검색
- 텍스트 및 카테고리 필터 사용
- 검색 결과에서 물품 선택

### 3. 물품 관리
- 관리 탭에서 물품 추가/수정/삭제
- 폼 유효성 검사 자동 실행
- 실시간 데이터 업데이트

### 4. AI 챗봇 연동
- 우상단 "AI 챗봇" 버튼 클릭
- Streamlit 챗봇 페이지로 이동
- 자연어로 물품 위치 문의

## 개발 가이드

### 새 컴포넌트 추가
1. `src/components/` 폴더에 새 컴포넌트 생성
2. TypeScript 인터페이스 정의
3. Tailwind CSS 스타일 적용
4. 메인 페이지에 import

### API 확장
1. `src/lib/api.ts`에 새 메서드 추가
2. 타입 정의 업데이트
3. 에러 핸들링 구현

### 스타일 커스터마이징
1. `tailwind.config.js`에서 색상/스타일 정의
2. `src/styles/globals.css`에 커스텀 CSS 추가
3. 컴포넌트에서 클래스 적용

## 트러블슈팅

### 일반적인 문제
1. **API 연결 오류**: 백엔드 서버 실행 상태 확인
2. **LED 하이라이트 안됨**: ESP32 연결 상태 확인
3. **검색 결과 없음**: 데이터베이스 데이터 확인

### 개발 모드 오류
- TypeScript 에러: `npm run build`로 타입 검사
- 스타일 오류: Tailwind CSS 설정 확인
- 컴포넌트 오류: React DevTools 사용

## 🔍 시스템 상태 확인

### 📊 실행 중인 서비스 확인

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

### 🌐 접속 테스트

| 서비스 | URL | 상태 확인 방법 |
|--------|-----|----------------|
| Next.js 웹앱 | <http://localhost:3000> | 브라우저에서 그리드 화면 확인 |
| REST API | <http://localhost:8001/docs> | FastAPI 문서 페이지 접속 |
| Streamlit 챗봇 | <http://localhost:8501> | AI 챗봇 인터페이스 확인 |
| API Health | <http://localhost:8001/health> | `{"status": "healthy"}` 응답 |

### 🔧 문제 해결

#### 포트 충돌 해결
```bash
# 사용 중인 프로세스 종료
sudo lsof -ti:8000 | xargs kill -9
sudo lsof -ti:8001 | xargs kill -9
sudo lsof -ti:8501 | xargs kill -9
```

#### 데이터베이스 초기화
```bash
# SQLite 데이터베이스 재생성
rm items.db
python database.py  # 샘플 데이터와 함께 재생성
```

#### 의존성 재설치
```bash
# Python 의존성
pip install -r requirements.txt --force-reinstall

# Node.js 의존성  
cd nextjs-inventory
rm -rf node_modules package-lock.json
npm install
```

## 향후 개선사항

- [ ] 드래그 앤 드롭으로 물품 이동
- [ ] 실시간 알림 시스템
- [ ] 물품 이력 관리
- [ ] 모바일 앱 지원
- [ ] 다국어 지원

## 라이센스

MIT License

## 기여하기

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

---

**개발팀**: 2025년 유연화 프로젝트팀
**연락처**: 프로젝트 관련 문의사항은 이슈 등록 바랍니다.

## 📋 주요 파일별 역할

### 🐍 백엔드 Python 파일들

| 파일명 | 역할 | 포트 | 설명 |
|--------|------|------|------|
| `mcp_server.py` | MCP 서버 | 8000 | FastMCP 기반, Streamlit과 stdio 통신 |
| `rest_api.py` | REST API | 8001 | FastAPI 기반, Next.js와 HTTP 통신 |
| `streamlit_client.py` | AI 챗봇 | 8501 | Streamlit 웹앱, Gemini LLM 연동 |
| `gemini_agent.py` | AI 에이전트 | - | Gemini Flash 2.5 LLM 처리 |
| `database.py` | DB 관리 | - | SQLite 데이터베이스 CRUD 작업 |
| `models.py` | 데이터 모델 | - | Pydantic 모델 정의 |
| `esp32_controller.py` | LED 제어 | - | ESP32 NeoPixel LED 통신 |

### 🌐 Next.js React 컴포넌트

| 컴포넌트 | 파일 | 기능 |
|----------|------|------|
| `InventoryGrid` | `InventoryGrid.tsx` | 5x8 그리드 시각화, 카테고리별 색상, 애니메이션 |
| `SearchInterface` | `SearchInterface.tsx` | 물품 검색, 필터링, 하이라이트 |
| `ItemManager` | `ItemManager.tsx` | CRUD 작업, 폼 관리, 유효성 검사 |
| `MainPage` | `index.tsx` | 탭 네비게이션, 상태 관리, API 연동 |

### ⚙️ 설정 파일들

| 파일명 | 용도 | 설명 |
|--------|------|------|
| `package.json` | NPM 설정 | Next.js 의존성, 스크립트 |
| `tsconfig.json` | TypeScript | 타입 설정, 컴파일 옵션 |
| `tailwind.config.js` | Tailwind CSS | 커스텀 스타일, 색상 테마 |
| `next.config.js` | Next.js | 빌드 설정, 최적화 |
| `.env` | 환경 변수 | API 키, URL 설정 |
| `requirements.txt` | Python 의존성 | 백엔드 패키지 목록 |

### 🗃️ 데이터 파일들

| 파일명 | 타입 | 내용 |
|--------|------|------|
| `items.db` | SQLite | 물품 데이터, 카테고리 정보 |
| `.env` | 환경 변수 | Gemini API 키, 설정값 |
