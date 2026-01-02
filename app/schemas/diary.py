from pydantic import BaseModel
from typing import List, Optional

class DiaryCreate(BaseModel):
    title: Optional[str] = "오늘의 투자 기록"
    content: str  # 일기 본문 (필수)
    # 언급된 종목들을 리스트로 받음 (예: ["TSLA", "NVDA", "NASDAQ"])
    mentioned_tickers: Optional[List[str]] = []
    market_sentiment_score: Optional[int] = 5  # 사용자가 느끼는 시장 점수 (1~10)