from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "FastAPI Microservice"
    VERSION: str = "0.1.0"
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    REDIS_URL: str = Field(default="redis://redis:6379/0")
    RABBITMQ_URL: str = Field(..., env="RABBITMQ_URL")
    LOG_LEVEL: str = Field(..., env="LOG_LEVEL")
    OTEL_EXPORTER_OTLP_ENDPOINT: str = Field(default="http://otel-collector:4317")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
