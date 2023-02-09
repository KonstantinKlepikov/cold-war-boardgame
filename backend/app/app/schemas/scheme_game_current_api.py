from typing import Optional
from pydantic import BaseModel, conint
from app.constructs import (
    Phases, Agents, HiddenGroups, Groups, Objectives, Factions,
    HiddenObjectives, HiddenAgents, AwaitingAbilities
        )


class Steps(BaseModel):
    """Phases and turns of game
    """
    game_turn: int
    turn_phase: Optional[Phases]
    turn_phases_left: list[Phases]
    is_game_ends: bool
    # is_game_starts: bool


class PlayerAgents(BaseModel):
    """Players agents
    """
    in_headquarter: list[Agents]
    terminated: list[Agents]
    agent_x: Optional[Agents]
    on_leave: list[Agents]


class OpponentAgents(BaseModel):
    """Opponents agents
    """
    in_headquarter: list[HiddenAgents]
    terminated: list[Agents]
    agent_x: Optional[HiddenAgents]
    on_leave: list[Agents]


class BaseUser(BaseModel):
    """Base user
    """
    login: str
    score: conint(ge=0)
    faction: Optional[Factions]
    has_balance: bool
    has_domination: bool
    awaiting_abilities: list[AwaitingAbilities]


class Player(BaseUser):
    """Player
    """
    agents: PlayerAgents


class Opponent(BaseUser):
    """Opponent processor
    """
    agents: OpponentAgents


class Users(BaseModel):
    """Users
    """
    player: Player
    opponent: Opponent


class GroupsDeck(BaseModel):
    """Groups
    """
    pile: list[Groups]
    deck: list[HiddenGroups]


class ObjectivesDeck(BaseModel):
    """Objectives"""
    pile: list[Objectives]
    mission: Optional[HiddenObjectives]
    deck: list[HiddenObjectives]


class Decks(BaseModel):
    """Decks
    """
    groups: GroupsDeck
    objectives: ObjectivesDeck


class CurrentGameDataApi(BaseModel):
    """Current game data
    """
    steps: Steps
    players: Users
    decks: Decks
