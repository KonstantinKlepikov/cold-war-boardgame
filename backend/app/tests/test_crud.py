import pytest
from typing import Dict, Generator, Callable
from mongoengine.context_managers import switch_db
from app.crud import crud_user, crud_card, crud_game
from app.models import model_user, model_cards, model_game
from app.schemas import schema_user, schema_cards, schema_game


class TestCRUDUser:
    """Test CRUDUser class
    """

    def test_get_user_by_login_from_db(
        self,
        db_user: Dict[str, str],
        connection: Generator,
            ) -> None:
        """Test get user from db by login

        Args:
            users_data (List[Dict[str, str]]): mock users
        """
        with switch_db(model_user.User, 'test-db-alias') as User:
            crud = crud_user.CRUDUser(User, schema_user.UserCreateUpdate)
            user = crud.get_by_login(login=db_user['login'])
            assert user.login == db_user['login'], 'wrong user'

            user = crud.get_by_login(login='notexisted')
            assert user is None, 'existed user'


class TestCRUDCards:
    """Test CRUDCards class
    """

    def test_get_all_cards(
        self,
        connection: Generator,
            ) -> None:
        with switch_db(model_cards.AgentCard, 'test-db-alias') as AgentCard, \
            switch_db(model_cards.GroupCard, 'test-db-alias') as GroupCard, \
            switch_db(model_cards.ObjectiveCard, 'test-db-alias') as ObjectiveCard:
                crud = crud_card.CRUDCards(
                    [AgentCard, GroupCard, ObjectiveCard],
                    schema_cards.GameCards
                    )
                cards = crud.get_all_cards()
                assert isinstance(cards, schema_cards.GameCards), 'wrong type'
                assert isinstance(cards.agent_cards, list), 'wrong agents type'
                assert len(cards.agent_cards) == 6, 'wrong agent len'
                assert isinstance(cards.agent_cards[0], schema_cards.AgentCard), 'wrong agent type'
                assert isinstance(cards.group_cards, list), 'wrong groups type'
                assert len(cards.group_cards) == 24, 'wrong group len'
                assert isinstance(cards.group_cards[0], schema_cards.GroupCard), 'wrong group type'
                assert isinstance(cards.objective_cards, list), 'wrong objectives type'
                assert len(cards.objective_cards) == 21, 'wrong group len'
                assert isinstance(cards.objective_cards[0], schema_cards.ObjectiveCard), \
                    'wrong objective type'


