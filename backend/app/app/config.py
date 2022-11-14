import toml
from pydantic import BaseSettings
from typing import Optional, Dict, List, Type
from app.schemas import errors


poetry_data = toml.load('pyproject.toml')['tool']['poetry']
ErrorType = Dict[int, Dict[str, Type[errors.HttpErrorMessage]]]


class Settings(BaseSettings):
    # db settings
    mongodb_url: str
    db_name: str = 'prod-db'
    test_mongodb_url: Optional[str] = None
    access_token_expires_minites: Optional[int] = None

    # JWT
    secret_key: str
    algorithm: str

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
            "name": "game/data",
            "description": "Game data api",
        },
        {
            "name": "game",
            "description": "Game processing api",
        },
    ]

    # open-api errors
    AUTHENTICATE_RESPONSE_ERRORS: ErrorType = {
        400: {'model': errors.HttpError400},
        }
    ACCESS_ERRORS: ErrorType = {
        401: {'model': errors.HttpError401},
        }

    # test data
    user0_login: Optional[str] = None
    user0_password: Optional[str] = None
    user0_hashed_password: Optional[str] = None
    user0_token: Optional[str] = None


settings = Settings()
