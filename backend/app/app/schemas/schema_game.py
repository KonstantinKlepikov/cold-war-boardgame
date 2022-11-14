from typing import Literal, Optional, List
from pydantic import BaseModel, NonNegativeInt, conint
from app.schemas import schema_cards, schema_user


class GameSteps(BaseModel):
    """Game steps schema
    """
    game_turn: NonNegativeInt = 0
    turn_phase: Optional[Literal[
        'briefing', 'planning', 'influence_struggle',
        'ceasefire', 'debriefing', 'detente',
    ]] = None

    class Config:
        schema_extra = {
            "example": {
                "game_turn": 0,
                "turn_phase": "briefing",
            }
        }


class PlayerAgentCard(BaseModel):
    is_dead: bool = False
    is_in_play: bool = False
    is_in_vacation: bool = False
    is_revealed: bool = False
    agent_card: schema_cards.CardName

    class Config:
        schema_extra = {
            "example": {
                "is_dead": False,
                "is_in_play": True,
                "is_in_vacation": False,
                "is_revealed": False,
                "agent_card":
                    {"name": "Master Spy"},
                }
            }


class PlayerCards(BaseModel):
    """Player cards schema
    """
    agent_cards: List[PlayerAgentCard]
    group_cards: List[schema_cards.CardName] = []
    objective_cards: List[schema_cards.CardName] = []


class GameDeck(BaseModel):
    """Game decks
    """
    deck_len: NonNegativeInt = 0
    pile_len: NonNegativeInt = 0
    pile: List[schema_cards.CardName] = []

    class Config:
        schema_extra = {
            "example": {
                "deck_len": 0,
                "pile_len": 0,
                "pile": [
                    {"name": "Master Spy"},
                    {"name": "Something Else"},
                ]
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
    user: Optional[schema_user.UserBase] = None

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
                            "agent_card":
                                {"name": "Master Spy"},
                            },
                        ],
                    },
                "user": {
                    "login": "DonaldTrump",
                    }
                }
            }


class CurrentGameData(BaseModel):
    """Read or write current game data
    """
    game_steps: GameSteps = GameSteps()
    players: List[Player]
    game_decks: GameDecks = GameDecks()
