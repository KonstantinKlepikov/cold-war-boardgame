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
    game_proc = crud_game.game.get_game_processor(user.login)
    game_proc = crud_game.game.deal_and_shuffle_decks(game_proc)


@router.patch(
    "/preset",
    status_code=status.HTTP_200_OK,
    responses=settings.ACCESS_ERRORS,
    summary='Preset faction and priority before game start',
    response_description="Ok. Data is changed if not seted before.",
    deprecated=True,
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
    game_proc = crud_game.game.get_game_processor(user.login)
    game_proc = crud_game.game.set_faction(faction, game_proc)
    game_proc = crud_game.game.set_priority(priority, game_proc)


@router.patch(
    "/preset/faction",
    status_code=status.HTTP_200_OK,
    responses=settings.NEXT_ERRORS,
    summary='Preset faction before game start',
    response_description="Ok. Faction is setted."
        )
def preset_faction(
    q: Faction = Query(
        title="Preset faction",
            ),
    user: schema_user.User = Depends(security_user.get_current_active_user),
        ) -> None:
    """Preset faction of player
    """
    game_proc = crud_game.game.get_game_processor(user.login)
    game_proc = crud_game.game.set_faction(q, game_proc)


@router.patch(
    "/preset/priority",
    status_code=status.HTTP_200_OK,
    responses=settings.NEXT_ERRORS,
    summary='Preset priority before game start',
    response_description="Ok. Priority is setted.",
    deprecated=True,
        )
def preset_priority(
    q: Priority = Query(
        title="Preset priority",
        description="- true - set priority to player\n"
                    "- false - set priority to bot\n"
                    "- random - set priority at random\n"
            ),
    user: schema_user.User = Depends(security_user.get_current_active_user),
        ) -> None:
    """Preset priotity of player
    """
    game_proc = crud_game.game.get_game_processor(user.login)
    game_proc = crud_game.game.set_priority(q, game_proc)


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
    game_proc = crud_game.game.get_game_processor(user.login)
    game_proc = crud_game.game.set_next_turn(game_proc)


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
    game_proc = crud_game.game.get_game_processor(user.login)
    game_proc = crud_game.game.set_next_phase(game_proc)
    game_proc = crud_game.game.set_phase_conditions_after_next(game_proc)
