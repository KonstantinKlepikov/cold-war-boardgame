from mongoengine import (
    Document, StringField, IntField, ListField, EmbeddedDocument
    )


class CardName(EmbeddedDocument):
    """Card name
    """
    name = StringField(required=True)


class AgentCard(Document):
    """Collection of agents cards
    """

    name = StringField(unique=True, required=True)
    agenda_lose = StringField(required=True)
    agenda_win = StringField(required=True)
    initiative = IntField(min_value=0, required=True)
    meta = {
        'indexes': ['name', ],
        }


class GroupCard(Document):
    """Collection of group cards
    """

    name = StringField(unique=True, required=True)
    faction = StringField(required=True)
    influence = IntField(min_value=0, required=True)
    power = StringField(required=True)
    meta = {
        'indexes': ['name', ],
        }


class ObjectiveCard(Document):
    """Collection of objective cards
    """

    name = StringField(unique=True, required=True)
    bias_icons = ListField(StringField())
    population = IntField(required=True)
    special_ability = StringField()
    stability = IntField(min_value=1, required=True)
    victory_points = IntField(min_value=0, required=True)
    meta = {
        'indexes': ['name', ],
        }
