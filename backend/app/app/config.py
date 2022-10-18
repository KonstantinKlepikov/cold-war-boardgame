from pydantic import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    mongodb_url: str
    db_name: str = 'prod-db'
    test_mongodb_url: Optional[str] = None
    access_token_expires_minites: Optional[int] = None
    secret_key: str


settings = Settings()
