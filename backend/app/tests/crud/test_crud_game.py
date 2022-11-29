import pytest
from typing import Dict, Generator, Union
from fastapi import HTTPException
from app.crud import crud_game
from app.schemas import schema_game
from app.config import settings


@pytest.fixture(scope="function")
def game(connection: Generator) -> crud_game.CRUDGame:
    """Get game object
    """
    return crud_game.CRUDGame(connection['CurrentGameData'])


class TestCRUDGame:
    """Test CRUDGame class
    """

    def test_get_current_game_data_return_state(
        self,
        game: crud_game.CRUDGame,
        connection: Generator,
            ) -> None:
        """Test get current game data return state
        """
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
        assert len(state.game_decks.group_deck.current) == 24, 'wrong current'
        assert state.game_decks.objective_deck.deck_len == 21, \
            'wrong objective len'
        assert state.game_decks.objective_deck.pile == [], \
            'wrong objective pile'
        assert len(state.game_decks.objective_deck.current) == 21, 'wrong current'
        assert not state.game_decks.mission_card, 'wrong mission card'

    def test_create_new_game(
        self,
        game: crud_game.CRUDGame,
        db_game_data: Dict[str, Union[str, bool]],
        connection: Generator,
            ) -> None:
        """Test create new game
        """
        assert connection['CurrentGameData'].objects().count() == 1, 'wrong count of data'

        obj_in = schema_game.CurrentGameData(**db_game_data)
        game.create_new_game(obj_in)
        assert connection['CurrentGameData'].objects().count() == 2, 'wrong count of data'
        assert connection['CurrentGameData'].objects[0].id != connection['CurrentGameData'].objects[1].id, \
            'not current'
        assert len(connection['CurrentGameData'].objects[1].game_decks.objective_deck.current) == 21, \
            'wrong current'

    def test_set_faction(
        self,
        game: crud_game.CRUDGame,
        connection: Generator,
            ) -> None:
        """Test self faction
        """
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
        game: crud_game.CRUDGame,
        connection: Generator,
            ) -> None:
        """Test set priority to me
        """
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
        game: crud_game.CRUDGame,
        connection: Generator,
            ) -> None:
        """Test set priority to opponent
        """
        game.set_priority(settings.user0_login, crud_game.Priority.FALSE)
        data = connection['CurrentGameData'].objects().first()
        assert not data.players[0].has_priority, 'wrong priority'
        assert data.players[1].has_priority, 'wrong priority'

    def test_set_priority_random(
        self,
        game: crud_game.CRUDGame,
        connection: Generator,
            ) -> None:
        """Test set priority at random
        """
        game.set_priority(settings.user0_login, crud_game.Priority.RANDOM)
        data = connection['CurrentGameData'].objects().first()
        assert isinstance(data.players[0].has_priority, bool), 'wrong priority'
        assert isinstance(data.players[1].has_priority, bool), 'wrong priority'


class TestCRUDGameNextTurn:
    """Test CRUDGame next_turn method
    """

    def test_set_next_turn_phase_change_the_turn_number(
        self,
        game: crud_game.CRUDGame,
        connection: Generator,
            ) -> None:
        """Test set_next_turn() push turn
        """
        data = connection['CurrentGameData'].objects().first()
        assert data.game_steps.game_turn == 0, 'wrong turn'

        game.set_next_turn(settings.user0_login)
        data = connection['CurrentGameData'].objects().first()
        assert data.game_steps.game_turn == 1, 'wrong turn'

    def test_set_next_turn_raises_exception_when_game_end(
        self,
        game: crud_game.CRUDGame,
        connection: Generator,
            ) -> None:
        """Test set_next_turn) raises exception when game end
        """
        data = connection['CurrentGameData'].objects().first()
        data.game_steps.is_game_end = True
        data.save()

        with pytest.raises(
            HTTPException,
            ):
            game.set_next_turn(settings.user0_login)

class TestCRUDGameNextPhase:
    """Test CRUDGame next_phase method
    """

    def test_set_next_phase_change_phase(
        self,
        game: crud_game.CRUDGame,
        connection: Generator,
            ) -> None:
        """Test set_next_phase() push phase
        """
        data = connection['CurrentGameData'].objects().first()
        assert data.game_steps.turn_phase == None, 'wrong phase'

        game.set_next_phase(settings.user0_login)
        data = connection['CurrentGameData'].objects().first()
        assert data.game_steps.turn_phase == settings.phases[0], 'wrong phase'

    def test_set_next_phase_cant_change_detente(
        self,
        game: crud_game.CRUDGame,
        connection: Generator,
            ) -> None:
        """Test set_next_phase() cant change detente
        """
        data = connection['CurrentGameData'].objects().first()
        data.game_steps.turn_phase = settings.phases[-1]
        data.save()

        with pytest.raises(
            HTTPException,
            ):
            game.set_next_phase(settings.user0_login)

    def test_set_next_phase_raises_exception_when_game_end(
        self,
        game: crud_game.CRUDGame,
        connection: Generator,
            ) -> None:
        """Test set_next_phase() raises exception when game end
        """
        data = connection['CurrentGameData'].objects().first()
        data.game_steps.is_game_end = True
        data.save()

        with pytest.raises(
            HTTPException,
            ):
            game.set_next_phase(settings.user0_login)


class TestCRUDGamePhaseConditions:
    """Tesy CRUDGame chek_phase_conditions()
    """

    def test_chek_phase_conditions_raise_if_no_priority(
        self,
        game: crud_game.CRUDGame,
        connection: Generator,
            ) -> None:
        """Test _chek_phase_conditions() if no player has
        priority in briefing
        """
        data = connection['CurrentGameData'].objects().first()
        data.game_steps.turn_phase = settings.phases[0]
        data.save()

        with pytest.raises(
            HTTPException,
            ):
            game._chek_phase_conditions(settings.user0_login)
