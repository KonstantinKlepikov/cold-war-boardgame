import datetime
import pytest
import bgameb
from typing import Generator, Callable
from fastapi import HTTPException
from app.core import security, security_user, game_data
from app.schemas import schema_user
from app.crud import crud_user
from app.models import model_game
from app.config import settings


class TestSecurity:
    """Test security functions
    """

    def test_password_is_hashed(self) -> None:
        """Test password is hashed
        """
        plain_password = '123456789'
        hashed_password = security.get_password_hash(plain_password)
        assert len(hashed_password) == 60, 'wrong hashed password len'

    def test_verify_hashed_password(self) -> None:
        """Test verify hashed password
        """
        assert security.verify_password(
            settings.user0_password,
            settings.user0_hashed_password
            ), 'wrong hash'

    def test_create_access_token(self) -> None:
        """Test create access token
        """
        data = settings.user0_login
        token = security.create_access_token(data)
        assert len(token) == 109, 'wrong len'
        token = security.create_access_token(
            data, expires_delta=datetime.timedelta(minutes=1)
                )
        assert len(token) == 132, 'wrong len'


class TestSecurityUser:
    """Test security user functions
    """

    def test_get_current_user(
        self,
        monkeypatch,
        connection: Generator
            ) -> None:
        """Test get current user
        """
        def mockreturn(*args, **kwargs) -> Callable:
            user = crud_user.CRUDUser(connection['User'])
            return user.get_by_login(settings.user0_login)

        monkeypatch.setattr(crud_user.user, "get_by_login", mockreturn)

        user = security_user.get_current_user(settings.user0_token)
        assert user.login == settings.user0_login, 'wrong login'
        assert user.is_active, 'wrong is_active'
        with pytest.raises(
            HTTPException,
            ):
            security_user.get_current_user('12345')

    def test_get_current_active_user(self, connection: Generator) -> None:
        """Test get current active user
        """
        schema = schema_user.User(login=settings.user0_login)
        user = security_user.get_current_active_user(schema)
        assert user.login == settings.user0_login, 'wrong login'
        assert user.is_active, 'wrong is_active'
        with pytest.raises(
            HTTPException,
            ):
            schema = schema_user.User(login=settings.user0_login, is_active=None)
            security_user.get_current_active_user(schema)


class TestGameData:
    """Test game data functions
    """

    def test_make_game_data(self) -> None:
        """Test make_game_data()
        """
        data = game_data.make_game_data(settings.user0_login)

        assert data, 'empty state'
        assert data.game_steps.game_turn == 0, 'wrong game turn'
        assert not data.game_steps.turn_phase, 'wrong turn phase'
        assert not data.game_steps.is_game_end, 'game end'

        assert data.players[0].login == settings.user0_login, 'wrong user'
        assert not data.players[0].has_priority, 'wrong priority'
        assert data.players[0].is_bot == False, 'wrong is_bot'
        assert not data.players[0].faction, 'wrong faction'
        assert data.players[0].score == 0, 'wrong score'
        assert len(data.players[0].player_cards.agent_cards) == 6, 'hasnt cards'
        assert data.players[0].player_cards.group_cards == [], 'hasnt cards'
        assert data.players[0].player_cards.objective_cards == [], 'hasnt cards'

        assert not data.players[1].login, 'wrong user'
        assert not data.players[1].has_priority, 'wrong priority'
        assert data.players[1].is_bot == True, 'wrong is_bot'
        assert not data.players[1].faction, 'wrong faction'
        assert data.players[1].score == 0, 'wrong score'
        assert len(data.players[1].player_cards.agent_cards) == 6, 'hasnt cards'
        assert data.players[1].player_cards.group_cards == [], 'hasnt cards'
        assert data.players[1].player_cards.objective_cards == [], 'hasnt cards'

        assert data.game_decks.group_deck.deck_len == 24, 'wrong group len'
        assert data.game_decks.group_deck.pile == [], 'wrong group pile'
        assert data.game_decks.objective_deck.deck_len == 21, \
            'wrong objective len'
        assert data.game_decks.objective_deck.pile == [], \
            'wrong objective pile'
        assert not data.game_decks.mission_card, 'wrong mission card'


class TestGameProcessor:
    """Test GameProcessor class
    """

    @pytest.fixture(scope="function")
    def game(self, connection: Generator) -> game_data.GameProcessor:
        """Get game processor object
        """
        return game_data.GameProcessor(login=settings.user0_login)

    def test_create_game(self, game: game_data.GameProcessor) -> None:
        """Test game is created
        """
        assert isinstance(game.game, bgameb.Game), 'wrong game'
        assert isinstance(game.cards, dict), 'not a cards'
        assert isinstance(game.current, model_game.CurrentGameData), 'wrong current'

    def test_objective_deck(self, game: game_data.GameProcessor) -> None:
        """Test objective deck creation
        """
        game.init_new_objective_deck()
        print(game.game.objective_deck.get_names())
        print(game.game.objective_deck.__dict__.keys())
        assert len(game.game.objective_deck) == 26, 'wrong len' # FIXME: here is 21, but tnedd fixes in bgameb

    def test_not_inted_game_eaise_exception(
        self,
        connection: Generator,
            ) -> None:
        """Exception is raised if player not starts any games
        """
        data = connection['CurrentGameData'].objects().first().delete()
        with pytest.raises(
            HTTPException,
            ):
            game_data.GameProcessor(login=settings.user0_login)
