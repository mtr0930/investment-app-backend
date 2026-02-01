from datetime import datetime
import json
import httpx
from fastapi import FastAPI, Depends, HTTPException, APIRouter, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, extract, and_, func, cast, Date
from typing import Optional


from apscheduler.schedulers.background import BackgroundScheduler

# 이전에 만든 모듈들 임포트
from app.core.database import init_db, AsyncSessionLocal
from app.models.investment import InvestmentDiary
from app.schemas.diary import DiaryCreate
from app.services.market_data import MarketService

app = FastAPI(title="Investment Diary AI API")

# ... existing code ...

# CORS 미들웨어 설정 (모바일/외부 접속 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 도메인 허용 (보안 필요 시 특정 IP로 제한 가능)
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP Method 허용 (GET, POST, OPTIONS 등)
    allow_headers=["*"],  # 모든 헤더 허용
)

@app.websocket("/ws/ai-analyze")
async def websocket_ai_analyze(websocket: WebSocket):
    await websocket.accept()
    try:
        # 클라이언트로부터 데이터 수신 (JSON)
        data = await websocket.receive_json()
        content = data.get("content", "")
        user_prompt = data.get("prompt", "")

        # AI에게 보낼 프롬프트 구성
        full_prompt = (
            f"당신은 전문 주식 투자 분석가입니다. 사용자의 투자 일기를 읽고, "
            f"객관적인 피드백, 감정 분석, 그리고 개선할 점을 한국어로 조언해 주세요.\n\n"
            f"추가 요청사항: {user_prompt}\n\n"
            f"--- 일기 내용 ---\n{content}\n----------------"
        )

        # Ollama API 호출 (스트리밍)
        # 로컬 Ollama 엔드포인트: http://localhost:11434/api/generate
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST", 
                "http://localhost:11434/api/generate", 
                json={
                    "model": "mistral",  # 모델명 (설치된 모델에 맞게 변경 가능)
                    "prompt": full_prompt,
                    "stream": True
                }, 
                timeout=60.0
            ) as response:
                # 스트리밍 응답 처리
                async for line in response.aiter_lines():
                    if line:
                        json_response = json.loads(line)
                        chunk = json_response.get("response", "")
                        if chunk:
                            await websocket.send_text(chunk)
                        
                        if json_response.get("done", False):
                            break
                            
    except WebSocketDisconnect:
        print("Client disconnected from AI analysis")
    except Exception as e:
        print(f"AI Analysis Error: {e}")
        try:
            await websocket.send_text(f"Error: {str(e)}")
        except:
            pass

# API 라우터 생성 (prefix 설정을 통해 모든 경로 앞에 /api 추가)
api_router = APIRouter(prefix="/api")

# 1. DB 세션 의존성 주입 함수
# DB 세션 의존성 주입 (API 호출 시마다 세션 생성/닫기 관리)
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


# 2. 서버 시작 시 실행되는 이벤트
@app.on_event("startup")
async def on_startup():
    # 테이블이 없으면 생성
    await init_db()

    # 스케줄러 시작 (예: 1시간마다 시장 데이터 동기화 로그)
    scheduler = BackgroundScheduler()
    scheduler.add_job(scheduled_market_sync, 'interval', hours=1)
    scheduler.start()
    print("✅ Database initialized and Scheduler started.")


def scheduled_market_sync():
    # 백그라운드에서 주기적으로 실행될 로직 (필요 시 확장)
    print("⏰ Periodic Market Sync: Fetching major indices...")


# --- API Endpoints ---

@app.get("/")
async def root():
    return {"message": "Investment Diary API is running. Go to /api/ for endpoints.", "version": "1.0.0"}


