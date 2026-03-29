from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import List


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )

    app_name: str = "TalentID API"
    app_version: str = "1.0.0"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"

    host: str = "0.0.0.0"
    port: int = 8000

    database_url: str = "sqlite+aiosqlite:///./talentid.db"

    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    gemini_api_key: str = ""

    cors_origins: str = "http://localhost:3000"

    rate_limit_per_minute: int = 60

    log_level: str = "INFO"
    log_file: str = "logs/app.log"

    # Blockchain
    blockchain_rpc_url: str = "http://localhost:8545"
    talent_services_contract_address: str = ""
    talent_nft_contract_address: str = ""
    private_key: str = ""

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]


@lru_cache()
def get_settings() -> Settings:
    return Settings()
