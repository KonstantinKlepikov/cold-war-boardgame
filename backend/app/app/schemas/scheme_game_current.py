from typing import Optional
from pydantic import BaseModel, NonNegativeInt, NonPositiveInt, conint, root_validator
from app.constructs import (
    Phases, Agents, Groups, Objectives, Factions, HiddenObjectives, ObjectiveAbilities,
    HiddenAgents, AwaitingAbilities
        )
from app.schemas.scheme_game_static import Agent, Group, Objective
from app.schemas.schema_user import UserBase

import bgameb
from bgameb import Steps, Player, Bag, Card, Deck


class StepsProcessor(Steps):
    """Phases and turns of game

    send to api or db
    c.dict(
        exclude={
            'steps': {
                'last_id', 'current_ids', 'current', 'last'
                    }
            },
        )

    >
    {'id': 'steps',
    'game_turn': 1,
    'is_game_ends': True,
    'is_game_starts': True,
    'turn_phase': 'some',
    'turn_phase_left': ['that']}

    load from db
    data = {'id': 'step',
            'turn_phase_left': [(0, {'id': 'that', 'priority': 0})],
            'turn_phase': None,
            'game_turn': 1,
            'is_game_ends': False,
            'is_game_starts': False,
            }

    e = StepsProcessor(**data)
    e.fill()

    """
    game_turn: int = 1
    is_game_ends: bool = False
    is_game_starts: bool = False

    @property
    def turn_phase_left(self):
        return self.current_ids

    @property
    def turn_phase(self):
        return self.last_id

    def fill(self):
        """Fill steps
        """
        self.deal(self.turn_phase_left)
        self.last = self.c.by_id(self.turn_phase)


class BaseCardProcessor(BaseModel):
    revealed_to: list[str] = [] # TODO: crate enum


# class GroupProcessor(bgameb.Card, BaseCardProcessor, Group):
#     # card: Group
#     is_active: bool = True


# class ObjectiveProcessor(bgameb.Card, BaseCardProcessor, Objective):
#     """"""
#     # card: Objective



# # class GroupsProcessor(bgameb.Deck):
# #     """"""
# #     pile: list[GroupProcessor]

# #     class Config(bgameb.Deck.Config):
# #         fields = {'current': 'deck'}


# class ObjectivesProcessor(bgameb.Deck):
#     """"""
#     pile: list[ObjectiveProcessor]

#     class Config(bgameb.Deck.Config):
#         fields = {
#             'current': 'deck',
#             'last': 'mission',
#                 }

    # @root_validator(pre=False)
    # def _set_c(cls, values: dict) -> dict:
    #     """This is a validator that sets the field values based on the
    #     the user's account type.

    #     Args:
    #         values (dict): Stores the attributes of the User object.

    #     Returns:
    #         dict: The attributes of the user object with the user's fields.
    #     """
    #     values["c"] = bgameb.base.Component(**all_objective_cards)
    #     return values


class AgentProcessor(Card, Agent):
    """"""
    is_in_headquarter: bool = True
    is_terminated: bool = False
    is_on_leave: bool = False
    is_agent_x: bool = False

    class Config(bgameb.Card):
        """"""


class AgentsProcessor(Deck):
    """
    send to api
    c.dict(
        exclude={
            'cards': {
                'last_id', 'current_ids', 'current', 'last'
                    }
            },
        )

    >

    send to db
    c.dict(
        exclude={
            'cards': {
                'in_headquarter', 'terminated', 'agent_x', 'on_leave',
                    }
            },
        )

    >

    return lists of ids or _hidden

    """

    class Config(bgameb.Deck.Config):
        fields = {
            'current': 'deck',
                }

    @property
    def in_headquarter(self) -> list[HiddenAgents]:
        result = []
        for agent in self.current:
            if agent.is_in_headquarter is True:
                if agent.is_revealed is True: # TODO: change in bgameb
                    result.append(agent.id)
                else:
                    result.append(HiddenAgents.HIDDEN.value)
        return result

    @property
    def terminated(self) -> list[Agents]:
        result = []
        for agent in self.current:
            if agent.is_terminated is True:
                result.append(agent.id)
        return result

    @property
    def agent_x(self) -> Optional[Agent]:
        for agent in self.current:
            if agent.is_agent_x is True:
                result = agent.id if agent.is_revealed is True else HiddenAgents.HIDDEN.value
                return result

    @property
    def on_leave(self) -> list[Agents]:
        result = []
        for agent in self.current:
            if agent.on_leave is True:
                result.append(agent.id)
        return result


class PlayerProcessor(Player):
    score: conint(ge=0) = 0
    faction: Optional[Factions] = None
    agents: AgentsProcessor #TODO: init that processor by static cards
    has_balance: Optional[bool] = None
    has_domination: Optional[bool] = None
    abilities: list[AwaitingAbilities] = []


class PlayersProcessor(BaseModel):
    player1: PlayerProcessor
    player2: PlayerProcessor


class GroupProcessor(Card, Group):
    """"""
    revealed_to_player1: bool = False
    revealed_to_player2: bool = False


