from typing import Optional
from pydantic import BaseModel, PositiveInt, NonNegativeInt
from app.constructs import (
    Factions, Phases, Icons, ObjectiveAbilities, GroupFactions,
    Agents, Groups, Objectives
        )


class Agent(BaseModel):
    """Agent card scheme
    """
    id: Agents
    agenda_lose: str
    agenda_win: str
    initiative: PositiveInt

    class Config:
        fields = {'id': 'name'}
        schema_extra = {
            "example": {
                "id": "Master Spy",
                "agenda_lose": "You claim the objective immediately",
                "agenda_win": "Your opponent claims the objective immediately",
                "initiative": 1,
                }
            }

class Group(BaseModel):
    """Group card scheme
    """
    id: Groups
    faction: GroupFactions
    influence: PositiveInt
    power: str

    class Config:
        fields = {'id': 'name'}
        schema_extra = {
            "example": {
                "id": "Guerilla",
                "faction": "Military",
                "influence": 1,
                "power": "Send any other group card, whether "
                         "ready or mobilized, to the discard pile",
                }
            }

class Objective(BaseModel):
    """Objective card scheme
    """
    id: Objectives
    bias_icons: list[Icons] #  TODO:  is a combination of 4 ids
    population: PositiveInt
    special_ability_phase: Optional[Phases]
    special_ability_text: Optional[str]
    stability: PositiveInt
    victory_points: NonNegativeInt

    class Config:
        fields = {'id': 'name'}
        schema_extra = {
            "example": {
                "id": "Egypt",
                "bias_icons": [
                    "Political",
                    "Economic",
                    "Media",
                    "Military"
                    ],
                "population": 4,
                "special_ability_phase": None,
                "special_ability_text": None,
                "stability": 11,
                "victory_points": 20
                }
            }

class Rules(BaseModel):
    """Game rules scheme
    """
    # TODO: fill me from yaml

class StaticGameData(BaseModel):
    """Static game data scheme
    """
    agents: dict[str, Agent]
    groups: dict[str, Group]
    objectives: dict[str, Objective]
    # rules: Rules # TODO: get from db
    phases: list[Phases] = Phases.get_values()
    player_factions: list[Factions] = Factions.get_values()
    objectives_ids: list[Objectives] = Objectives.get_values()
    objectie_icons: list[Icons] = Icons.get_values()
    objectives_ablilities: list[ObjectiveAbilities] = ObjectiveAbilities.get_values()
    groups_ids: list[Groups] = Groups.get_values()
    groups_factions: list[GroupFactions] = GroupFactions.get_values()
    agents_ids: list[Agents] = Agents.get_values()
