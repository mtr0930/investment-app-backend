from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.investment import Base

# 1. 비동기 엔진 생성 (echo=True는 실행되는 SQL 로그를 터미널에 출력함)
engine = create_async_engine(settings.DATABASE_URL, echo=True)

# 2. 비동기 세션 팩토리 생성
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# 3. DB 초기화 함수 (서버 시작 시 테이블 생성)
async def init_db():
    async with engine.begin() as conn:
        # 이 코드는 models/investment.py에 정의된 모든 Base 기반 테이블을 생성함
        await conn.run_sync(Base.metadata.create_all)