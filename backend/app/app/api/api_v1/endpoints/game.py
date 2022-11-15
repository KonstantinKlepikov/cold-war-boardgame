from fastapi import status, Depends, APIRouter, Query
from app.schemas import schema_user, schema_game
from app.crud import crud_game
from app.core import game_data, security_user
from app.config import settings


router = APIRouter()


@router.post(
    "/create",
    response_model=schema_game.CurrentGameData,
    status_code=status.HTTP_201_CREATED,
    responses=settings.ACCESS_ERRORS,
    summary='Create new game',
    response_description="Created. New game object created in db."
        )
def create_new_game(
    user: schema_user.User = Depends(security_user.get_current_active_user)
        ) -> None:
    """Create new game.
    """
    obj_in = game_data.make_game_data(user.login)
    crud_game.game.create_new_game(obj_in)


@router.patch(
    "/preset",
    status_code=status.HTTP_200_OK,
    responses=settings.ACCESS_ERRORS,
    summary='Preset faction and priority before game start',
    response_description="Ok. Data is changed if not seted before."
        )
def preset(
    faction: crud_game.Faction = Query(
        title="Preset faction",
            ),
    priority: crud_game.Priority = Query(
        default=crud_game.Priority.RANDOM,
        title="Preset priority",
        description="- true - set priority to player\n"
                    "- false - set priority to bot\n"
                    "- random - set priority at random\n"
            ),
    user: schema_user.User = Depends(security_user.get_current_active_user),
        ) -> None:
    """Preset faction and/or priotity for game
    if not seted before in this game
    """
    crud_game.game.set_faction(user.login, faction)
    crud_game.game.set_priority(user.login, priority)


@router.post(
    "/turn/next",
    status_code=status.HTTP_200_OK,
    responses=settings.TURN_ERRORS,
    summary='Go to next turn',
    response_description="Ok."
        )
def next_turn(
    user: schema_user.User = Depends(security_user.get_current_active_user)
        ) -> None:
    """Change turn number to next
    """
    data = crud_game.game.get_current_game_data(user.login)


@router.post(
    "/turn/phase/next",
    status_code=status.HTTP_200_OK,
    responses=settings.PHASE_ERRORS,
    summary='Go to next phase of turn',
    response_description="Ok."
        )
def next_phase(
    user: schema_user.User = Depends(security_user.get_current_active_user)
        ) -> None:
    """Change phase of turn
    """
    data = crud_game.game.get_current_game_data(user.login)
