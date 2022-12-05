import pytest
from typing import Dict, Generator, Union
from fastapi import HTTPException
from app.core import game_logic
from app.crud import crud_game
from app.schemas import schema_game
from app.config import settings


class TestCRUDGame:
    """Test CRUDGame class
    """

    def test_get_current_game_data_return_state(
        self,
        game: crud_game.CRUDGame,
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

    def test_get_game_processor(
        self,
        game: crud_game.CRUDGame,
            ) -> None:
        """Test gt game processor returns game processor obgect
        """
        game_proc = game.get_game_processor(
            game.get_current_game_data(settings.user0_login)
                )
        assert isinstance(game_proc, game_logic.GameProcessor), 'wrong return'

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

    def test_deal_and_shuffle_decks(
        self,
        game: crud_game.CRUDGame,
        inited_game_proc: game_logic.GameProcessor,
        connection: Generator,
            ) -> None:
        """Test deal_and_shuffle_decks()
        """
        game_proc = game.deal_and_shuffle_decks(
            game.get_current_game_data(settings.user0_login),
            inited_game_proc
            )
        assert len(connection['CurrentGameData'].objects[0].game_decks.objective_deck.current) == 21, \
            'wrong objective current'
        assert len(connection['CurrentGameData'].objects[0].game_decks.group_deck.current) == 24, \
            'wrong group current'
        assert isinstance(game_proc, game_logic.GameProcessor), 'wrong return'
        assert len(game_proc.game.objective_deck.current) == 21, 'wrong proc objective len'
        assert len(game_proc.game.group_deck.current) == 24, 'wrong proc group len'

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

class TestCRUDGameNextPhase:
    """Test CRUDGame set_next_phase())
    """

    def test_set_next_phase_change_phase(
        self,
        game: crud_game.CRUDGame,
        inited_game_proc: game_logic.GameProcessor,
        connection: Generator,
            ) -> None:
        """Test set_next_phase() push phase
        """
        data = connection['CurrentGameData'].objects().first()
        assert data.game_steps.turn_phase == None, 'wrong phase'

        proc_game = game.set_next_phase(
            game.get_current_game_data(settings.user0_login),
            inited_game_proc
                )
        assert isinstance(proc_game, game_logic.GameProcessor), 'wrong game_proce'
        assert proc_game.game.turn_phase == settings.phases[0], \
            'wrong proc phase'
        data = connection['CurrentGameData'].objects().first()
        assert data.game_steps.turn_phase == settings.phases[0], 'wrong phase'

    def test_set_next_phase_cant_change_detente(
        self,
        game: crud_game.CRUDGame,
        inited_game_proc: game_logic.GameProcessor,
        connection: Generator,
            ) -> None:
        """Test set_next_phase() cant change detente
        """
        data = connection['CurrentGameData'].objects().first()
        data.game_steps.turn_phase = settings.phases[5]
        data.save()

        game.set_next_phase(
            game.get_current_game_data(settings.user0_login),
            inited_game_proc
                )

        data = connection['CurrentGameData'].objects().first()
        assert data.game_steps.turn_phase == settings.phases[5], 'detente changed'

    def test_set_next_phase_cant_change_phase_when_game_end(
        self,
        game: crud_game.CRUDGame,
        inited_game_proc: game_logic.GameProcessor,
        connection: Generator,
            ) -> None:
        """Test set_next_phase() raises exception when game end
        """
        data = connection['CurrentGameData'].objects().first()
        turn_phase = data.game_steps.turn_phase
        data.game_steps.is_game_end = True
        data.save()

        game.set_next_phase(
            game.get_current_game_data(settings.user0_login),
            inited_game_proc
                )

        data = connection['CurrentGameData'].objects().first()
        assert data.game_steps.turn_phase == turn_phase, \
            'phase changed if game end'


class TestCRUDGamePhaseConditions:
    """Test CRUDGame change conditions after set next phase
    """

    def test_set_mission_card(
        self,
        started_game_proc: game_logic.GameProcessor,
        game: crud_game.CRUDGame,
            ) -> None:
        """Test set mission card and change objective deck
        """
        current_data = game.get_current_game_data(settings.user0_login)
        l = current_data.game_decks.objective_deck.deck_len - 1
        cards = current_data.game_decks.objective_deck.current

        game_proc = game.set_mission_card(
            current_data,
            started_game_proc,
                )

        current_data = game.get_current_game_data(settings.user0_login)

        assert isinstance(current_data.game_decks.mission_card, str), 'mission not set'
        assert current_data.game_decks.objective_deck.deck_len == l, 'wrong len'
        assert current_data.game_decks.objective_deck.current == cards[:-1], 'wrong current'
        assert len(game_proc.game.objective_deck.current) == l, 'wrong proc current'
        assert game_proc.game.mission_card == current_data.game_decks.mission_card, \
            'wrong proc mission card'

    def test_set_phase_conditions_after_next_briefing(
        self,
        started_game_proc: game_logic.GameProcessor,
        game: crud_game.CRUDGame,
        connection: Generator,
            ) -> None:
        """Test set_phase_conditions_after_next() set mission card
        in briefing
        """
        data = connection['CurrentGameData'].objects().first()
        data.game_steps.turn_phase = settings.phases[0]
        data.save()

        assert data.game_decks.mission_card is None, 'wrong mission card'
        l = data.game_decks.objective_deck.deck_len
        cards = data.game_decks.objective_deck.current

        game.set_phase_conditions_after_next(
            game.get_current_game_data(settings.user0_login),
            started_game_proc,
                )

        data = connection['CurrentGameData'].objects().first()
        assert isinstance(data.game_decks.mission_card, str), 'mission not set'
        assert data.game_decks.objective_deck.deck_len == l - 1, 'wrong len'
        assert data.game_decks.objective_deck.current == cards[:-1], 'wrong current'
