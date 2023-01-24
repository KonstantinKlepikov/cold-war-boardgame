from mongoengine import (
    Document, StringField, IntField, ListField, EmbeddedDocument,
    EmbeddedDocumentField, EmbeddedDocumentListField
)
from app.constructs import (
    Factions, Phases, Icons, ObjectiveAbilities, GroupFactions,
    Agents, Groups, Objectives
        )


class BaseCard(EmbeddedDocument):
    """Base class for all game cards
    """
    id = StringField(unique=True, required=True)
    meta = {
        'indexes': ['id', ],
            }


class Agent(BaseCard):
    """Agent card
    """
    id = StringField(
        unique=True, required=True, choices=Agents.get_values()
            )
    agenda_lose = StringField(required=True)
    agenda_win = StringField(required=True)
    initiative = IntField(min_value=0, required=True)


class Group(BaseCard):
    """Group card
    """
    id = StringField(
        unique=True, required=True, choices=Groups.get_values()
            )
    faction = StringField(
        required=True, choices=GroupFactions.get_values()
            )
    influence = IntField(min_value=0, required=True)
    power = StringField(required=True)


class Objective(BaseCard):
    """Objective card
    """
    id = StringField(
        unique=True, required=True, choices=Objectives.get_values()
            )
    bias_icons = ListField(
        StringField(required=True, choices=Icons.get_values())
            )
    population = IntField(min_value=0, required=True)
    special_ability_phase = StringField(
        null=True, choices=Phases.get_values()
            )
    special_ability_text = StringField(null=True)
    stability = IntField(min_value=1, required=True)
    victory_points = IntField(min_value=0, required=True)


class Rules(Document):
    """Rules document
    """


class  StaticGameData(Document):
    """Static game data
    """
    agents = EmbeddedDocumentListField(Agent)
    groups = EmbeddedDocumentListField(Group)
    objectives = EmbeddedDocumentListField(Objective)
    rules = EmbeddedDocumentField(Rules, default=Rules())
    phases = ListField(
        StringField(choices=Phases.get_values()),
        default=Phases.get_values(),
            )
    player_factions = ListField(
        StringField(choices=Factions.get_values()),
        default=Factions.get_values(),
            )
    objectives_ids = ListField(
        StringField(choices=Objectives.get_values()),
        default=Objectives.get_values(),
            )
    objectie_icons = ListField(
        StringField(choices=Icons.get_values()),
        default=Icons.get_values(),
            )
    objectives_ablilitues = ListField(
        StringField(choices=ObjectiveAbilities.get_values()),
        default= ObjectiveAbilities.get_values(),
            )
    groups_ids = ListField(
        StringField(choices=Groups.get_values()),
        default=Groups.get_values(),
            )
    group_factions = ListField(
        StringField(choices=GroupFactions()),
        default=GroupFactions(),
            )
    agents_ids = ListField(
        StringField(choices=Agents.get_values()),
        defult=Agents.get_values(),
            )
