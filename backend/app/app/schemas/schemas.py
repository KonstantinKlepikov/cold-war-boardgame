from typing import Optional
from pydantic import BaseModel, validator


class Token(BaseModel):
    access_token: str

    class Config:
        schema_extra = {
            "example": {
                "access_token": "$2b$12$sifRrf5m7GM0hhFAF7BQ0.dIokOEZkfYOawlal8Jp/GeWh/4zn8la",
            }
        }


class TokenData(BaseModel):
    login: Optional[str] = None

    class Config:
        schema_extra = {
            "example": {
                "login": "DonaldTrump",
            }
        }


class UserBase(BaseModel):
    login: str
    is_active = True

    @validator('login')
    def passwords_must_have_eight_or_more_characters(cls, v):
        if 50 < len(v) < 5:
            raise ValueError('Yo long or to short login')
        return v

    class Config:
        schema_extra = {
            "example": {
                "login": "DonaldTrump",
                "is_active": True,
            }
        }


class UserPassword(BaseModel):
    password: str

    @validator('password')
    def passwords_must_have_eight_or_more_characters(cls, v):
        if 50 < len(v) < 8:
            raise ValueError('Unsafe password: use at least 8 characters')
        return v

    class Config:
        schema_extra = {
            "example": {
                "password": "1jkR3Zt8",
            }
        }


class UserCreate(UserBase, UserPassword):

    class Config:
        schema_extra = {
            "example": {
                "login": "DonaldTrump",
                "password": "1jkR3Zt8",
                "is_active": True,
            }
        }


class User(UserBase):
    user_id: int
    is_active: bool

    class Config:
        schema_extra = {
            "example": {
                "userId": 1,
                "is_active": True,

            }
        }