class TestCRUDGame:
    """Test CRUDGame class
    """

    def test_get_current_game_data_return_nothing_from_empty_base(
        self,
        connection: Generator,
            ) -> None:
        with switch_db(model_game.CurrentGameData, 'test-db-alias') as CurrentGameData:
            game = crud_game.CRUDGame(CurrentGameData, schema_game.CurrentGameData)
            state = game.get_current_game_data()
            assert not state, 'nonempty state'

    def test_make_user(
        self,
        connection: Generator,
        monkeypatch,
            ) -> None:
        """Test make user function
        """
        def mockreturn(*args, **kwargs) -> Callable:
            with switch_db(model_user.User, 'test-db-alias') as User:
                crud = crud_user.CRUDUser(User, schema_user.UserCreateUpdate)
                return crud.get_by_login(args[0])

        monkeypatch.setattr(crud_user.user, "get_by_login", mockreturn)

        player = crud_game.make_user()
        assert player is None, 'wrong player'
        player = crud_game.make_user('DonaldTrump')
        assert player.login == 'DonaldTrump', 'wrong player'
        with pytest.raises(
            KeyError,
            ):
            player = crud_game.make_user('NotExisted')

    def test_make_agents_cards(
        self,
        connection: Generator,
        monkeypatch,
            ) -> None:
        """Test make agent cards function
        """
        def mockreturn(*args, **kwargs) -> Callable:
            with switch_db(model_cards.AgentCard, 'test-db-alias') as AgentCard, \
                switch_db(model_cards.GroupCard, 'test-db-alias') as GroupCard, \
                switch_db(model_cards.ObjectiveCard, 'test-db-alias') as ObjectiveCard:
                    crud =  crud_card.CRUDCards(
                        [AgentCard, GroupCard, ObjectiveCard],
                        schema_cards.GameCards
                        )
                    return crud.get_all_cards()

        monkeypatch.setattr(crud_card.cards, "get_all_cards", mockreturn)

        agent_cards = crud_game.make_agents_cards()

        assert len(agent_cards) == 6, 'wrong len'
        assert agent_cards[0].is_dead == False, 'wrong is_dead'
        assert agent_cards[0].is_in_play == False, 'wrong is_in_play'
        assert agent_cards[0].is_in_vacation == False, 'wrong is_in_vacation'
        assert agent_cards[0].is_revealed == False, 'wrong is_revealed'
        assert agent_cards[0].agent_card.name == 'Master Spy', 'wrong agent card name'

    def test_make_player(self, monkeypatch) -> None:
        """Test make olayer function
        """
        def mockreturn(*args, **kwargs) -> Callable:
            if args[0]:
                return schema_user.UserBase(login=args[0])
            else:
                return
        monkeypatch.setattr(crud_game, "make_user", mockreturn)

        player = crud_game.make_player('DonaldTrump')
        assert player.user.login == 'DonaldTrump', 'wrong user'
        assert not player.has_priority, 'wrong priority'
        assert player.is_bot == False, 'wrong is_bot'
        assert not player.faction, 'wrong faction'
        assert player.score == 0, 'wrong score'
        assert len(player.player_cards.agent_cards) == 6, 'hasnt cards'
        assert player.player_cards.group_cards == [], 'hasnt cards'
        assert player.player_cards.objective_cards == [], 'hasnt cards'

        player = crud_game.make_player()
        assert not player.user, 'wrong user'
        assert player.is_bot == True, 'wrong is_bot'

    def test_make_players(self, monkeypatch) -> None:
        """Test make olayer function
        """
        def mockreturn(*args, **kwargs) -> Callable:
            if args[0]:
                return schema_user.UserBase(login=args[0])
            else:
                return
        monkeypatch.setattr(crud_game, "make_user", mockreturn)

        players = crud_game.make_players('DonaldTrump')
        assert len(players) == 2, 'wrong players'
        assert players[0].is_bot == False, 'wrong first player'
        assert players[1].is_bot == True, 'wrong second player'

    def test_make_new_game(
        self,
        connection: Generator,
            ) -> None:
        """Test make new game create new current game state
        """
        with switch_db(model_game.CurrentGameData, 'test-db-alias') as CurrentGameData:
            game = crud_game.CRUDGame(CurrentGameData, schema_game.CurrentGameData)
            new_game = game.make_new_game('DonaldTrump')
            assert new_game.game_steps.game_turn == 0, 'wrong game turn'
            assert not new_game.game_steps.turn_phase, 'wrong turn phase'
            assert new_game.players[0].user.login == 'DonaldTrump', 'wrong user'
            assert new_game.players[1].is_bot == True, 'wrong bot'
            assert new_game.game_decks.group_deck.deck_len == 24, 'wrong group len'
            assert new_game.game_decks.group_deck.pile_len == 0, 'wrong group pile len'
            assert new_game.game_decks.group_deck.pile == [], 'wrong group pile'
            assert new_game.game_decks.objective_deck.deck_len == 21, \
                'wrong objective len'
            assert new_game.game_decks.objective_deck.pile_len == 0, \
                'wrong objective pile len'
            assert new_game.game_decks.objective_deck.pile == [], \
                'wrong objective pile'

    def test_make_new_game(
        self,
        connection: Generator,
            ) -> None:
        """Test create new game
        """
        with switch_db(model_game.CurrentGameData, 'test-db-alias') as CurrentGameData:
            game = crud_game.CRUDGame(CurrentGameData, schema_game.CurrentGameData)
            game.create_new_game('DonaldTrump')
            state = game.get_current_game_data()
            assert state, 'empty state'

    @pytest.mark.skip
    def test_get_current_game_data_return_latest_game(
        self,
        connection: Generator,
            ) -> None:
        """Test get_current_game_data() return latest game data
        """