class GroupsProcessor(Deck):
    """"""
    pile: list[Agents]
    deck_view_of_player1: list[Groups]
    deck_view_of_player2: list[Groups]
    owned_by_player1: list[Groups] = []
    owned_by_player2: list[Groups] = []

    class Config(bgameb.Deck.Config):
        fields = {
            'current': 'deck',
                }


class ObjectiveProcessor(Card, Objective):
    """"""
    is_revealed_to_player1: bool = False
    is_revealed_to_player2: bool = False


class ObjectivesProcessor(Deck):
    """"""
    pile: list[ObjectiveProcessor]
    deck_view_of_player1: list[Objectives]
    deck_view_of_player2: list[Objectives]
    owned_by_player1: list[Objectives] = []
    owned_by_player2: list[Objectives] = []

    class Config(bgameb.Deck.Config):
        fields = {
            'last': 'mission'
                }

    @property
    def mission(self) -> Optional[Objectives]:
        return self.last_id

    @property
    def deck_view_of_player1(self) -> list[HiddenObjectives]:
        result = []
        for objective in self.current:
            if objective.is_revealed_to_player1 is True:
                result.append(objective)
            else:
                result.append(HiddenObjectives.HIDDEN.value)
            return result

    @property
    def deck_view_of_player2(self) -> list[HiddenObjectives]:
        result = []
        for objective in self.current:
            if objective.is_revealed_to_player1 is True:
                result.append(objective)
            else:
                result.append(HiddenObjectives.HIDDEN.value)
            return result


class GameCardsProcessor(BaseModel):
    groups: GroupsProcessor
    objectives: ObjectivesProcessor


class CurrentGameDataProcessor(bgameb.Game):
    """"""
    steps: StepsProcessor # TODO: init that processor by phases of game, then deal by fill()
    players: PlayersProcessor
    cards: GameCardsProcessor











# class BaseCardInPlay(BaseModel):
#     revealed_to: list[str] = [] # TODO: crate enum


# class AgentInPlay(bgameb.Card, BaseCardInPlay):
#     """"""
#     card: Agent

#     # id is used from model property id
#     # cards from same source

# class GroupInPlay(bgameb.Card, BaseCardInPlay):
#     card: Group
#     is_active: bool = True
#     # TODO: propertyes that returs card: GroupId


# class ObjectiveInPlay(bgameb.Card, BaseCardInPlay):
#     """"""
#     card: Objective
#     # TODO: propertyes that returs card: ObjectiveId


# class BasePlayerCards:
#     objectives: list[Objectives]
#     terminated: list[Agents]
#     on_leave: list[Agents]
#     groups: list[Groups]


# class PlayerCardsDb(BasePlayerCards):
#     headquarter: list[AgentInPlay]
#     agent_x: Optional[AgentInPlay]


# class PlayerCards(BasePlayerCards):
#     headquarter: list[Agents]
#     agent_x: Optional[Agents]
#     # Root_validator: replace id with “_hidden” for hidden for opponent


# class PlayerDb(UserBase):
#     """Player current data
#     """
#     score: conint(ge=0) = 0
#     faction: Optional[Factions] = None
#     cards: PlayerCardsDb
#     has_balance: Optional[bool] = None
#     has_domination: Optional[bool] = None
#     abilities: list[AwaitingAbilities] = []


# class Player(PlayerDb):
#     """Player current data in db
#     """
#     cards: PlayerCards


# class BaseGameCards(BaseModel):
#     objective_pile = list[Objectives]
#     mission = Optional[Objectives]
#     groups_pile = list[Groups]


# class GameCardsDb(BaseGameCards):
#     objectives_deck: list[ObjectiveInPlay]
#     groups_deck: list[GroupInPlay]


# class GameCards(BaseGameCards):
#     objectives_deck: list[Objectives]
#     groups_deck: list[Groups]
#     # Root_validator: replace id with “_hidden” for hidden for opponent


# class StepsDb(BaseModel):
#     """Game steps in db scheme
#     """
#     game_turn: NonNegativeInt = 1
#     turn_phase: Phases = Phases.BRIEFING.value
#     is_game_ends: bool = False
#     is_game_starts: bool = False

#     class Config:
#         schema_extra = {
#             "example": {
#                 "game_turn": 1,
#                 "turn_phase": "briefing",
#                 "is_game_ends": False,
#                 "is_game_starts": False,
#             }
#         }


# class Steps(StepsDb):
#     """Game steps scheme
#     """
#     turn_phases_left: list[Phases] = Phases.get_values()

#     class Config:
#         schema_extra = {
#             "example": {
#                 "game_turn": 1,
#                 "turn_phase": "debriefing",
#                 "is_game_ends": True,
#                 "is_game_starts": True,
#                 "turn_phases_left": [
#                     "detente",
#                     ],
#             }
#         }


# class CurrentGameDataDb(BaseModel):
#     """Current game data
#     """
#     steps: StepsDb
#     players: list[PlayerDb]
#     cards: GameCardsDb


# class CurrentGameData(CurrentGameDataDb):
#     """Current game data
#     """
#     game_steps: Steps
#     players: list[Player]
#     cards: GameCards