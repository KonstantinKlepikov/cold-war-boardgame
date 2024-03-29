import toml
from pydantic import BaseSettings
from typing import Optional, Type
from app.schemas import scheme_errors


poetry_data = toml.load('pyproject.toml')['tool']['poetry']
ErrorType = dict[int, dict[str, Type[scheme_errors.HttpErrorMessage]]]


class Settings(BaseSettings):
    # api vars
    api_v1_str: str = "/api/v1"

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
    openapi_tags: list = [
        {
            "name": "user",
            "description": "Users api",
        },
        {
            "name": "game_data",
            "description": "Game data api",
        },
        {
            "name": "game",
            "description": "Game processing api",
        },
    ]

    # open-api errors
    AUTHENTICATE_RESPONSE_ERRORS: ErrorType = {
        400: {'model': scheme_errors.HttpError400},
            }
    ACCESS_ERRORS: ErrorType = {
        401: {'model': scheme_errors.HttpError401},
            }
    CURRENT_DATA_ERRORS: ErrorType = {
        401: {'model': scheme_errors.HttpError401},
        404: {'model': scheme_errors.HttpError404},
            }
    NEXT_ERRORS: ErrorType = {
        401: {'model': scheme_errors.HttpError401},
        404: {'model': scheme_errors.HttpError404},
        409: {'model': scheme_errors.HttpError409},
            }

    # test data
    user0_login: Optional[str] = None
    user0_password: Optional[str] = None
    user0_hashed_password: Optional[str] = None
    user0_token: Optional[str] = None

    user1_login: Optional[str] = None
    user1_password: Optional[str] = None
    user1_hashed_password: Optional[str] = None

    user2_login: Optional[str] = None
    user2_password: Optional[str] = None
    user2_hashed_password: Optional[str] = None


settings = Settings()
