from fastapi import status, Depends, APIRouter, HTTPException
from app.schemas import schema_cards, schema_user, schema_game
from app.crud import crud_card, crud_game
from app.core import security_user
from app.config import settings


router = APIRouter()


@router.get(
    "/static",
    response_model=schema_cards.GameCards,
    status_code=status.HTTP_200_OK,
    summary='Static game data',
    response_description="OK. As response you recieve static game data."
        )
def get_static_data() -> schema_cards.GameCards:
    """Get all static game data (cards data).
    """
    db_cards = crud_card.cards.get_all_cards()
    return schema_cards.GameCards(**db_cards)


@router.post(
    "/current",
    response_model=schema_game.CurrentGameData,
    status_code=status.HTTP_200_OK,
    responses=settings.CURRENT_DATA_ERRORS,
    summary='Current game data',
    response_description="OK. As response you recieve current game data."
        )
def get_current_data(
    user: schema_user.User = Depends(security_user.get_current_active_user)
        ) -> schema_game.CurrentGameData:
    """Get all current game data (game statement) for current user.
    """
    data = crud_game.game.get_current_game_data(user.login)
    if data:
        return data.to_mongo().to_dict()
    else:
        raise HTTPException(
            status_code=404,
            detail="Cant find current game data in db. For start "
                   "new game use /game/create endpoint",
                )
