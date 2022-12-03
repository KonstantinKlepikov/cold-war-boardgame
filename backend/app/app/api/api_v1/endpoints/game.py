from typing import Union, Literal
from fastapi import status, Depends, APIRouter, Query
from app.schemas import schema_user
from app.crud import crud_game
from app.core import security_user
from app.constructs import Priority, Faction
from app.config import settings
from app.core import game_logic


router = APIRouter()


@router.post(
    "/create",
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
    obj_in = game_logic.make_game_data(user.login)
    crud_game.game.create_new_game(obj_in)
    crud_game.game.deal_and_shuffle_decks(user.login)


@router.patch(
    "/preset",
    status_code=status.HTTP_200_OK,
    responses=settings.ACCESS_ERRORS,
    summary='Preset faction and priority before game start',
    response_description="Ok. Data is changed if not seted before."
        )
def preset(
    faction: Faction = Query(
        title="Preset faction",
            ),
    priority: Priority = Query(
        default=Priority.RANDOM,
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
    response_description="Ok.",
    deprecated=True,
        )
def next_turn_phase(
    turn: Union[Literal['push', ], None] = None,
    phase: Union[Literal['push', ], None] = None,
    user: schema_user.User = Depends(security_user.get_current_active_user),
        ) -> None:
    """Change turn number or phase to next
    """
    return None


@router.patch(
    "/next_turn",
    status_code=status.HTTP_200_OK,
    responses=settings.NEXT_ERRORS,
    summary='Go to next turn',
    response_description="Ok.",
        )
def next_turn(
    user: schema_user.User = Depends(security_user.get_current_active_user),
        ) -> None:
    """Change turn number to next
    """
    crud_game.game.set_next_turn(user.login)


@router.patch(
    "/next_phase",
    status_code=status.HTTP_200_OK,
    responses=settings.NEXT_ERRORS,
    summary='Go to next phase',
    response_description="Ok.",
        )
def next_phase(
    user: schema_user.User = Depends(security_user.get_current_active_user),
        ) -> None:
    """Change phase to next
    """
    crud_game.game.set_next_phase(user.login)
