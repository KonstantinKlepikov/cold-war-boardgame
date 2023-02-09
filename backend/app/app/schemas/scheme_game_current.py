from typing import Optional
from pydantic import BaseModel, conint, Field
from app.constructs import (
    Phases, Agents, HiddenGroups, Groups, Objectives, Factions,
    HiddenObjectives, HiddenAgents, AwaitingAbilities
        )
from collections import deque
from bgameb import Steps, Player, Card, Deck, Game, Dice


class StepsProcessor(Steps):
    """Steps turns processor
    """
    id: str = Field(exclude=True, default='steps')
    game_turn: int
    turn_phase: Optional[Phases]
    turn_phases_left: list[Phases]
    is_game_ends: bool


class AgentInPlayProcessor(Card):
    """Agent card processor
    """
    id: Agents = Field(..., alias='name')
    is_in_headquarter: bool = True
    is_terminated: bool = False
    is_on_leave: bool = False
    is_agent_x: bool = False

    class Config(Card.Config):
        allow_population_by_field_name = True
        fields = {
            'is_active': {'exclude': True},
            'side': {'exclude': True},
            'count': {'exclude': True},
                }


class BaseAgentsProcessor(Deck):
    """Agents deck processor
    """
    id: str = Field(exclude=True, default='agents')
    current: deque[AgentInPlayProcessor] = Field(default_factory=deque)

    @property
    def terminated(self) -> list[Agents]:
        return [agent.id for agent in self.current if agent.is_terminated]

    @property
    def on_leave(self) -> list[Agents]:
        return [agent.id for agent in self.current if agent.is_on_leave]


class PlayerAgentsProcessor(BaseAgentsProcessor):
    """P;ayer agents deck processor
    """
    @property
    def in_headquarter(self) -> list[Agents]:
        return [agent.id for agent in self.current if agent.is_in_headquarter]

    @property
    def agent_x(self) -> Optional[Agents]:
        for agent in self.current:
            if agent.is_agent_x:
                return agent.id


class OpponentAgentsProcessor(BaseAgentsProcessor):
    """Opponent agents deck processor
    """
    @property
    def in_headquarter(self) -> list[HiddenAgents]:
        result = []
        for agent in self.current:
            if agent.is_in_headquarter is True:
                if agent.is_revealed is True:
                    result.append(agent.id)
                else:
                    result.append(HiddenAgents.HIDDEN.value)
        return result

    @property
    def agent_x(self) -> Optional[Agents]:
        for agent in self.current:
            if agent.is_agent_x is True:
                result = agent.id if agent.is_revealed is True \
                    else HiddenAgents.HIDDEN.value
                return result


class BaseUserProcessor(Player):
    """Base user processor
    """
    login: str
    score: conint(ge=0) = 0
    faction: Optional[Factions] = None
    has_balance: bool = False
    has_domination: bool = False
    awaiting_abilities: list[AwaitingAbilities] = []


class PlayerProcessor(BaseUserProcessor):
    """Player processor
    """
    id: str = Field(exclude=True, default='player')
    agents: PlayerAgentsProcessor


class OpponentProcessor(BaseUserProcessor):
    """Opponent processor
    """
    id: str = Field(exclude=True, default='opponent')
    agents: OpponentAgentsProcessor


class Users(BaseModel):
    """Users
    """
    player: PlayerProcessor
    opponent: OpponentProcessor


class GroupInPlayProcessor(Card):
    """Group card processor
    """
    id: Groups = Field(..., alias='name')
    is_revealed_to_player: bool = False
    is_revealed_to_opponent: bool = False

    class Config(Card.Config):
        allow_population_by_field_name = True
        fields = {
            'side': {'exclude': True},
            'count': {'exclude': True},
            'is_revealed': {'exclude': True},
            'is_revealed_to_player': {'exclude': True}, # TODO: cant be excluded
            'is_revealed_to_opponent': {'exclude': True}, # TODO: cant be excluded
                }


class GroupsInPlayProcessor(Deck):
    """Groups deck processor
    """
    id: str = Field(exclude=True, default='groups')
    current: deque[GroupInPlayProcessor] = Field(default_factory=deque)
    pile: list[Groups] = []
    owned_by_player: list[GroupInPlayProcessor] = []
    owned_by_opponent: list[GroupInPlayProcessor] = []

    @property
    def deck(self) -> list[HiddenGroups]:
        result = []
        for group in self.current:
            if group.is_revealed_to_player is True:
                result.append(group.id)
            else:
                result.append(HiddenGroups.HIDDEN.value)
        return result


class ObjectiveInPlayProcessor(Card):
    """Objective card processor
    """
    id: Objectives = Field(..., alias='name')
    is_revealed_to_player: bool = False
    is_revealed_to_opponent: bool = False

    class Config(Card.Config):
        allow_population_by_field_name = True
        fields = {
            'is_active': {'exclude': True},
            'side': {'exclude': True},
            'count': {'exclude': True},
            'is_revealed': {'exclude': True},
            'is_revealed_to_player': {'exclude': True}, # TODO: cant be excluded
            'is_revealed_to_opponent': {'exclude': True}, # TODO: cant be excluded
                }


class ObjectivesInPlayProcessor(Deck):
    """Objectives deck processor
    """
    id: str = Field(exclude=True, default='objectives')
    current: deque[ObjectiveInPlayProcessor] = Field(default_factory=deque)
    last: Optional[ObjectiveInPlayProcessor] = None
    pile: list[Objectives] = []
    owned_by_player: list[Objectives] = []
    owned_by_opponent: list[Objectives] = []

    @property
    def deck(self) -> list[HiddenObjectives]:
        result = []
        for objective in self.current:
            if objective.is_revealed_to_player is True:
                result.append(objective.id)
            else:
                result.append(HiddenObjectives.HIDDEN.value)
        return result

    @property
    def mission(self) -> Optional[Objectives]:
        return self.last_id


class Decks(BaseModel):
    """Current decks
    """
    groups: GroupsInPlayProcessor
    objectives: ObjectivesInPlayProcessor


class CurrentGameDataProcessor(Game):
    """Current game processor
    """
    id: str = Field(exclude=True, default='game')
    steps: StepsProcessor
    players: Users
    decks: Decks
    coin: Optional[Dice]

    class Config(Game.Config):
        allow_population_by_field_name = True
        fields = {
            'coin': {'exclude': True},
            }

    def fill(self):
        """Fill sgame constructs by current data
        """
        self.coin = Dice(id='coin')
        self.steps.deal(self.steps.turn_phases_left)
        self.steps.last = self.steps.c.by_id(self.steps.turn_phase)

    def flusch(self):
        """Flusch data to fields
        """
        self.steps.turn_phases_left = self.steps.current_ids
        self.steps.turn_phase = self.steps.last_id
