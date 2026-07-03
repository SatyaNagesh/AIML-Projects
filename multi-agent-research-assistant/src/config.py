from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    openai_api_key: str = ""
    openai_model: str = "gpt-5"

    tavily_api_key: str = ""

    database_url: str = "postgresql+asyncpg://agent:agent@localhost:5433/research_db"

    host: str = "0.0.0.0"
    port: int = 8001


settings = Settings()