# 3. 시장 요약 및 특정 종목 조회 API
@api_router.get("/market/summary")
async def get_market_summary():
    """
    메인 화면용: 주요 지수(S&P500, NASDAQ) 및 시장 뉴스 요약
    """
    indices = ["^GSPC", "^IXIC"]  # S&P500, NASDAQ 티커
    summary = {}
    for ticker in indices:
        data = await MarketService.fetch_ticker_data(ticker)
        summary[ticker] = data
    return summary


@api_router.get("/market/{ticker}")
async def get_ticker_info(ticker: str):
    """
    특정 종목의 현재가와 뉴스 조회
    """
    data = await MarketService.fetch_ticker_data(ticker)
    if not data:
        raise HTTPException(status_code=404, detail="Ticker not found")
    return data


# 4. 투자 일기 관련 API
@api_router.post("/diaries", response_model=None)
async def create_diary(diary_in: DiaryCreate, db: AsyncSession = Depends(get_db)):
    """
    유연한 투자 일기 작성 (종목 지정 가능/미지정 가능)
    """
    new_diary = InvestmentDiary(
        title=diary_in.title,
        content=diary_in.content,
        mentioned_tickers=diary_in.mentioned_tickers,
        market_sentiment_score=diary_in.market_sentiment_score,
        user_id="test_user_01"  # 현재는 하드코딩, 추후 인증 도입 시 수정
    )
    db.add(new_diary)
    await db.commit()
    await db.refresh(new_diary)
    return new_diary


@api_router.get("/diaries/summary")
async def get_diary_summary(year: int, month: int, db: AsyncSession = Depends(get_db)):
    """
    특정 연월의 일기 목록 조회 (캘린더용)
    """
    result = await db.execute(
        select(InvestmentDiary)
        .where(extract('year', InvestmentDiary.created_at) == year)
        .where(extract('month', InvestmentDiary.created_at) == month)
        .order_by(InvestmentDiary.created_at.asc())
    )
    diaries = result.scalars().all()
    return diaries


@api_router.get("/diaries")
async def list_diaries(
    diary_date: Optional[str] = None, 
    db: AsyncSession = Depends(get_db)
):
    """
    내가 쓴 투자 일기 전체 목록 조회 (최신순)
    - diary_date: "YYYY-MM-DD" 형태의 문자열. 제공 시 해당 날짜의 일기만 조회.
    """
    stmt = select(InvestmentDiary)
    
    if diary_date:
        # 문자열을 Python date 객체로 변환하여 DB의 Date 타입과 비교
        # 이렇게 해야 Postgres에서 Date = Date 비교가 되어 오류가 발생하지 않음
        try:
            target_date = datetime.strptime(diary_date, "%Y-%m-%d").date()
            stmt = stmt.where(
                cast(InvestmentDiary.created_at, Date) == target_date
            )
        except ValueError:
            # 날짜 형식이 잘못된 경우 400 에러 반환 (선택 사항)
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    stmt = stmt.order_by(InvestmentDiary.created_at.desc())
    
    result = await db.execute(stmt)
    diaries = result.scalars().all()
    return diaries

# 6. 일기 삭제 API (ID 기준)
@api_router.delete("/diaries/{diary_id}")
async def delete_diary(diary_id: int, db: AsyncSession = Depends(get_db)):
    # 삭제할 일기 조회
    result = await db.execute(
        select(InvestmentDiary).where(InvestmentDiary.id == diary_id)
    )
    diary = result.scalar_one_or_none()
    
    if not diary:
        raise HTTPException(status_code=404, detail="Diary not found")
        
    await db.delete(diary)
    await db.commit()
    return {"message": "Diary deleted successfully", "id": diary_id}


# 5. 특정 일기 상세 조회 (ID 기준)
@api_router.get("/diaries/{diary_id}")
async def get_diary_detail(diary_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(InvestmentDiary).where(InvestmentDiary.id == diary_id)
    )
    diary = result.scalar_one_or_none()
    if not diary:
        raise HTTPException(status_code=404, detail="Diary not found")
    return diary

# 라우터 등록
app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)