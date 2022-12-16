import pytest
from typing import Dict, Generator, Union, Tuple
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
            settings.user0_login
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
        game_proc = game.deal_and_shuffle_decks(inited_game_proc)
        assert len(connection['CurrentGameData'].objects[0].game_decks.objective_deck.current) == 21, \
            'wrong objective current'
        assert len(connection['CurrentGameData'].objects[0].game_decks.group_deck.current) == 24, \
            'wrong group current'
        assert isinstance(game_proc, game_logic.GameProcessor), 'wrong return'
        assert len(game_proc.G.t.objectives.current) == 21, 'wrong proc objective len'
        assert len(game_proc.G.t.groups.current) == 24, 'wrong proc group len'

    @pytest.mark.parametrize("test_input,expected", [
        (crud_game.Faction.KGB, ('kgb', 'cia')), (crud_game.Faction.CIA, ('cia', 'kgb')),
            ])
    def test_set_faction(
        self,
        test_input: crud_game.Faction,
        expected: Tuple[str],
        game: crud_game.CRUDGame,
        inited_game_proc: game_logic.GameProcessor,
        connection: Generator,
            ) -> None:
        """Test set faction
        """
        game_proc = game.set_faction(test_input, inited_game_proc)

        assert game_proc.game.player.faction == expected[0], 'wrong player proc faction'
        assert game_proc.game.bot.faction == expected[1], 'wrong bot proc faction'
        assert game_proc.current_data.players[0].faction == expected[0], 'wrong player current faction'
        assert game_proc.current_data.players[1].faction == expected[1], 'wrong bot current faction'

        data = connection['CurrentGameData'].objects().first()
        assert data.players[0].faction == expected[0], \
            'wrong faction of player'
        assert data.players[1].faction == expected[1], \
            'wrong faction of pot'

        with pytest.raises(HTTPException):
            game_proc = game.set_faction(test_input, inited_game_proc)

    @pytest.mark.parametrize("test_input,expected", [
        (crud_game.Priority.TRUE.value, (True, False)),
        (crud_game.Priority.FALSE.value, (False, True)),
            ])
    def test_set_priority(
        self,
        test_input: crud_game.Priority,
        expected: Tuple[bool],
        game: crud_game.CRUDGame,
        inited_game_proc: game_logic.GameProcessor,
        connection: Generator,
            ) -> None:
        """Test set priority
        """
        game_proc = game.set_priority(test_input, inited_game_proc)

        assert game_proc.game.player.has_priority == expected[0], 'wrong player proc priority'
        assert game_proc.game.bot.has_priority == expected[1], 'wrong bot proc priority'
        assert game_proc.current_data.players[0].has_priority == expected[0], 'wrong player current priority'
        assert game_proc.current_data.players[1].has_priority == expected[1], 'wrong bot current priority'

        data = connection['CurrentGameData'].objects().first()
        assert data.players[0].has_priority == expected[0], 'wrong priority'
        assert data.players[1].has_priority == expected[1], 'wrong priority'

        with pytest.raises(HTTPException):
            game_proc = game.set_priority(test_input, inited_game_proc)

    def test_set_priority_random(
        self,
        game: crud_game.CRUDGame,
        inited_game_proc: game_logic.GameProcessor,
        connection: Generator,
            ) -> None:
        """Test set priority at random
        """
        game_proc = game.set_priority(crud_game.Priority.RANDOM.value, inited_game_proc)

        data = connection['CurrentGameData'].objects().first()
        assert isinstance(data.players[0].has_priority, bool), 'wrong priority'
        assert isinstance(data.players[1].has_priority, bool), 'wrong priority'


class TestCRUDGameNext:
    """Test CRUDGame next_turn and next_phase
    """

    def test_set_next_turn_change_the_turn_number(
        self,
        game: crud_game.CRUDGame,
        inited_game_proc: game_logic.GameProcessor,
        connection: Generator,
            ) -> None:
        """Test set_next_turn() push turn
        """
        game_proc = game.set_next_turn(inited_game_proc)

        assert game_proc.game.game_turn == 1, 'wrong proc turn'
        assert game_proc.current_data.game_steps.game_turn == 1, 'wrong current turn'

        data = connection['CurrentGameData'].objects().first()
        assert data.game_steps.game_turn == 1, 'wrong turn'

    def test_set_next_turn_cant_change_if_game_ends(
        self,
        game: crud_game.CRUDGame,
        inited_game_proc: game_logic.GameProcessor,
        connection: Generator,
            ) -> None:
        """Test set_next_turn() cant change turn if game end
        """
        inited_game_proc.current_data.game_steps.is_game_end = True

        with pytest.raises(HTTPException):
            game_proc = game.set_next_turn(inited_game_proc)

    def test_set_next_phase_change_phase(
        self,
        game: crud_game.CRUDGame,
        inited_game_proc: game_logic.GameProcessor,
        connection: Generator,
            ) -> None:
        """Test set_next_phase() push phase
        """
        game_proc = game.set_next_phase(inited_game_proc)

        assert isinstance(game_proc, game_logic.GameProcessor), 'wrong game_proce'
        assert game_proc.game.game_steps.current_step.id == settings.phases[0], \
            'wrong proc phase'
        assert game_proc.current_data.game_steps.turn_phase == settings.phases[0], \
            'wrong proc phase'

        data = connection['CurrentGameData'].objects().first()
        assert data.game_steps.turn_phase == settings.phases[0], 'wrong phase'

    @pytest.mark.skip('Wait for bgameb changes')
    def test_set_next_phase_cant_change_detente(
        self,
        game: crud_game.CRUDGame,
        inited_game_proc: game_logic.GameProcessor,
        connection: Generator,
            ) -> None:
        """Test set_next_phase() cant change detente
        """
        inited_game_proc.current_data.game_steps.turn_phase = settings.phases[5]

        game_proc = game.set_next_phase(inited_game_proc)

        assert game_proc.game.turn_phase is None, \
            'phase changed if game end'
        assert game_proc.current_data.game_steps.turn_phase is settings.phases[5], \
            'phase changed if game end'

        data = connection['CurrentGameData'].objects().first()
        assert data.game_steps.turn_phase is None, 'detente changed'

    def test_set_next_phase_cant_change_phase_when_game_end(
        self,
        game: crud_game.CRUDGame,
        inited_game_proc: game_logic.GameProcessor,
        connection: Generator,
            ) -> None:
        """Test set_next_phase() raises exception when game end
        """
        # inited_game_proc.current_data.game_steps.is_game_end = True
        inited_game_proc.game.is_game_end = True

        with pytest.raises(HTTPException):
            game_proc = game.set_next_phase(inited_game_proc)


