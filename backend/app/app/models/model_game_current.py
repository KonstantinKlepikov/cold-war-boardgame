from mongoengine import (
    Document, EmbeddedDocument, EmbeddedDocumentField, StringField,
    BooleanField, IntField, ListField, EmbeddedDocumentListField,
    queryset_manager, ReferenceField
        )
from app.models import model_user, model_game_static
from app.constructs import Phases, Factions, AwaitingAbilities, Objectives, HiddenObjectives


# class BaseCardInPlay(EmbeddedDocument):
#     """Base card in play
#     """
#     card = ReferenceField(model_game_static.BaseCard)
#     # users = ListField(ReferenceField(model_user.User))
#     revealed_to = ListField(StringField(choices=['player1', 'player2']))

#     # @property
#     # def revealed_to(self) -> list[str]:
#     #     """Return logins of users, who can see card

#     #     Returns:
#     #         list[str]: logins
#     #     """
#     #     return [user.login for user in self.users]

#     @property
#     def id(self) -> str:
#         """Card id

#         Returns:
#             str: id
#         """
#         return self.card.id


# class AgentInPlay(BaseCardInPlay):
#     """Agent in play
#     """
#     card = ReferenceField(model_game_static.Agent)


# class GroupInPlay(BaseCardInPlay):
#     """Group in play
#     """
#     card = ReferenceField(model_game_static.Group)
#     is_active = BooleanField(default=True)


# class ObjectiveInPlay(BaseCardInPlay):
#     """Objective in play
#     """
#     card = ReferenceField(model_game_static.Objective)


# class GameCards(EmbeddedDocument):
#     """Game cards
#     """
#     objectives_deck = EmbeddedDocumentListField(ObjectiveInPlay)
#     objectives_pile = EmbeddedDocumentListField(ObjectiveInPlay)
#     mission = EmbeddedDocumentField(ObjectiveInPlay, null=True)
#     groups_deck = EmbeddedDocumentListField(GroupInPlay)
#     groups_pile = EmbeddedDocumentListField(GroupInPlay)


# class PlayerCards(EmbeddedDocument):
#     """Player cards
#     """
#     headquarter = EmbeddedDocumentListField(AgentInPlay)
#     terminated = EmbeddedDocumentListField(AgentInPlay)
#     agent_x = EmbeddedDocumentField(AgentInPlay, null=True)
#     on_leave = EmbeddedDocumentListField(AgentInPlay)
#     groups = EmbeddedDocumentListField(GroupInPlay)
#     objectives = EmbeddedDocumentListField(ObjectiveInPlay)


class Steps(EmbeddedDocument):
    """Game steps
    """
    game_turn = IntField(min_value=1, default=1)
    turn_phase = StringField(
        default=Phases.BRIEFING.value, choices=Phases.get_values()
            )
    turn_phase_left = ListField(StringField(choices=Phases.get_values()))
    is_game_ends = BooleanField(default=False)
    is_game_starts = BooleanField(default=False)


class AgentInPlay(model_game_static.Agent):
    """Agent in play
    """
    is_revealed = BooleanField(default=False)
    is_in_headquarter = BooleanField(default=True)
    is_terminated = BooleanField(default=False)
    is_on_leave = BooleanField(default=False)
    is_agent_x = BooleanField(default=False)


class AgentsInPlay(EmbeddedDocument):
    deck = EmbeddedDocumentListField(AgentInPlay)


class Player(EmbeddedDocument):
    """Player
    """
    user = ReferenceField(model_user.User)
    score = IntField(min_value=0, max_value=100, default=0)
    faction = StringField(null=True, choices=Factions.get_values())
    agents = AgentsInPlay
    has_balance = BooleanField(null=True)
    has_domination = BooleanField(null=True)
    awaiting_abilities = ListField(
        StringField(null=True, choices=AwaitingAbilities.get_values())
            )

    @property
    def login(self) -> str:
        """User login

        Returns:
            str: login
        """
        return self.user.login


class Players(EmbeddedDocument):
    """Players
    """
    player1 = EmbeddedDocumentField(Player)
    player2 = EmbeddedDocumentField(Player)


class GroupInPlay(model_game_static.Group):
    """Group in play
    """
    is_active = BooleanField(default=True)
    revealed_to_player1 = BooleanField(default=False)
    revealed_to_player2 = BooleanField(default=False)


class GroupsInPlay(EmbeddedDocument):
    deck = EmbeddedDocumentListField(GroupInPlay)
    pile = EmbeddedDocumentListField(GroupInPlay)
    owned_by_player1 = EmbeddedDocumentListField(GroupInPlay)
    owned_by_player2 = EmbeddedDocumentListField(GroupInPlay)


class ObjectiveInPlay(model_game_static.Objective):
    """Objective in play
    """
    revealed_to_player1 = BooleanField(default=False)
    revealed_to_player2 = BooleanField(default=False)


class ObjectivesInPlay(EmbeddedDocument):
    """Objective in play
    """
    current = EmbeddedDocumentListField(ObjectiveInPlay)
    pile = ListField(StringField(choices=Objectives.get_values()))
    deck_view_of_player1 = ListField(StringField(choices=HiddenObjectives.get_values()))
    deck_view_of_player2 = ListField(StringField(choices=HiddenObjectives.get_values()))
    owned_by_player1 = ListField(StringField(choices=Objectives.get_values()))
    owned_by_player2 = ListField(StringField(choices=Objectives.get_values()))
    mission = StringField(choices=Objectives.get_values(), null=True)


class GameCards(EmbeddedDocument):
    """Game cards
    """
    groups = EmbeddedDocumentField(GroupsInPlay)
    objectives = EmbeddedDocumentField(ObjectivesInPlay)


class CurrentGameData(Document):
    """Summary of game data
    """
    steps = EmbeddedDocumentField(Steps, default=Steps())
    players = EmbeddedDocumentField(Players)
    cards = EmbeddedDocumentField(GameCards)

    @queryset_manager
    def objects(doc_cls, queryset):
        """Return last added object from database
        """
        return queryset.order_by('-$natural')
