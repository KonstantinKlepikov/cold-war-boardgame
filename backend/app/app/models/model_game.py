from mongoengine import (
    Document, EmbeddedDocument, EmbeddedDocumentField, ListField,
    ReferenceField, StringField, BooleanField, IntField,
    GenericReferenceField, ValidationError, queryset_manager
        )
from app.models import model_cards, model_user


class GameSteps(EmbeddedDocument):
    """Game steps definition
    """
    game_turn = IntField(min_value=0, default=0)
    turn_phase = StringField(null=True)


class PlayerAgentCard(EmbeddedDocument):
    """Player agent cards
    """
    is_dead = BooleanField(default=False)
    is_in_play = BooleanField(default=False)
    is_in_vacation = BooleanField(default=False)
    is_revealed = BooleanField(default=False)
    agent_card = ReferenceField(model_cards.AgentCard)


class PlayerCards(EmbeddedDocument):
    """Array of player cards
    """
    agent_cards = ListField(
        EmbeddedDocumentField(PlayerAgentCard)
            )
    group_cards = ListField(
        ReferenceField(model_cards.GroupCard)
            )
    objective_cards = ListField(
        ReferenceField(model_cards.ObjectiveCard)
            )


class Player(EmbeddedDocument):
    """Player definition
    """
    has_priority = BooleanField(null=True)
    is_bot = BooleanField(null=True)
    score = IntField(min_value=0, max_value=100, default=0)
    faction = StringField(null=True)
    player_cards = EmbeddedDocumentField(PlayerCards)
    user = ReferenceField(model_user.User)


def check_cards_pile(pile_card) -> None:
    """Chek pile card

    Args:
        pile_card (): pile card Document

    Raises:
        ValidationError: wrong pile card
    """
    if not isinstance(pile_card, model_cards.GroupCard) or \
            not isinstance(pile_card, model_cards.ObjectiveCard):
        raise ValidationError("Wrong pile card")


class GameDeck(EmbeddedDocument):
    """Deck in play difinition (except players cards)
    """
    deck_len = IntField(min_value=0)
    pile_len = IntField(min_value=0)
    pile = ListField(
        GenericReferenceField(validation=check_cards_pile)
            )


class GameDecks(EmbeddedDocument):
    """Game cards definition (include game deck)
    """
    group_deck = EmbeddedDocumentField(GameDeck)
    objective_deck = EmbeddedDocumentField(GameDeck)


class CurrentGameData(Document):
    """Summary of game data
    """
    game_steps = EmbeddedDocumentField(GameSteps)
    players = ListField(EmbeddedDocumentField(Player))
    game_decks = EmbeddedDocumentField(GameDecks)

    @queryset_manager
    def objects(doc_cls, queryset):
        return queryset.order_by('$natural')
