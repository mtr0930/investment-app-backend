from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from apscheduler.schedulers.background import BackgroundScheduler

# 이전에 만든 모듈들 임포트
from app.core.database import init_db, AsyncSessionLocal
from app.models.investment import InvestmentDiary
from app.schemas.diary import DiaryCreate
from app.services.market_data import MarketService

app = FastAPI(title="Investment Diary AI API")


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
    return {"message": "Investment Diary API is running", "version": "1.0.0"}


# 3. 시장 요약 및 특정 종목 조회 API
@app.get("/market/summary")
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


@app.get("/market/{ticker}")
async def get_ticker_info(ticker: str):
    """
    특정 종목의 현재가와 뉴스 조회
    """
    data = await MarketService.fetch_ticker_data(ticker)
    if not data:
        raise HTTPException(status_code=404, detail="Ticker not found")
    return data


# 4. 투자 일기 관련 API
@app.post("/diaries", response_model=None)
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


@app.get("/diaries")
async def list_diaries(db: AsyncSession = Depends(get_db)):
    """
    내가 쓴 투자 일기 전체 목록 조회 (최신순)
    """
    result = await db.execute(
        select(InvestmentDiary).order_by(InvestmentDiary.created_at.desc())
    )
    diaries = result.scalars().all()
    return diaries


# 5. 특정 일기 상세 조회 (ID 기준)
@app.get("/diaries/{diary_id}")
async def get_diary_detail(diary_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(InvestmentDiary).where(InvestmentDiary.id == diary_id)
    )
    diary = result.scalar_one_or_none()
    if not diary:
        raise HTTPException(status_code=404, detail="Diary not found")
    return diary

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)