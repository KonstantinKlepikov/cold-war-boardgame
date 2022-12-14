from typing import Literal, Optional, List, Union
from pydantic import BaseModel, NonNegativeInt, NonPositiveInt, conint
from app.constructs import Phase


class GameSteps(BaseModel):
    """Game steps
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


class GameStepsDb(GameSteps):
    """Game steps in db
    """
    turn_phases_left: List[str] = []

    class Config:
        schema_extra = {
            "example": {
                "game_turn": 0,
                "turn_phase": "briefing",
                "is_game_end": False,
                "turn_phases_left": [
                    "detente",
                    ],
            }
        }


class PlayerAgentCard(BaseModel):
    """Agent card owned by player
    """
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


class PlayerGroupOrObjectivreCard(BaseModel):
    """Known or own by player nonagent card.
    Position here - is any nonegative integer from 0 to len of deck.
    This represent card position in deck from top to bottom.
    """
    is_in_deck: bool = True
    is_in_play: bool = False
    is_active: Optional[bool]
    pos_in_deck: Optional[NonPositiveInt]
    name: str

    class Config:
        schema_extra = {
            "example": {
                "is_in_deck": True,
                "is_in_play": False,
                "is_active": None,
                "pos_in_deck": 0,
                "name": "Master Spy",
                }
            }


class TopDeck(BaseModel):
    """List of id of top cards of any deck. The top card
    is a last card in list.
    """
    top_cards: List[str]

    class Config:
        schema_extra = {
            "example": {
                "top_cards": [
                    "Master Spy",
                    ],
                }
            }


class PlayerCards(BaseModel):
    """Player cards
    """
    agent_cards: List[PlayerAgentCard]
    group_cards: List[PlayerGroupOrObjectivreCard] = []
    objective_cards: List[PlayerGroupOrObjectivreCard] = []


class GameDeck(BaseModel):
    """Game deck
    """
    deck_len: NonNegativeInt = 0
    pile: List[str] = []

    class Config:
        schema_extra = {
            "example": {
                "deck_len": 0,
                "pile": [
                    "Ukranian War", "Something Else",
                ],
            }
        }


class GameDeckDb(GameDeck):
    """Game deck in db
    """
    deck: List[str] = []

    class Config:
        schema_extra = {
            "example": {
                "deck_len": 0,
                "pile": [
                    "Ukranian War", "Something Else",
                ],
                "deck": [
                    "Some Great Card",
                ],
            }
        }


class GameDecks(BaseModel):
    """Game decks and mission card
    """
    group_deck: GameDeck = GameDeck()
    objective_deck: GameDeck = GameDeck()
    mission_card: Optional[str] = None


class Player(BaseModel):
    """Player current data
    """
    has_priority: Optional[bool] = None
    is_bot: Optional[bool] = None
    score: conint(ge=0, le=100) = 0
    faction: Optional[Literal['kgb', 'cia']] = None
    player_cards: PlayerCards
    login: Optional[str] = None
    abilities: List[str] = []

    class Config:
        schema_extra = {
            "example": {
                "has_priority": True,
                "is_bot": False,
                "score": 0,
                "faction": "kgb",
                "player_cards": {
                    "agent_cards": [
                        {
                            "is_dead": False,
                            "is_in_play": True,
                            "is_in_vacation": False,
                            "is_revealed": False,
                            "name": "Master Spy",
                            },
                    ],
                    "group_cards": [
                        {
                            "is_in_deck": True,
                            "is_in_play": False,
                            "is_active": True,
                            "position": 0,
                            "name": "Militia",
                            },
                    ],
                    "objective_cards": [
                        {
                            "is_in_deck": False,
                            "is_in_play": True,
                            "is_active": False,
                            "position": None,
                            "name": "Egypt",
                            },
                        ],
                    },
                "login": "DonaldTrump",
                "abilities": [
                    "Analist",
                    ],
                }
            }


class CurrentGameData(BaseModel):
    """Current game data
    """
    game_steps: GameSteps = GameSteps()
    players: List[Player]
    game_decks: GameDecks = GameDecks()
