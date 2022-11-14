import pytest
from typing import Dict, Generator, Union
from mongoengine.context_managers import switch_db
from app.crud import crud_user, crud_card, crud_game
from app.models import model_user, model_cards, model_game
from app.schemas import schema_game


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
            crud = crud_user.CRUDUser(User)
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
                    AgentCard, GroupCard, ObjectiveCard
                        )
                cards = crud.get_all_cards()
                assert isinstance(cards, dict), 'wrong type'
                assert isinstance(cards['agent_cards'], list), 'wrong agents type'
                assert len(cards['agent_cards']) == 6, 'wrong agent len'
                assert isinstance(cards['agent_cards'][0], dict), 'wrong agent type'
                assert isinstance(cards['group_cards'], list), 'wrong groups type'
                assert len(cards['group_cards']) == 24, 'wrong group len'
                assert isinstance(cards['group_cards'][0], dict), 'wrong group type'
                assert isinstance(cards['objective_cards'], list), 'wrong objectives type'
                assert len(cards['objective_cards']) == 21, 'wrong group len'
                assert isinstance(cards['objective_cards'][0], dict), \
                    'wrong objective type'


class TestCRUDGame:
    """Test CRUDGame class
    """

    def test_get_current_game_data_return_state(
        self,
        connection: Generator,
            ) -> None:
        """Test get current game data return state
        """
        with switch_db(model_game.CurrentGameData, 'test-db-alias') as CurrentGameData:
            game = crud_game.CRUDGame(CurrentGameData)
            state = game.get_current_game_data('DonaldTrump')

            assert state, 'empty state'
            assert state.game_steps.game_turn == 0, 'wrong game turn'
            assert not state.game_steps.turn_phase, 'wrong turn phase'

            assert state.players[0].user.login == 'DonaldTrump', 'wrong user'
            assert not state.players[0].has_priority, 'wrong priority'
            assert state.players[0].is_bot == False, 'wrong is_bot'
            assert not state.players[0].faction, 'wrong faction'
            assert state.players[0].score == 0, 'wrong score'
            assert len(state.players[0].player_cards.agent_cards) == 6, 'hasnt cards'
            assert state.players[0].player_cards.group_cards == [], 'hasnt cards'
            assert state.players[0].player_cards.objective_cards == [], 'hasnt cards'

            assert not state.players[1].user, 'wrong user'
            assert not state.players[1].has_priority, 'wrong priority'
            assert state.players[1].is_bot == True, 'wrong is_bot'
            assert not state.players[1].faction, 'wrong faction'
            assert state.players[1].score == 0, 'wrong score'
            assert len(state.players[1].player_cards.agent_cards) == 6, 'hasnt cards'
            assert state.players[1].player_cards.group_cards == [], 'hasnt cards'
            assert state.players[1].player_cards.objective_cards == [], 'hasnt cards'

            assert state.game_decks.group_deck.deck_len == 24, 'wrong group len'
            assert state.game_decks.group_deck.pile_len == 0, 'wrong group pile len'
            assert state.game_decks.group_deck.pile == [], 'wrong group pile'
            assert state.game_decks.objective_deck.deck_len == 21, \
                'wrong objective len'
            assert state.game_decks.objective_deck.pile_len == 0, \
                'wrong objective pile len'
            assert state.game_decks.objective_deck.pile == [], \
                'wrong objective pile'

    def test_create_new_game(
        self,
        db_game_data: Dict[str, Union[str, bool]],
        connection: Generator,
            ) -> None:
        """Test create new game
        """
        with switch_db(model_game.CurrentGameData, 'test-db-alias') as CurrentGameData:
            game = crud_game.CRUDGame(CurrentGameData)
            assert CurrentGameData.objects().count() == 1, 'wrong count of data'

            obj_in = schema_game.CurrentGameData(**db_game_data)
            game.create_new_game(obj_in)
            assert CurrentGameData.objects().count() == 2, 'wrong count of data'
            assert CurrentGameData.objects[0].id != CurrentGameData.objects[1].id, \
                'not current'
