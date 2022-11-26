import pytest
from typing import Dict, Generator, Union
from fastapi import HTTPException
from app.crud import crud_game
from app.schemas import schema_game
from app.config import settings


class TestCRUDGame:
    """Test CRUDGame class
    """

    def test_get_current_game_data_return_state(
        self,
        connection: Generator,
            ) -> None:
        """Test get current game data return state
        """
        game = crud_game.CRUDGame(connection['CurrentGameData'])
        state = game.get_current_game_data(settings.user0_login)

        assert state, 'empty state'
        assert state.game_steps.game_turn == 0, 'wrong game turn'
        assert not state.game_steps.turn_phase, 'wrong turn phase'
        assert not state.game_steps.is_game_end, 'game is end'

        assert state.players[0].login == settings.user0_login, 'wrong user'
        assert not state.players[0].has_priority, 'wrong priority'
        assert state.players[0].is_bot == False, 'wrong is_bot'
        assert not state.players[0].faction, 'wrong faction'
        assert state.players[0].score == 0, 'wrong score'
        assert len(state.players[0].player_cards.agent_cards) == 6, 'hasnt cards'
        assert state.players[0].player_cards.group_cards == [], 'hasnt cards'
        assert state.players[0].player_cards.objective_cards == [], 'hasnt cards'

        assert not state.players[1].login, 'wrong user'
        assert not state.players[1].has_priority, 'wrong priority'
        assert state.players[1].is_bot == True, 'wrong is_bot'
        assert not state.players[1].faction, 'wrong faction'
        assert state.players[1].score == 0, 'wrong score'
        assert len(state.players[1].player_cards.agent_cards) == 6, 'hasnt cards'
        assert state.players[1].player_cards.group_cards == [], 'hasnt cards'
        assert state.players[1].player_cards.objective_cards == [], 'hasnt cards'

        assert state.game_decks.group_deck.deck_len == 24, 'wrong group len'
        assert state.game_decks.group_deck.pile == [], 'wrong group pile'
        assert state.game_decks.objective_deck.deck_len == 21, \
            'wrong objective len'
        assert state.game_decks.objective_deck.pile == [], \
            'wrong objective pile'
        assert not state.game_decks.mission_card, 'wrong mission card'

    def test_create_new_game(
        self,
        db_game_data: Dict[str, Union[str, bool]],
        connection: Generator,
            ) -> None:
        """Test create new game
        """
        game = crud_game.CRUDGame(connection['CurrentGameData'])
        assert connection['CurrentGameData'].objects().count() == 1, 'wrong count of data'

        obj_in = schema_game.CurrentGameData(**db_game_data)
        game.create_new_game(obj_in)
        assert connection['CurrentGameData'].objects().count() == 2, 'wrong count of data'
        assert connection['CurrentGameData'].objects[0].id != connection['CurrentGameData'].objects[1].id, \
            'not current'

    def test_set_faction(
        self,
        connection: Generator,
            ) -> None:
        """Test self faction
        """
        game = crud_game.CRUDGame(connection['CurrentGameData'])

        game.set_faction(settings.user0_login, crud_game.Faction.KGB)
        data = connection['CurrentGameData'].objects().first()
        assert data.players[0].faction == 'kgb', \
            'wrong faction of player'
        assert data.players[1].faction == 'cia', \
            'wrong faction of pot'

        game.set_faction(settings.user0_login, crud_game.Faction.CIA)
        data = connection['CurrentGameData'].objects().first()
        assert data.players[0].faction == 'kgb', \
            'wrong faction of player'
        assert data.players[1].faction == 'cia', \
            'wrong faction of pot'

    def test_set_priority_to_me(
        self,
        connection: Generator,
            ) -> None:
        """Test set priority to me
        """
        game = crud_game.CRUDGame(connection['CurrentGameData'])

        game.set_priority(settings.user0_login, crud_game.Priority.TRUE)
        data = connection['CurrentGameData'].objects().first()
        assert data.players[0].has_priority, 'wrong priority'
        assert not data.players[1].has_priority, 'wrong priority'

        game.set_priority(settings.user0_login, crud_game.Priority.FALSE)
        data = connection['CurrentGameData'].objects().first()
        assert data.players[0].has_priority, 'wrong priority'
        assert not data.players[1].has_priority, 'wrong priority'


    def test_set_priority_to_opponent(
        self,
        connection: Generator,
            ) -> None:
        """Test set priority to opponent
        """
        game = crud_game.CRUDGame(connection['CurrentGameData'])

        game.set_priority(settings.user0_login, crud_game.Priority.FALSE)
        data = connection['CurrentGameData'].objects().first()
        assert not data.players[0].has_priority, 'wrong priority'
        assert data.players[1].has_priority, 'wrong priority'

    def test_set_priority_random(
        self,
        connection: Generator,
            ) -> None:
        """Test set priority at random
        """
        game = crud_game.CRUDGame(connection['CurrentGameData'])

        game.set_priority(settings.user0_login, crud_game.Priority.RANDOM)
        data = connection['CurrentGameData'].objects().first()
        assert isinstance(data.players[0].has_priority, bool), 'wrong priority'
        assert isinstance(data.players[1].has_priority, bool), 'wrong priority'

    def test_set_next_turn_phase_change_the_turn_number(
        self,
        connection: Generator,
            ) -> None:
        """Test set_next_turn_phase() push turn
        """
        game = crud_game.CRUDGame(connection['CurrentGameData'])
        data = connection['CurrentGameData'].objects().first()
        assert data.game_steps.game_turn == 0, 'wrong turn'

        game.set_next_turn_phase(settings.user0_login, True, False)
        data = connection['CurrentGameData'].objects().first()
        assert data.game_steps.game_turn == 1, 'wrong turn'

    def test_set_next_turn_phase_change_phase(
        self,
        connection: Generator,
            ) -> None:
        """Test set_next_turn_phase() push phase
        """
        game = crud_game.CRUDGame(connection['CurrentGameData'])
        data = connection['CurrentGameData'].objects().first()
        assert data.game_steps.turn_phase == None, 'wrong phase'

        game.set_next_turn_phase(settings.user0_login, False, True)
        data = connection['CurrentGameData'].objects().first()
        assert data.game_steps.turn_phase == settings.phases[0], 'wrong phase'

        game.set_next_turn_phase(settings.user0_login, False, True)
        data = connection['CurrentGameData'].objects().first()
        assert data.game_steps.turn_phase == settings.phases[1], 'wrong phase'

    def test_set_next_turn_phase_change_turn_and_phase(
        self,
        connection: Generator,
            ) -> None:
        """Test set_next_turn_phase() push turn and phases
        """
        game = crud_game.CRUDGame(connection['CurrentGameData'])
        data = connection['CurrentGameData'].objects().first()
        assert data.game_steps.game_turn == 0, 'wrong turn'
        assert data.game_steps.turn_phase == None, 'wrong phase'

        game.set_next_turn_phase(settings.user0_login, True, True)
        data = connection['CurrentGameData'].objects().first()
        assert data.game_steps.game_turn == 1, 'wrong turn'
        assert data.game_steps.turn_phase == settings.phases[1], 'wrong phase'

        game.set_next_turn_phase(settings.user0_login, True, True)
        data = connection['CurrentGameData'].objects().first()
        assert data.game_steps.game_turn == 2, 'wrong turn'
        assert data.game_steps.turn_phase == settings.phases[1], 'wrong phase'

    def test_set_next_turn_phase_cant_change_detente(
        self,
        connection: Generator,
            ) -> None:
        """Test set_next_turn_phase() cant change detente
        """
        game = crud_game.CRUDGame(connection['CurrentGameData'])
        data = connection['CurrentGameData'].objects().first()
        data.game_steps.turn_phase = settings.phases[-1]
        data.save()

        with pytest.raises(
            HTTPException,
            ):
            game.set_next_turn_phase(settings.user0_login, False, True)

        game.set_next_turn_phase(settings.user0_login, True, True)
        data = connection['CurrentGameData'].objects().first()
        assert data.game_steps.game_turn == 1, 'wrong turn'
        assert data.game_steps.turn_phase == settings.phases[1], 'wrong phase'

    def test_set_next_raises_exception_when_game_end(
        self,
        connection: Generator,
            ) -> None:
        """Test set_next_turn_phase() raises exception when game end
        """
        game = crud_game.CRUDGame(connection['CurrentGameData'])
        data = connection['CurrentGameData'].objects().first()
        data.game_steps.is_game_end = True
        data.save()

        with pytest.raises(
            HTTPException,
            ):
            game.set_next_turn_phase(settings.user0_login, False, True)
        with pytest.raises(
            HTTPException,
            ):
            game.set_next_turn_phase(settings.user0_login, True, False)
        with pytest.raises(
            HTTPException,
            ):
            game.set_next_turn_phase(settings.user0_login, True, True)
