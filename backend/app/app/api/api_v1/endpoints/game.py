from fastapi import status, Depends, APIRouter, Query, HTTPException
from typing import Optional
from app.schemas.scheme_user import User
from app.crud import crud_game_current
from app.core import security_user, logic
from app.constructs import Factions, Groups, Agents
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
    "/preset",
    status_code=status.HTTP_200_OK,
    responses=settings.NEXT_ERRORS,
    summary='Preset faction before game start and deal a mission card',
    response_description="Ok. Faction is set."
        )
def preset(
    q: Factions = Query(
        title="Preset faction",
            ),
    user: User = Depends(security_user.get_current_active_user),
        ) -> None:
    """Preset faction of player. Next deal a mission card.
    """
    game_logic = logic.GameLogic(
        crud_game_current.game.get_last_game(user.login)
            ).set_faction(q).set_mission_card()
    crud_game_current.game.save_game_logic(game_logic)


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
    crud_game_current.game.save_game_logic(game_logic)


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
    crud_game_current.game.save_game_logic(game_logic)


@router.patch(
    "/phase/briefing/analyst_look",
    status_code=status.HTTP_200_OK,
    responses=settings.NEXT_ERRORS,
    summary='Look top three cards of group deck with analyst ability',
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
    crud_game_current.game.save_game_logic(game_logic)


@router.patch(
    "/phase/briefing/analyst_arrange",
    status_code=status.HTTP_200_OK,
    responses=settings.NEXT_ERRORS,
    summary='Arrange top three cards of group deck with analyst ability',
    response_description="Ok. Data is changed",
        )
def analyst_arrange(
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
    crud_game_current.game.save_game_logic(game_logic)


@router.patch(
    "/phase/planning/agent_x",
    status_code=status.HTTP_200_OK,
    responses=settings.NEXT_ERRORS,
    summary='Set agent X for current turn',
    response_description="Ok. Agent X is set",
        )
def agent_x(
    q: Agents = Query(title="Agent X id"),
    user: User = Depends(security_user.get_current_active_user),
        ) -> None:
    """Set agent X
    Args:
        q (Agents): agent for current turn
    """
    game_logic = logic.GameLogic(
        crud_game_current.game.get_last_game(user.login)
            ).set_agent_x(q)
    crud_game_current.game.save_game_logic(game_logic)


@router.patch(
    "/influence_struggle/recruit",
    status_code=status.HTTP_200_OK,
    responses=settings.NEXT_ERRORS,
    summary='Recruit a group in a influence-struggle subgame',
    response_description="Ok. Group is recruited",
        )
def recruit(user: User = Depends(security_user.get_current_active_user),
    ) -> None:
    """The player draw a group card from top of group deck.
    This group is recruited by this player.
    """
    game_logic = logic.GameLogic(
        crud_game_current.game.get_last_game(user.login)
            ).recruit_group()
    crud_game_current.game.save_game_logic(game_logic)


@router.patch(
    "/influence_struggle/activate",
    status_code=status.HTTP_200_OK,
    responses=settings.NEXT_ERRORS,
    summary='Activate a group in a influence-struggle subgame',
    response_description="Ok. Abilitie is activated",
        )
def activate(
    source: Groups,
    target: Optional[Groups],
    user: User = Depends(security_user.get_current_active_user),
    ) -> None:
    """Activate abilitie of choosen group card.

    Args:
        source (Groups): Id of source group.
                         Group must be owned by player and must be active.
        target (Optional[Groups]): Id of target group.
                                   Not all group requred targeting of
                                   another groups in action.
    """
    raise HTTPException(
        status_code=409,
        detail="Not implemented."
            )


@router.patch(
    "/influence_struggle/pass",
    status_code=status.HTTP_200_OK,
    responses=settings.NEXT_ERRORS,
    summary='Pass in a influence-struggle subgame',
    response_description="Ok. Abilitie is activated",
        )
def passing(
    user: User = Depends(security_user.get_current_active_user),
    ) -> None:
    """Pass in a influence-struggle subgame.
    """
    game_logic = logic.GameLogic(
        crud_game_current.game.get_last_game(user.login)
            ).pass_influence()
    crud_game_current.game.save_game_logic(game_logic)


@router.patch(
    "/influence_struggle/nuclear_escalation",
    status_code=status.HTTP_200_OK,
    responses=settings.NEXT_ERRORS,
    summary='Play nuclear escalation abilitie',
    response_description="Ok. Abilitie is used",
        )
def nuclear_escalation(
    user: User = Depends(security_user.get_current_active_user),
    ) -> None:
    """Activate nuclear escalation abilitie.
    """
    game_logic = logic.GameLogic(
        crud_game_current.game.get_last_game(user.login)
            ).nuclear_escalation()
    crud_game_current.game.save_game_logic(game_logic)
