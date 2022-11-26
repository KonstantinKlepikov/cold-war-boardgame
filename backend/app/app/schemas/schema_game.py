from typing import Literal, Optional, List, Union
from pydantic import BaseModel, NonNegativeInt, conint
from app.schemas import schema_cards
from app.constructs import Phase


class GameSteps(BaseModel):
    """Game steps schema
    """
    game_turn: NonNegativeInt = 0
    turn_phase: Union[Phase, None] = None
    is_game_end: bool = False

    class Config:
        schema_extra = {
            "example": {
                "game_turn": 0,
                "turn_phase": "briefing",
                "is_game_end": False,
            }
        }


class PlayerAgentCard(BaseModel):
    is_dead: bool = False
    is_in_play: bool = False
    is_in_vacation: bool = False
    is_revealed: bool = False
    name: str

    class Config:
        schema_extra = {
            "example": {
                "is_dead": False,
                "is_in_play": True,
                "is_in_vacation": False,
                "is_revealed": False,
                "name": "Master Spy",
                }
            }


class PlayerCards(BaseModel):
    """Player cards schema
    """
    agent_cards: List[PlayerAgentCard]
    group_cards: List[schema_cards.Card] = []
    objective_cards: List[schema_cards.Card] = []


class GameDeck(BaseModel):
    """Game decks
    """
    deck_len: NonNegativeInt = 0
    deck_top: List[schema_cards.Card] = []
    deck_bottom: List[schema_cards.Card] = []
    pile: List[schema_cards.Card] = []

    class Config:
        schema_extra = {
            "example": {
                "deck_len": 0,
                "deck_top": [
                    {"name": "Some card"},
                ],
                "deck_bottom": [
                    {"name": "Other card"},
                ],
                "pile": [
                    {"name": "Ukranian War"},
                    {"name": "Something Else"},
                ],
            }
        }


class GameDecks(BaseModel):
    """Game cards of all decs
    """
    group_deck: GameDeck = GameDeck(deck_len=24)
    objective_deck: GameDeck = GameDeck(deck_len=21)


class Player(BaseModel):
    """Player current data schema
    """
    has_priority: Optional[bool] = None
    is_bot: Optional[bool] = None
    score: conint(ge=0, le=100) = 0
    faction: Optional[Literal['kgb', 'cia']] = None
    player_cards: PlayerCards
    login: Optional[str] = None

    class Config:
        schema_extra = {
            "example": {
                "has_priority": True,
                "is_bot": False,
                "score": 0,
                "faction": "kgb",
                "player_cards": {
                    "agent_cards": [
                        {"name": "Master Spy"},
                    ],
                    "group_cards": [
                        {"name": "Director"},
                    ],
                    "objective_cards": [
                        {
                            "is_dead": False,
                            "is_in_play": True,
                            "is_in_vacation": False,
                            "is_revealed": False,
                            "name": "Master Spy",
                            },
                        ],
                    },
                "login": "DonaldTrump",
                }
            }


class CurrentGameData(BaseModel):
    """Read or write current game data
    """
    game_steps: GameSteps = GameSteps()
    players: List[Player]
    game_decks: GameDecks = GameDecks()
