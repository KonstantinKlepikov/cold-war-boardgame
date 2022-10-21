import toml
from pydantic import BaseSettings
from typing import Optional, Dict, List
from app.schemas.errors import HttpErrorMessage


poetry_data = toml.load('pyproject.toml')['tool']['poetry']


class Settings(BaseSettings):
    # db settings
    mongodb_url: str
    db_name: str = 'prod-db'
    test_mongodb_url: Optional[str] = None
    access_token_expires_minites: Optional[int] = None
    secret_key: str

    # open-api settings
    title: str = poetry_data['name']
    descriprion: str = poetry_data['description']
    version: str = poetry_data['version']
    openapi_tags: List = [
        {
            "name": "user",
            "description": "Users api",
        },
        {
            "name": "game",
            "description": "Game api",
        },
    ]

    # open-api errors
    AUTHENTICATE_RESPONSE_ERRORS: Dict = {
        code: {'model': HttpErrorMessage} for code in [400,]
        }


settings = Settings()
