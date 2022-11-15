from typing import Optional
from pydantic import BaseModel, validator


class Token(BaseModel):
    access_token: str
    token_type: str

    class Config:
        schema_extra = {
            "example": {
                "access_token":
                    "$2b$12$sifRrf5m7GM0hhFAF7BQ0.dIokOEZkfYOawlal8Jp/GeWh/4zn8la",
                    "token_type": "bearer",
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

    @validator('login')
    def passwords_must_have_eight_or_more_characters(cls, v):
        if 50 < len(v) < 5:
            raise ValueError('To long or to short login')
        return v

    class Config:
        schema_extra = {
            "example": {
                "login": "DonaldTrump",
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
                "password": "greatagain",
            }
        }


class UserCreateUpdate(UserBase, UserPassword):

    class Config:
        schema_extra = {
            "example": {
                "login": "DonaldTrump",
                "password": "greatagain",
            }
        }


class UserInDBBase(UserBase):

    is_active: Optional[bool] = True

    class Config:
        schema_extra = {
            "example": {
                "login": "DonaldTrump",
                "is_active": True,
            }
        }


class User(UserInDBBase):

    class Config:
        schema_extra = {
            "example": {
                "login": "DonaldTrump",
                "is_active": True,
            }
        }


class UserInDB(UserInDBBase):
    hashed_password: str

    class Config:
        schema_extra = {
            "example": {
                "login": "DonaldTrump",
                "is_active": True,
                "hashed_password":
                    "$2b$12$sifRrf5m7GM0hhFAF7BQ0.dIokOEZkfYOawlal8Jp/GeWh/4zn8la",
            }
        }