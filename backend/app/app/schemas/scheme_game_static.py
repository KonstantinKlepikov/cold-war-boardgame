from typing import Optional
from pydantic import BaseModel, PositiveInt, NonNegativeInt
from app.constructs import (
    Factions, Phases, Icons, ObjectiveAbilities, GroupFactions,
    Agents, Groups, Objectives
        )


class AgentId(BaseModel):
    """Agent card id scheme
    """
    id: Agents


class GroupId(BaseModel):
    """Group card id scheme
    """
    id: Groups


class ObjectiveId(BaseModel):
    """Objective card id scheme
    """
    id: Objectives


class Agent(AgentId):
    """Agent card scheme
    """
    agenda_lose: str
    agenda_win: str
    initiative: PositiveInt

    class Config:
        schema_extra = {
            "example": {
                "id": "Master Spy",
                "agenda_lose": "You claim the objective immediately",
                "agenda_win": "Your opponent claims the objective immediately",
                "initiative": 1,
                }
            }

class Group(GroupId):
    """Group card scheme
    """
    faction: GroupFactions
    influence: PositiveInt
    power: str

    class Config:
        schema_extra = {
            "example": {
                "id": "Guerilla",
                "faction": "Military",
                "influence": 1,
                "power": "Send any other group card, whether "
                         "ready or mobilized, to the discard pile",
                }
            }

class Objective(ObjectiveId):
    """Objective card scheme
    """
    bias_icons: set[Icons] #  TODO:  is a combination of 4 ids
    population: PositiveInt
    special_ability_phase: Optional[Phases]
    special_ability_text: Optional[str]
    stability: PositiveInt
    victory_points: NonNegativeInt

    class Config:
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

class StaticGameData(BaseModel):
    """Static game data scheme
    """
    agents: list[Agent] # TODO: fill data here
    groups: list[Group]
    objectives: list[Objective]
    rules: Rules
    phases: list[Phases] = Phases.get_values() # TODO: init this in scheme
    player_factions: list[Factions] = Factions.get_values()
    objectives_ids: list[Objectives] = Objectives.get_values()
    objectie_icons: list[Icons] = Icons.get_values()
    objectives_ablilities: list[ObjectiveAbilities] = ObjectiveAbilities.get_values()
    groups_ids: list[Groups] = Groups.get_values()
    groups_factions: list[GroupFactions] = GroupFactions.get_values()
    agents_ids: list[Agents] = Agents.get_values()
