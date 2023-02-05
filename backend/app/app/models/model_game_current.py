from mongoengine import (
    Document, EmbeddedDocument, EmbeddedDocumentField, StringField,
    BooleanField, IntField, ListField, EmbeddedDocumentListField,
    EnumField, queryset_manager
        )
from app.constructs import (
    Phases, Factions, AwaitingAbilities, Objectives, Agents, Groups
        )


class Steps(EmbeddedDocument):
    """Game steps
    """
    game_turn = IntField(min_value=1, default=1)
    turn_phase = EnumField(Phases, default=Phases.BRIEFING)
    turn_phases_left = ListField(
        EnumField(Phases),
        default=Phases.get_values()[1:]
            )
    is_game_ends = BooleanField(default=False)
    is_game_starts = BooleanField(default=False)


class AgentInPlay(EmbeddedDocument):
    """Agent in play
    """
    name = EnumField(Agents, required=True)
    is_revealed = BooleanField(default=False)
    is_in_headquarter = BooleanField(default=True)
    is_terminated = BooleanField(default=False)
    is_on_leave = BooleanField(default=False)
    is_agent_x = BooleanField(default=False)


class AgentsInPlay(EmbeddedDocument):
    """Agents in play
    """
    current = EmbeddedDocumentListField(AgentInPlay)


class Player(EmbeddedDocument):
    """Player
    """
    login = StringField(required=True)
    score = IntField(min_value=0, max_value=100, default=0)
    faction = EnumField(Factions, null=True)
    has_balance = BooleanField(default=False)
    has_domination = BooleanField(default=False)
    awaiting_abilities = ListField(EnumField(AwaitingAbilities))
    agents = EmbeddedDocumentField(AgentsInPlay, default=AgentsInPlay())


class Players(EmbeddedDocument):
    """Players
    """
    player = EmbeddedDocumentField(Player, required=True)
    opponent = EmbeddedDocumentField(Player, required=True)


class GroupInPlay(EmbeddedDocument):
    """Group in play
    """
    name = EnumField(Groups, required=True)
    revealed_to_player = BooleanField(default=False)
    revealed_to_opponent = BooleanField(default=False)
    is_active = BooleanField(default=True)


class GroupsInPlay(EmbeddedDocument):
    """Groups in play
    """
    current = EmbeddedDocumentListField(GroupInPlay)
    pile = EmbeddedDocumentListField(GroupInPlay)
    owned_by_player = EmbeddedDocumentListField(GroupInPlay)
    owned_by_opponent = EmbeddedDocumentListField(GroupInPlay)


class ObjectiveInPlay(EmbeddedDocument):
    """Objective in play
    """
    name = EnumField(Objectives, required=True)
    revealed_to_player = BooleanField(default=False)
    revealed_to_opponent = BooleanField(default=False)


class ObjectivesInPlay(EmbeddedDocument):
    """Objectives in play
    """
    current = EmbeddedDocumentListField(ObjectiveInPlay)
    mission = EnumField(Objectives, null=True)
    pile = ListField(EnumField(Objectives))
    owned_by_player = ListField(EnumField(Objectives))
    owned_by_opponent = ListField(EnumField(Objectives))


class Decks(EmbeddedDocument):
    """Game decks
    """
    groups = EmbeddedDocumentField(GroupsInPlay, default=GroupsInPlay())
    objectives = EmbeddedDocumentField(ObjectivesInPlay, default=ObjectivesInPlay())


class CurrentGameData(Document):
    """Summary of game data

    This document have to deleted from db
    on day 3 after its creation
    """
    steps = EmbeddedDocumentField(Steps, default=Steps())
    players = EmbeddedDocumentField(Players, required=True)
    decks = EmbeddedDocumentField(Decks, default=Decks())

    @queryset_manager
    def objects(doc_cls, queryset):
        """Return last added object from database
        """
        return queryset.order_by('-$natural')

    meta = {
        'expireAfterSeconds': 259200,
            }
