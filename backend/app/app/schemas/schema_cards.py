from typing import List, Literal, Set, Optional
from pydantic import BaseModel, PositiveInt, NonNegativeInt


class CardName(BaseModel):
    """Base schema for cards
    """
    name: str

    class Config:
        schema_extra = {
            "example": {
                "name": "Master Spy",
                }
            }


class AgentCard(CardName):
    """Agent card schema
    """
    agenda_lose: str
    agenda_win: str
    initiative: PositiveInt

    class Config:
        schema_extra = {
            "example": {
                "name": "Master Spy",
                "agenda_lose": "You claim the objective immediately",
                "agenda_win": "Your opponent claims the objective immediately",
                "initiative": 1,
                }
            }


class GroupCard(CardName):
    """Group card schema
    """
    faction: Literal[
        'Military', 'Economic', 'Political', 'Government', 'Media',
            ]
    influence: PositiveInt
    power: str

    class Config:
        schema_extra = {
            "example": {
                "name": "Guerilla",
                "faction": "Military",
                "influence": 1,
                "power": "Send any other group card, whether "
                         "ready or mobilized, to the discard pile",
                }
            }


class ObjectiveCard(CardName):
    """Objective card schema
    """

    bias_icons: Set[Literal[
        'Economic', 'Military', 'Media', 'Political',
            ]]
    population: PositiveInt
    special_ability: Optional[str]
    stability: PositiveInt
    victory_points: NonNegativeInt

    class Config:
        schema_extra = {
            "example": {
                "name": "Egypt",
                "bias_icons": [
                    "Political",
                    "Economic",
                    "Media",
                    "Military"
                    ],
                "population": 4,
                "special_ability": None,
                "stability": 11,
                "victory_points": 20
                }
            }


class GameCards(BaseModel):
    """Agents, group and objective cards schema
    """
    agent_cards: List[AgentCard]
    group_cards: List[GroupCard]
    objective_cards: List[ObjectiveCard]
