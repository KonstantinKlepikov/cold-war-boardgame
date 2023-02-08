from fastapi import status, Depends, APIRouter, Query, HTTPException
from app.schemas.schema_user import User
from app.crud import crud_game_current
from app.core import security_user, logic
from app.constructs import Factions, Groups
from app.config import settings


router = APIRouter()


@router.post(
    "/create",
    status_code=status.HTTP_201_CREATED,
    responses=settings.ACCESS_ERRORS,
    summary='Create new game',
    response_description="Created. New game object created in db."
        )
def create_new_game(
    user: User = Depends(security_user.get_current_active_user)
        ) -> None:
    """Create new game.
    """
    crud_game_current.game.create_new_game(user.login)


@router.patch(
    "/preset/faction",
    status_code=status.HTTP_200_OK,
    responses=settings.NEXT_ERRORS,
    summary='Preset faction before game start',
    response_description="Ok. Faction is setted."
        )
def preset_faction(
    q: Factions = Query(
        title="Preset faction",
            ),
    user: User = Depends(security_user.get_current_active_user),
        ) -> None:
    """Preset faction of player
    """
    game_logic = logic.GameLogic(
        crud_game_current.game.get_last_game(user.login)
            ).set_faction(q)
    crud_game_current.game.save_game_processor(game_logic)


@router.patch(
    "/next_turn",
    status_code=status.HTTP_200_OK,
    responses=settings.NEXT_ERRORS,
    summary='Go to next turn',
    response_description="Ok.",
        )
def next_turn(
    user: User = Depends(security_user.get_current_active_user),
        ) -> None:
    """Change turn number to next
    """
    game_logic = logic.GameLogic(
        crud_game_current.game.get_last_game(user.login)
            ).set_next_turn()
    crud_game_current.game.save_game_processor(game_logic)


@router.patch(
    "/next_phase",
    status_code=status.HTTP_200_OK,
    responses=settings.NEXT_ERRORS,
    summary='Go to next phase',
    response_description="Ok.",
        )
def next_phase(
    user: User = Depends(security_user.get_current_active_user),
        ) -> None:
    """Change phase to next
    """
    game_logic = logic.GameLogic(
        crud_game_current.game.get_last_game(user.login)
            ).chek_phase_conditions_before_next() \
            .set_next_phase() \
            .set_phase_conditions_after_next()
    crud_game_current.game.save_game_processor(game_logic)


@router.patch(
    "/phase/briefing/analyst_look",
    status_code=status.HTTP_200_OK,
    responses=settings.NEXT_ERRORS,
    summary='Look top three cards of group deck with analist ability',
    response_description="Ok. Data is changed",
        )
def analyst_get(
    user: User = Depends(security_user.get_current_active_user),
        ) -> None:
    """Look top three cards of group deck and change current game data
    """
    game_logic = logic.GameLogic(
        crud_game_current.game.get_last_game(user.login)
            ).play_analyst_for_look_the_top()
    crud_game_current.game.save_game_processor(game_logic)


@router.patch(
    "/phase/briefing/analyst_arrange",
    status_code=status.HTTP_200_OK,
    responses=settings.NEXT_ERRORS,
    summary='Arrange top three cards of group deck with analist ability',
    response_description="Ok. Data is changed",
        )
def analyst_arrnge(
    top: list[Groups],
    user: User = Depends(security_user.get_current_active_user),
        ) -> None:
    """Arrange top three cards of group deck and change current game data
    """
    if len(top) != 3:
        raise HTTPException(
            status_code=409,
            detail="You must give exactly tree cards id "
                   f"in list to rearrange top deck. You given {len(top)}."
                )
    game_logic = logic.GameLogic(
        crud_game_current.game.get_last_game(user.login)
            ).play_analyst_for_arrange_the_top(top)
    crud_game_current.game.save_game_processor(game_logic)
