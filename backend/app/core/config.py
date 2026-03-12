from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    APP_NAME: str = "MD-ADSS"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # AWS Configuration
    AWS_REGION: str = "us-east-1"
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""

    # Amazon Nova 2 Lite — Foundation model via Bedrock Converse API
    NOVA_LITE_MODEL_ID: str = "amazon.nova-2-lite-v1:0"

    # Amazon Bedrock Agent — Nova Act + Nova Forge orchestration
    # NOVA_AGENT_ID: your 10-char Agent ID from the Bedrock console agent overview
    # NOVA_AGENT_ALIAS_ID: the alias ID shown on the agent overview page
    NOVA_AGENT_ID: str = ""
    NOVA_AGENT_ALIAS_ID: str = "PLLSBPKVUS"

    # Simulation settings
    LOG_GENERATION_INTERVAL: float = 2.0
    THREAT_DETECTION_INTERVAL: float = 5.0
    MAX_EVENTS_IN_MEMORY: int = 5000

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
