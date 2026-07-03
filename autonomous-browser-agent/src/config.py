from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    openai_api_key: str = ""
    openai_model: str = "gpt-5"

    database_url: str = "postgresql+asyncpg://agent:agent@localhost:5432/agent_db"

    host: str = "0.0.0.0"
    port: int = 8000

    browser_headless: bool = True
    browser_viewport_width: int = 1280
    browser_viewport_height: int = 720
    browser_slow_mo: int = 50
    browser_nav_timeout: int = 30000


settings = Settings()
