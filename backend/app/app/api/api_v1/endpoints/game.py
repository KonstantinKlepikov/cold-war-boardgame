from fastapi import status, Depends, APIRouter, Query, HTTPException
from app.schemas import schema_user, schema_game
from app.crud import crud_game
from app.core import security_user, processor_game
from app.constructs import Faction
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
    user: schema_user.User = Depends(security_user.get_current_active_user)
        ) -> None:
    """Create new game.
    """
    obj_in = processor_game.make_game_data(user.login)
    crud_game.game.create_new_game(obj_in)
    crud_game.game.get_game_processor(user.login) \
        .deal_and_shuffle_decks() \
        .flush().save()


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
    crud_game.game.get_game_processor(user.login) \
        .set_faction(q) \
        .flush().save()


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
    crud_game.game.get_game_processor(user.login) \
        .set_next_turn() \
        .flush().save()


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
    crud_game.game.get_game_processor(user.login) \
        .chek_phase_conditions_before_next() \
        .set_next_phase() \
        .set_phase_conditions_after_next() \
        .flush().save()


@router.patch(
    "/phase/briefing/analyst_look",
    status_code=status.HTTP_200_OK,
    responses=settings.NEXT_ERRORS,
    summary='Look top three cards of group deck with analist ability',
    response_description="Ok. Data is changed",
        )
def analyst_get(
    user: schema_user.User = Depends(security_user.get_current_active_user),
        ) -> schema_game.TopDeck:
    """Look top three cards of group deck and change current game data
    """
    proc = crud_game.game.get_game_processor(user.login) \
        .play_analyst_for_look_the_top()

    proc.flush().save()

    return { "top_cards": proc.G.c.group_deck.temp_group }


@router.patch(
    "/phase/briefing/analyst_arrange",
    status_code=status.HTTP_200_OK,
    responses=settings.NEXT_ERRORS,
    summary='Arrange top three cards of group deck with analist ability',
    response_description="Ok. Data is changed",
        )
def analyst_arrnge(
    top: schema_game.TopDeck,
    user: schema_user.User = Depends(security_user.get_current_active_user),
        ) -> None:
    """Arrange top three cards of group deck and change current game data
    """
    if len(top.top_cards) != 3:
        raise HTTPException(
            status_code=409,
            detail="You must give exactly tree cards id "
                   f"in list to rearrange top deck. You given {len(top.top_cards)}."
                )
    crud_game.game.get_game_processor(user.login) \
        .play_analyst_for_arrange_the_top(top.top_cards) \
        .flush().save()
