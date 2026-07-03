from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str = ""
    database_url: str = "postgresql+asyncpg://analyst:analyst@localhost:5436/analyst_db"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
