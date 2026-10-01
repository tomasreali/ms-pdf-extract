from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "ms-pdf-extract"
    max_file_size_mb: int = 10
    summary_service_url: str = "http://ms-ia-summary:8000/summarize"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()