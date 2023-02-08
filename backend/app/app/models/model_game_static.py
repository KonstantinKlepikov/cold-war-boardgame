from mongoengine import (
    Document, StringField, IntField, ListField
)
from app.constructs import (
    Phases, Icons, GroupFactions,
    Agents, Groups, Objectives
        )


class Agent(Document):
    """Agent card
    """
    name = StringField(
        unique=True, required=True, choices=Agents.get_values()
            )
    agenda_lose = StringField(required=True)
    agenda_win = StringField(required=True)
    initiative = IntField(min_value=0, required=True)
    meta = {
        'indexes': ['name', ],
            }


class Group(Document):
    """Group card
    """
    name = StringField(
        unique=True, required=True, choices=Groups.get_values()
            )
    faction = StringField(
        required=True, choices=GroupFactions.get_values()
            )
    influence = IntField(min_value=0, required=True)
    power = StringField(required=True)
    meta = {
        'indexes': ['name', ],
            }


class Objective(Document):
    """Objective card
    """
    name = StringField(
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
    meta = {
        'indexes': ['name', ],
            }


class Rules(Document):
    """Rules document
    """
