from mongoengine import (
    Document, EmbeddedDocument, EmbeddedDocumentField, StringField,
    BooleanField, IntField, ListField, EmbeddedDocumentListField,
    queryset_manager
        )
from app.constructs import Phases, Factions, AwaitingAbilities, Objectives, Agents, Groups


class Steps(EmbeddedDocument):
    """Game steps
    """
    game_turn = IntField(min_value=1, default=1)
    turn_phase = StringField(
        default=Phases.BRIEFING.value, choices=Phases.get_values()
            )
    turn_phases_left = ListField(
        StringField(choices=Phases.get_values()),
        default=Phases.get_values()[1:]
            )
    is_game_ends = BooleanField(default=False)
    is_game_starts = BooleanField(default=False)


class AgentInPlay(EmbeddedDocument):
    """Agent in play
    """
    name = StringField(required=str, choices=Agents.get_values())
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
    faction = StringField(null=True, choices=Factions.get_values())
    has_balance = BooleanField(default=False)
    has_domination = BooleanField(default=False)
    awaiting_abilities = ListField(
        StringField(choices=AwaitingAbilities.get_values())
            )
    agents = EmbeddedDocumentField(AgentsInPlay)


class Players(EmbeddedDocument):
    """Players
    """
    player = EmbeddedDocumentField(Player)
    opponent = EmbeddedDocumentField(Player)


class GroupInPlay(EmbeddedDocument):
    """Group in play
    """
    name = StringField(required=True, choices=Groups.get_values())
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
    name = StringField(required=True, choices=Objectives.get_values())
    revealed_to_player = BooleanField(default=False)
    revealed_to_opponent = BooleanField(default=False)


class ObjectivesInPlay(EmbeddedDocument):
    """Objectives in play
    """
    current = EmbeddedDocumentListField(ObjectiveInPlay)
    mission = StringField(choices=Objectives.get_values(), null=True)
    pile = ListField(StringField(choices=Objectives.get_values()))
    owned_by_player = ListField(StringField(choices=Objectives.get_values()))
    owned_by_opponent = ListField(StringField(choices=Objectives.get_values()))


class Decks(EmbeddedDocument):
    """Game decks
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
