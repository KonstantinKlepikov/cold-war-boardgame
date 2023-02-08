from fastapi import APIRouter
from app.api.api_v1.endpoints import user, data, game


api_router = APIRouter()
api_router.include_router(
    user.router, prefix="/user", tags=['user', ]
        )
api_router.include_router(
    data.router, prefix="/game/data", tags=['game_data', ]
        )
api_router.include_router(
    game.router, prefix="/game", tags=['game', ]
        )
