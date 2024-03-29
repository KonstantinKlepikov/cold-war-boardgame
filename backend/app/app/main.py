from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mongoengine import connect
from app.config import settings
from app.db.init_db import (
    check_db_cards_init, init_db_cards,
    check_db_users_init, init_db_users
        )
from app.api.api_v1.api import api_router


connect(
    host=settings.mongodb_url,
    name=settings.db_name,
    alias='default',
    )

if not check_db_cards_init():
    init_db_cards()
if not check_db_users_init():
    init_db_users()


app = FastAPI(
    title=settings.title,
    openapi_url=f"{settings.api_v1_str}/openapi.json",
    description=settings.descriprion,
    version=settings.version,
    openapi_tags=settings.openapi_tags,
    swagger_ui_parameters={"defaultModelsExpandDepth": -1}
        )


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(api_router, prefix=settings.api_v1_str)
