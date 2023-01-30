from mongoengine import (
    Document, EmbeddedDocument, EmbeddedDocumentField, StringField,
    BooleanField, IntField, ListField, EmbeddedDocumentListField,
    queryset_manager, ReferenceField
        )
from app.models import model_game_static, model_user
from app.constructs import Phases, Factions, AwaitingAbilities, Objectives, HiddenObjectives


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


class AgentInPlay(EmbeddedDocument):
    """Agent in play
    """
    card = ReferenceField(model_game_static.Agent)
    is_revealed = BooleanField(default=False)
    is_in_headquarter = BooleanField(default=True)
    is_terminated = BooleanField(default=False)
    is_on_leave = BooleanField(default=False)
    is_agent_x = BooleanField(default=False)


class AgentsInPlay(EmbeddedDocument):
    current = EmbeddedDocumentListField(AgentInPlay)


class Player(EmbeddedDocument):
    """Player
    """
    user = ReferenceField(model_user.User)
    score = IntField(min_value=0, max_value=100, default=0)
    faction = StringField(null=True, choices=Factions.get_values())
    has_balance = BooleanField(null=True)
    has_domination = BooleanField(null=True)
    awaiting_abilities = ListField(
        StringField(null=True, choices=AwaitingAbilities.get_values())
            )
    agents = EmbeddedDocumentField(AgentsInPlay)

    # @property
    # def login(self) -> str:
    #     """User login

    #     Returns:
    #         str: login
    #     """
    #     return self.user.login


class Players(EmbeddedDocument):
    """Players
    """
    player = EmbeddedDocumentField(Player)
    opponent = EmbeddedDocumentField(Player)


class GroupInPlay(EmbeddedDocument):
    """Group in play
    """
    card = ReferenceField(model_game_static.Group)
    revealed_to_player = BooleanField(default=False)
    revealed_to_opponent = BooleanField(default=False)
    is_active = BooleanField(default=True)


class GroupsInPlay(EmbeddedDocument):
    current = EmbeddedDocumentListField(GroupInPlay)
    pile = EmbeddedDocumentListField(GroupInPlay)
    owned_by_player1= EmbeddedDocumentListField(GroupInPlay)
    owned_by_opponent = EmbeddedDocumentListField(GroupInPlay)


class ObjectiveInPlay(EmbeddedDocument):
    """Objective in play
    """
    card = ReferenceField(model_game_static.Agent)
    revealed_to_player = BooleanField(default=False)
    revealed_to_opponent = BooleanField(default=False)


class ObjectivesInPlay(EmbeddedDocument):
    """Objective in play
    """
    current = EmbeddedDocumentListField(ObjectiveInPlay)
    mission = StringField(choices=Objectives.get_values(), null=True)
    pile = ListField(StringField(choices=Objectives.get_values()))
    owned_by_player = ListField(StringField(choices=Objectives.get_values()))
    owned_by_opponent = ListField(StringField(choices=Objectives.get_values()))


class Decks(EmbeddedDocument):
    """Game cards
    """
    groups = EmbeddedDocumentField(GroupsInPlay)
    objectives = EmbeddedDocumentField(ObjectivesInPlay)


class CurrentGameData(Document):
    """Summary of game data
    """
    steps = EmbeddedDocumentField(Steps, default=Steps(), required=True)
    players = EmbeddedDocumentField(Players)
    decks = EmbeddedDocumentField(Decks)

    @queryset_manager
    def objects(doc_cls, queryset):
        """Return last added object from database
        """
        return queryset.order_by('-$natural')
