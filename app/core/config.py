from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # .env의 변수명과 일치해야 합니다.
    DATABASE_URL: str

    # .env 파일을 읽어오기 위한 설정
    model_config = SettingsConfigDict(env_file=".env")


# 전역에서 사용할 수 있도록 인스턴스 생성
settings = Settings()