from typing import Dict, Generator, Union
from app.core import processor_game
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
        assert len(state.players[0].player_cards.agent_cards.db_cards) == 6, 'hasnt cards'
        assert state.players[0].player_cards.agent_cards.dead == [], 'wrong dead'
        assert state.players[0].player_cards.agent_cards.in_play == None, 'wrong in play'
        assert state.players[0].player_cards.agent_cards.in_vacation == [], 'wrong vacation'
        assert state.players[0].player_cards.agent_cards.revealed == [], 'wrong revealed'
        assert state.players[0].player_cards.group_cards == [], 'hasnt cards'
        assert state.players[0].player_cards.objective_cards == [], 'hasnt cards'

        assert not state.players[1].login, 'wrong user'
        assert not state.players[1].has_priority, 'wrong priority'
        assert state.players[1].is_bot == True, 'wrong is_bot'
        assert not state.players[1].faction, 'wrong faction'
        assert state.players[1].score == 0, 'wrong score'
        assert len(state.players[1].player_cards.agent_cards.db_cards) == 6, 'hasnt cards'
        assert state.players[1].player_cards.agent_cards.dead == [], 'wrong dead'
        assert state.players[1].player_cards.agent_cards.in_play == None, 'wrong in play'
        assert state.players[1].player_cards.agent_cards.in_vacation == [], 'wrong vacation'
        assert state.players[1].player_cards.agent_cards.revealed == [], 'wrong revealed'
        assert state.players[1].player_cards.group_cards == [], 'hasnt cards'
        assert state.players[1].player_cards.objective_cards == [], 'hasnt cards'

        assert state.game_decks.group_deck.deck_len == 24, 'wrong group len'
        assert state.game_decks.group_deck.pile == [], 'wrong group pile'
        assert len(state.game_decks.group_deck.deck) == 24, 'wrong current'
        assert state.game_decks.objective_deck.deck_len == 21, \
            'wrong objective len'
        assert state.game_decks.objective_deck.pile == [], \
            'wrong objective pile'
        assert len(state.game_decks.objective_deck.deck) == 21, 'wrong current'
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
        assert isinstance(game_proc, processor_game.GameProcessor), 'wrong return'

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
