# Investment Diary Backend

> **⚠️ 현재 기능 고도화 작업 중입니다 (Work In Progress)**
> *   AI 분석 기능(Ollama 연동) 및 투자 일기 세부 기능 개선 중

투자일기 기록 및 시장 데이터 분석을 위한 백엔드 API 서비스입니다. FastAPI를 기반으로 구축되었으며, PostgreSQL 데이터베이스와 연동하여 투자 일기를 관리하고 실시간 시장 데이터를 제공합니다.

## 🚀 주요 기능

*   **시장 요약 (Market Summary)**: S&P 500, NASDAQ 등 주요 지수의 실시간 데이터 및 관련 뉴스 요약 제공.
*   **투자 일기 (Investment Diary)**:
    *   투자 일기 작성, 조회, 상세 보기 (CRUD).
    *   특정 종목 태깅 및 시장 감정 점수(Market Sentiment Score) 기록.
*   **데이터 동기화**: APScheduler를 이용한 주기적인 시장 데이터 동기화.
*   **비동기 처리**: `async/await`를 활용한 고성능 비동기 API 처리.

## 🛠 기술 스택

*   **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
*   **Database**: PostgreSQL
*   **ORM**: SQLAlchemy (Async)
*   **Scheduler**: APScheduler
*   **Market Data**: yfinance
*   **Server**: Uvicorn

## ⚙️ 설치 및 실행 방법

### 1. 환경 설정 (Prerequisites)

Python 3.10 이상이 설치되어 있어야 합니다.

```bash
# 가상환경 생성
python3 -m venv venv

# 가상환경 활성화
# Mac/Linux
source venv/bin/activate
# Windows
.\venv\Scripts\activate
```

### 2. 패키지 설치

필요한 라이브러리를 설치합니다.

```bash
pip install -r requirements.txt
```

### 3. 환경 변수 설정 (.env)

프로젝트 루트 경로에 `.env` 파일을 생성하고 데이터베이스 접속 정보를 설정합니다.
(기존 `.env` 파일이 없다면 아래 예시를 참고하여 생성하세요)

```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost/dbname
```

### 4. 서버 실행

Uvicorn을 사용하여 개발 서버를 실행합니다.

```bash
# 기본 실행 (코드 변경 시 자동 재시작)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

*   서버가 정상적으로 실행되면 터미널에 `Application startup complete.` 로그가 표시됩니다.
*   API 문서는 브라우저에서 `http://localhost:8000/docs` 로 접속하여 확인할 수 있습니다.

### 5. AI 분석 기능 설정 (Ollama)

이 프로젝트는 로컬 LLM(Ollama)을 사용하여 프라이빗한 투자 일기 분석 기능을 제공합니다. AI 기능을 사용하려면 **Ollama가 백그라운드에서 실행**되어 있어야 합니다.

1.  **Ollama 설치**: [Ollama 공식 홈페이지](https://ollama.com/)에서 다운로드 및 설치.
2.  **서버 실행**:
    ```bash
    ollama serve
    ```
3.  **모델 다운로드**:
    기본 설정은 `mistral` 모델을 사용합니다. 아래 명령어로 다운로드하세요.
    ```bash
    ollama pull mistral
    ```
    (다른 모델을 사용하려면 `app/main.py`의 `model` 설정을 변경하세요)

### 6. 모바일(Expo)에서 접속 방법

모바일 기기나 시뮬레이터에서 백엔드에 접속하려면 `localhost` 대신 **컴퓨터의 내부 IP 주소**를 사용해야 합니다.

1.  **서버 실행**: 반드시 `--host 0.0.0.0` 옵션을 붙여서 실행하세요 (위 명령어 참고).
2.  **내부 IP 확인**:
    ```bash
    # Mac/Linux
    ifconfig | grep "inet " | grep -v 127.0.0.1
    ```
    (예: `192.168.0.x` 형태의 IP를 찾으세요)
3.  **Frontend 설정**: Expo 앱의 API URL 설정을 확인된 내부 IP로 변경하세요.
    *   예: `http://192.168.0.5:8000`

## 📂 프로젝트 구조

```
investment-app-backend/
├── app/
│   ├── core/           # 데이터베이스 설정 등 핵심 설정
│   ├── models/         # SQLAlchemy DB 모델 정의
│   ├── schemas/        # Pydantic 데이터 검증 스키마
│   ├── services/       # 비즈니스 로직 (시장 데이터 등)
│   └── main.py         # 애플리케이션 진입점 (Entry Point)
├── .env                # 환경 설정 파일
├── .gitignore          # Git 제외 파일 목록
├── docker-compose.yml  # Docker 설정 (선택 사항)
├── requirements.txt    # 의존성 패키지 목록
└── README.md           # 프로젝트 문서
```
