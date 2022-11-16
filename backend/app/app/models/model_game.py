from mongoengine import (
    Document, EmbeddedDocument, EmbeddedDocumentField, StringField,
    BooleanField, IntField, EmbeddedDocumentListField, queryset_manager,
        )
from app.models import model_cards


class GameSteps(EmbeddedDocument):
    """Game steps definition
    """
    game_turn = IntField(min_value=0, default=0)
    turn_phase = StringField(null=True)
    is_game_end = BooleanField(default=False)


class PlayerAgentCard(EmbeddedDocument):
    """Player agent cards
    """
    is_dead = BooleanField(default=False)
    is_in_play = BooleanField(default=False)
    is_in_vacation = BooleanField(default=False)
    is_revealed = BooleanField(default=False)
    name = StringField()


class PlayerCards(EmbeddedDocument):
    """Array of player cards
    """
    agent_cards = EmbeddedDocumentListField(PlayerAgentCard)
    group_cards = EmbeddedDocumentListField(model_cards.Card)
    objective_cards = EmbeddedDocumentListField(model_cards.Card)


class Player(EmbeddedDocument):
    """Player definition
    """
    has_priority = BooleanField(null=True)
    is_bot = BooleanField(null=True)
    score = IntField(min_value=0, max_value=100, default=0)
    faction = StringField(null=True)
    player_cards = EmbeddedDocumentField(PlayerCards)
    login = StringField(null=True)


class GameDeck(EmbeddedDocument):
    """Deck in play difinition (except players cards)
    """
    deck_len = IntField(min_value=0)
    pile_len = IntField(min_value=0, default=0)
    pile = EmbeddedDocumentListField(model_cards.Card)


class GameDecks(EmbeddedDocument):
    """Game cards definition (include game deck)
    """
    group_deck = EmbeddedDocumentField(
        GameDeck, default=GameDeck(deck_len=24)
        )
    objective_deck = EmbeddedDocumentField(
        GameDeck, default=GameDeck(deck_len=21)
        )


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
