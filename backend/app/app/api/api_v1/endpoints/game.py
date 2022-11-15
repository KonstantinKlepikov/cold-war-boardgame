from typing import Union, Literal
from fastapi import status, Depends, APIRouter, Query, HTTPException
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


@router.patch(
    "/next",
    status_code=status.HTTP_200_OK,
    responses=settings.NEXT_ERRORS,
    summary='Go to next turn or/and phase',
    response_description="Ok."
        )
def next_turn(
    turn: Union[Literal['push', ], None] = None,
    phase: Union[Literal['push', ], None] = None,
    user: schema_user.User = Depends(security_user.get_current_active_user),
        ) -> None:
    """Change turn number or phase to next
    """
    if not turn and not phase:
        raise HTTPException(
            status_code=400,
            detail='Need at least one query parameter for this request'
                )

    crud_game.game.set_next_turn_phase(
        user.login, bool(turn), bool(phase)
            )
