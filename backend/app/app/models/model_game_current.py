from mongoengine import (
    Document, EmbeddedDocument, EmbeddedDocumentField, StringField,
    BooleanField, IntField, ListField, EmbeddedDocumentListField,
    queryset_manager, ReferenceField
        )
from app.models import model_user, model_game_static
from app.constructs import Phases, Factions, AwaitingAbilities


class BaseCardInPlay(EmbeddedDocument):
    """Base card in play
    """
    card = ReferenceField(model_game_static.BaseCard)
    users = ListField(ReferenceField(model_user.User))

    @property
    def revealed_to(self) -> list[str]:
        """Return logins of users, who can see card

        Returns:
            list[str]: logins
        """
        return [user.login for user in self.users]

    @property
    def id(self) -> str:
        """Card id

        Returns:
            str: id
        """
        return self.card.id


class AgentInPlay(BaseCardInPlay):
    """Agent in play
    """
    card = ReferenceField(model_game_static.Agent)


class GroupInPlay(BaseCardInPlay):
    """Group in play
    """
    card = ReferenceField(model_game_static.Group)
    is_active = BooleanField(default=True)


class ObjectiveInPlay(BaseCardInPlay):
    """Objective in play
    """
    card = ReferenceField(model_game_static.Objective)


class GameCards(EmbeddedDocument):
    """Game cards
    """
    objectives_deck = EmbeddedDocumentListField(ObjectiveInPlay)
    objectives_pile = EmbeddedDocumentListField(ObjectiveInPlay)
    mission = EmbeddedDocumentField(ObjectiveInPlay, null=True)
    groups_deck = EmbeddedDocumentListField(GroupInPlay)
    groups_pile = EmbeddedDocumentListField(GroupInPlay)


class PlayerCards(EmbeddedDocument):
    """Player cards
    """
    headquarter = EmbeddedDocumentListField(AgentInPlay)
    terminated = EmbeddedDocumentListField(AgentInPlay)
    agent_x = EmbeddedDocumentField(AgentInPlay, null=True)
    on_leave = EmbeddedDocumentListField(AgentInPlay)
    groups = EmbeddedDocumentListField(GroupInPlay)
    objectives = EmbeddedDocumentListField(ObjectiveInPlay)


class Player(EmbeddedDocument):
    """Player
    """
    user = ReferenceField(model_user.User)
    score = IntField(min_value=0, max_value=100, default=0)
    faction = StringField(null=True, choices=Factions.get_values())
    cards = EmbeddedDocumentField(PlayerCards)
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


class Steps(EmbeddedDocument):
    """Game steps
    """
    game_turn = IntField(min_value=1, default=1)
    turn_phase = StringField(
        default=Phases.BRIEFING.value, choices=Phases.get_values()
            )
    is_game_ends = BooleanField(default=False)
    is_game_starts = BooleanField(default=False)


class CurrentGameData(Document):
    """Summary of game data
    """
    steps = EmbeddedDocumentField(Steps, default=Steps())
    players = EmbeddedDocumentListField(Player)
    cards = EmbeddedDocumentField(GameCards)

    @queryset_manager
    def objects(doc_cls, queryset):
        """Return last added object from database
        """
        return queryset.order_by('-$natural')
