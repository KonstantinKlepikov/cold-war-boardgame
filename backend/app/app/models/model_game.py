from mongoengine import (
    Document, EmbeddedDocument, EmbeddedDocumentField, StringField,
    BooleanField, IntField, ListField, EmbeddedDocumentListField,
    ValidationError, queryset_manager,
        )
from app.constructs import Phases, Agents, HiddenAgents, Factions


def check_turn_phase(value: str) -> bool:
    """Check is turn_phase allowable

    Args:
        value (str): phase name
    """
    if not Phases.has_value(value):
        raise ValidationError("Phase name is not allowable")


def check_agent(value: str) -> bool:
    """Check is turn_phase allowable

    Args:
        value (str): agent name
    """
    if not Agents.has_value(value):
        raise ValidationError("Agent name is not allowable")


def check_hidden_agent(value: str) -> bool:
    """Check is turn_phase allowable

    Args:
        value (str): agent name
    """
    if not HiddenAgents.has_value(value):
        raise ValidationError("Agent name is not allowable")


def check_faction(value: str) -> bool:
    """Check is turn_phase allowable

    Args:
        value (str): agent name
    """
    if not Factions.has_value(value):
        raise ValidationError("Faction is not allowable")


class GameSteps(EmbeddedDocument):
    """Game steps definition
    """
    game_turn = IntField(min_value=0, default=0)
    turn_phase = StringField(null=True, validation=check_turn_phase)
    turn_phases_left = ListField(StringField(), default=Phases.get_values())
    is_game_end = BooleanField(default=False)


class PlayerGroupOrObjectivreCard(EmbeddedDocument):
    """Known or own by player nonagent card
    """
    is_in_deck = BooleanField(default=True)
    is_in_play = BooleanField(default=False)
    is_active = BooleanField(null=True)
    pos_in_deck = IntField(max_value=0, null=True)
    name = StringField()


class PlayerAgentCard(EmbeddedDocument):
    """Player agent card
    """
    is_dead = BooleanField(default=False)
    is_in_play = BooleanField(default=False)
    is_in_vacation = BooleanField(default=False)
    is_revealed = BooleanField(default=False)
    is_in_headquarter = BooleanField(default=True)
    name = StringField(validation=check_agent)


class PlayerAgentCards(EmbeddedDocument):
    """Agent cards representation
    """
    dead = ListField(StringField(validation=check_agent))
    in_play = StringField(null=True, validation=check_hidden_agent)
    in_vacation = ListField(StringField(validation=check_agent))
    in_headquarter = ListField(StringField(validation=check_hidden_agent))
    db_cards = EmbeddedDocumentListField(PlayerAgentCard)


class PlayerCards(EmbeddedDocument):
    """Array of player cards
    """
    agent_cards = EmbeddedDocumentField(PlayerAgentCards, default=PlayerAgentCards())
    group_cards = EmbeddedDocumentListField(PlayerGroupOrObjectivreCard)
    objective_cards = EmbeddedDocumentListField(PlayerGroupOrObjectivreCard)


class Player(EmbeddedDocument):
    """Player definition
    """
    has_priority = BooleanField(null=True)
    is_bot = BooleanField(null=True)
    score = IntField(min_value=0, max_value=100, default=0)
    faction = StringField(null=True, validation=check_faction)
    player_cards = EmbeddedDocumentField(PlayerCards)
    login = StringField(null=True)
    abilities = ListField(StringField())


class GameDeck(EmbeddedDocument):
    """Deck in play difinition
    """
    deck_len = IntField(min_value=0, default=0)
    pile = ListField(StringField())
    deck = ListField(StringField())


class GameDecks(EmbeddedDocument):
    """Game decks and mission card
    """
    group_deck = EmbeddedDocumentField(
        GameDeck, default=GameDeck()
        )
    objective_deck = EmbeddedDocumentField(
        GameDeck, default=GameDeck()
        )
    mission_card = StringField(null=True)


class CurrentGameData(Document):
    """Summary of game data
    """
    game_steps = EmbeddedDocumentField(GameSteps, default=GameSteps())
    players = EmbeddedDocumentListField(Player)
    game_decks = EmbeddedDocumentField(GameDecks, default=GameDecks())

    @queryset_manager
    def objects(doc_cls, queryset):
        """Return last added object from database
        """
        return queryset.order_by('-$natural')
