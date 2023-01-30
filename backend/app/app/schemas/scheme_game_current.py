from typing import Optional
from pydantic import BaseModel, conint, Field
from app.constructs import (
    Phases, Agents, HiddenGroups, Groups, Objectives, Factions, HiddenObjectives,
    HiddenAgents, AwaitingAbilities
        )
from app.schemas.scheme_game_static import Agent, Group, Objective
from app.models import model_user
from bgameb import Steps, Player, Card, Deck, Game


class StepsProcessor(Steps):
    """Phases and turns of game

    -> send to api or db
    'game_turn'
    'is_game_ends'
    'is_game_starts'
    'turn_phase'
    'turn_phase_left'

    c.dict(
        exclude={
            'steps': {
                'last_id', 'current_ids', 'current', 'last'
                    }
            },
        )

    >  load from db
    data = {'turn_phase_left': [(0, {'id': 'that', 'priority': 0})],
            'turn_phase': None,
            'game_turn': 1,
            'is_game_ends': False,
            'is_game_starts': False,
            }

    e = StepsProcessor(**data)
    e.fill()
    """
    id: str = Field(exclude=True, default='steps')
    game_turn: int = 1
    is_game_ends: bool = False
    is_game_starts: bool = False

    @property
    def turn_phase_left(self) -> list[Phases]:
        return self.current_ids

    @property
    def turn_phase(self) -> Optional[Phases]:
        return self.last_id

    def fill(self):
        """Fill steps
        """
        self.deal(self.turn_phase_left)
        self.last = self.c.by_id(self.turn_phase)


class AgentProcessor(Card):
    card: Agent
    is_in_headquarter: bool = True
    is_terminated: bool = False
    is_on_leave: bool = False
    is_agent_x: bool = False

    class Config(Card.Config):
        """"""


class BaseAgentsProcessor(Deck):
    id: str = Field(exclude=True, default='agents')

    class Config(Deck.Config):
        """"""

    @property
    def terminated(self) -> list[Agents]:
        return [agent.id for agent in self.current if agent.is_terminated]

    @property
    def on_leave(self) -> list[Agents]:
        return [agent.id for agent in self.current if agent.is_on_leave]


class PlayerAgentsProcessor(BaseAgentsProcessor):
    """
    -> send to api
    'in_headquarter'
    'terminated'
    'agent_x'
    'on_leave'
    return ids

    c.dict(
        exclude={
            'agents': {
                'last_id', 'current_ids', 'current', 'last'
                    }
            },
        )

    -> send to db
    'current'

    c.dict(
        exclude={
            'agents': {
                'in_headquarter', 'terminated', 'agent_x', 'on_leave', 'last', 'last_id', 'current_ids'
                    }
            },
        )
    """
    @property
    def in_headquarter(self) -> list[Agents]:
        return [agent.id for agent in self.current if agent.is_in_headquarter]

    @property
    def agent_x(self) -> Optional[Agent]:
        for agent in self.current:
            if agent.is_agent_x:
                return agent.id


class OpponentAgentsProcessor(BaseAgentsProcessor):
    """
    -> send to api
    'in_headquarter'
    'terminated'
    'agent_x'
    'on_leave'
    return ids or _hidden

    c.dict(
        exclude={
            'cards': {
                'last_id', 'current_ids', 'current', 'last'
                    }
            },
        )

    -> send to db
    'current'

    c.dict(
        exclude={
            'cards': {
                'in_headquarter', 'terminated', 'agent_x', 'on_leave', 'last', 'last_id', 'current_ids'
                    }
            },
        )
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
    def agent_x(self) -> Optional[Agent]:
        for agent in self.current:
            if agent.is_agent_x is True:
                result = agent.id if agent.is_revealed is True else HiddenAgents.HIDDEN.value
                return result


class BaseUserProcessor(Player):
    user: model_user.User
    score: conint(ge=0) = 0
    faction: Optional[Factions] = None
    has_balance: Optional[bool] = None
    has_domination: Optional[bool] = None
    abilities: list[AwaitingAbilities] = []


class PlayerProcessor(BaseUserProcessor):
    id: str = Field(exclude=True, default='player')
    agents: PlayerAgentsProcessor


class OpponentProcessor(BaseUserProcessor):
    id: str = Field(exclude=True, default='opponent')
    agents: OpponentAgentsProcessor


class PlayersProcessor(BaseModel):
    player: PlayerProcessor
    opponent: OpponentProcessor


class GroupInPlayProcessor(Card):
    card: Group
    is_revealed_to_player: bool = False
    is_revealed_to_opponent: bool = False
    is_active: bool = True


class GroupsInPlayProcessor(Deck):
    """
    -> send to api
    'pile'
    'owned_by_player'
    'owned_by_opponent'
    'deck'

    c.dict(
        exclude={
            'groups': {
                'last_id', 'current_ids', 'current', 'last',
                    }
            },
        )

    -> send to db
    'current'
    'pile'
    'owned_by_player'
    'owned_by_opponent'

    c.dict(
        exclude={
            'groups': {
                'deck', 'current_ids', 'last', 'last_id'
                    }
            },
        )

    >
    return ids or _hidden
    """
    id: str = Field(exclude=True, default='groups')
    pile: list[Groups] = []
    owned_by_player: list[GroupInPlayProcessor] = []
    owned_by_opponent: list[GroupInPlayProcessor] = []

    class Config(Deck.Config):
        """"""

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
    """"""
    card: Objective
    is_revealed_to_player: bool = False
    is_revealed_to_opponent: bool = False


class ObjectivesInPlayProcessor(Deck):
    """
    -> send to api
    'mission'
    'pile'
    'owned_by_player'
    'owned_by_opponent'
    'deck'

    c.dict(
        exclude={
            'objectives': {
                'last_id', 'current_ids', 'current', 'last'
                    }
            },
        )

    -> send to db
    'current'
    'mission'
    'pile'
    'owned_by_player'
    'owned_by_opponent'

    c.dict(
        exclude={
            'objectives': {
                'deck', 'current_ids', 'last'
                    }
            },
        )

    >
    return ids or _hidden
    """
    id: str = Field(exclude=True, default='objectives')
    pile: list[Objectives]
    owned_by_player: list[Objectives] = []
    owned_by_opponent: list[Objectives] = []

    class Config(Deck.Config):
        fields = {'last_id': 'mission'}

    @property
    def deck(self) -> list[HiddenObjectives]:
        result = []
        for objective in self.current:
            if objective.is_revealed_to_player is True:
                result.append(objective.id)
            else:
                result.append(HiddenObjectives.HIDDEN.value)
            return result


class DecksProcessor(BaseModel):
    groups: GroupsInPlayProcessor
    objectives: ObjectivesInPlayProcessor


class CurrentGameDataProcessor(Game):
    """"""
    id: str = Field(exclude=True, default='game')
    steps: StepsProcessor
    players: PlayersProcessor
    decks: DecksProcessor
