from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class InvestmentDiary(Base):
    __tablename__ = "investment_diaries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)

    # 제목 추가 (일기를 리스트로 보여줄 때 유용)
    title = Column(String, nullable=True)

    # 본문 (전체 시장 상황, 심리 등 자유롭게 기록)
    content = Column(Text, nullable=False)

    # 주요 언급 종목 (필수 아님, 여러 개일 수 있으므로 리스트 형태 저장)
    # 예: ["TSLA", "NVDA", "NASDAQ"]
    mentioned_tickers = Column(JSON, nullable=True)

    # 사용자의 주관적인 시장 심리 점수 (1~10점 등)
    market_sentiment_score = Column(Integer, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

class MarketSnapshot(Base):
    __tablename__ = "market_snapshots"

    id = Column(Integer, primary_key=True)
    ticker = Column(String, index=True)
    price = Column(Float)
    news_summary = Column(JSON)          # 그날의 주요 뉴스 요약
    captured_at = Column(DateTime, default=datetime.utcnow)