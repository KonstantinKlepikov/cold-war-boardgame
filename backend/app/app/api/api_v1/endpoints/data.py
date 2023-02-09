from fastapi import status, Depends, APIRouter, HTTPException
from app.schemas.scheme_user import User
from app.schemas.scheme_game_current_api import CurrentGameDataApi
from app.schemas.scheme_game_static import StaticGameData
from app.crud import crud_game_static, crud_game_current
from app.core import security_user, logic
from app.config import settings


router = APIRouter()


@router.get(
    "/static",
    response_model=StaticGameData,
    status_code=status.HTTP_200_OK,
    summary='Static game data',
    response_description="OK. As response you recieve static game data."
        )
def get_static_data() -> StaticGameData:
    """Get all static game data.
    """
    return crud_game_static.static.get_static_game_data()


@router.post(
    "/current",
    response_model=CurrentGameDataApi,
    status_code=status.HTTP_200_OK,
    responses=settings.CURRENT_DATA_ERRORS,
    summary='Current game data',
    response_description="OK. As response you recieve current game data."
        )
def get_current_data(
    user: User = Depends(security_user.get_current_active_user)
        ) -> CurrentGameDataApi:
    """Get all current game data (game statement) for current user.
    """
    current = crud_game_current.game.get_last_game(user.login)

    if current:
        return logic.GameLogic(current).get_api_scheme()
    else:
        raise HTTPException(
            status_code=404,
            detail="Cant find current game data in db. For start "
                   "new game use /game/create endpoint",
                )