class TestCRUDGamePhaseConditions:
    """Test CRUDGame change conditions after set next phase
    """

    def test_set_mission_card(
        self,
        started_game_proc: game_logic.GameProcessor,
        game: crud_game.CRUDGame,
        connection: Generator,
            ) -> None:
        """Test set mission card and change objective deck
        """
        data = connection['CurrentGameData'].objects().first()
        l = data.game_decks.objective_deck.deck_len - 1
        cards = data.game_decks.objective_deck.current

        game_proc = game.set_mission_card(started_game_proc)

        assert isinstance(game_proc, game_logic.GameProcessor), 'wrong game_proce'

        assert isinstance(
            game_proc.current_data.game_decks.mission_card, str
                ), 'mission not set'
        assert game_proc.current_data.game_decks.objective_deck.deck_len == l, 'wrong len'
        assert game_proc.current_data.game_decks.objective_deck.current == cards[:-1], 'wrong current'
        assert len(game_proc.game.objective_deck.current) == l, 'wrong proc current'
        assert game_proc.game.mission_card == game_proc.current_data.game_decks.mission_card, \
            'wrong proc mission card'

        data = connection['CurrentGameData'].objects().first()
        assert data.game_decks.objective_deck.deck_len == l, 'wrong in db len'
        assert data.game_decks.objective_deck.current == cards[:-1], 'wrong in db current'

    def test_set_turn_priority_at_the_turn_0(
        self,
        started_game_proc: game_logic.GameProcessor,
        game: crud_game.CRUDGame,
        connection: Generator,
            ) -> None:
        """Test set turn priority at the turn 0
        """
        started_game_proc.game.player.score = 30
        started_game_proc.game.bot.score = 0

        game_proc = game.set_turn_priority(started_game_proc)

        assert isinstance(game_proc, game_logic.GameProcessor), 'wrong game_proce'
        assert isinstance(game_proc.current_data.players[0].has_priority, bool), 'wrong priority'
        assert isinstance(game_proc.current_data.players[1].has_priority, bool), 'wrong priority'
        assert isinstance(game_proc.game.player.has_priority, bool), 'wrong priority'
        assert isinstance(game_proc.game.bot.has_priority, bool), 'wrong priority'

        data = connection['CurrentGameData'].objects().first()
        assert isinstance(data.players[0].has_priority, bool), 'wrong priority'
        assert isinstance(data.players[1].has_priority, bool), 'wrong priority'

    @pytest.mark.parametrize("test_input,expected", [
        ((30, 0), (True, False)),
        ((0, 30), (False, True)),
        ((0, 0), (None, None)),
            ])
    def test_set_turn_priority(
        self,
        test_input: Tuple[int],
        expected: Tuple[bool],
        started_game_proc: game_logic.GameProcessor,
        game: crud_game.CRUDGame,
        connection: Generator,
            ) -> None:
        """Test set turn priority
        """
        started_game_proc.game.player.score = test_input[0]
        started_game_proc.game.bot.score = test_input[1]
        started_game_proc.game.game_turn = 1

        game_proc = game.set_turn_priority(started_game_proc)

        assert game_proc.current_data.players[0].has_priority == expected[0], 'wrong priority'
        assert game_proc.current_data.players[1].has_priority == expected[1], 'wrong priority'
        assert game_proc.game.player.has_priority == expected[0], 'wrong priority'
        assert game_proc.game.bot.has_priority == expected[1], 'wrong priority'

        data = connection['CurrentGameData'].objects().first()
        assert data.players[0].has_priority == expected[0], 'wrong priority'
        assert data.players[1].has_priority == expected[1], 'wrong priority'

    def test_set_phase_conditions_after_next_briefing(
        self,
        started_game_proc: game_logic.GameProcessor,
        game: crud_game.CRUDGame,
        connection: Generator,
            ) -> None:
        """Test set_phase_conditions_after_next() set mission card
        in briefing
        """
        started_game_proc.current_data.game_steps.turn_phase = settings.phases[0]

        game_proc = game.set_phase_conditions_after_next(started_game_proc)

        assert isinstance(game_proc, game_logic.GameProcessor), 'wrong game_proce'

        assert isinstance(game_proc.game.mission_card, str), 'mission not set'
        assert isinstance(game_proc.current_data.game_decks.mission_card, str), 'mission not set'

        data = connection['CurrentGameData'].objects().first()
        assert isinstance(data.game_decks.mission_card, str), 'mission not set'
