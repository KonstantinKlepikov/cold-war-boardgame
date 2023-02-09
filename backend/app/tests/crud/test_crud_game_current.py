from typing import Generator
from app.crud import crud_game_current
from app.config import settings
from app.core.logic import GameLogic
from app.constructs import Phases, Agents, Groups, Objectives


class TestCRUDGameCurrent:
    """Test CRUDGame class
    """

    def test_get_last_game(
        self,
        game: crud_game_current.CRUDGame,
            ) -> None:
        """Test get last game return state
        """
        data = game.get_last_game(settings.user0_login)

        assert data['steps']['game_turn'] == 1, 'wrong game turn'
        assert data['steps']['turn_phase'] == Phases.BRIEFING.value, \
            'wrong phases'
        assert data['steps']['turn_phases_left'] == Phases.get_values()[1:], \
            'wrong turn phases left'
        assert data['steps']['is_game_ends'] is False, 'wrong end'

        assert data['players']['player']['login'] == settings.user0_login, \
            'wrong player login'
        assert data['players']['opponent']['login'] == settings.user2_login, \
            'wrong opponent login'

        for player in ['player', 'opponent']:
            assert data['players'][player]['score'] == 0, 'wrong score'
            assert data['players'][player]['faction'] is None, 'wrong faction'
            assert data['players'][player]['has_balance'] is False, 'wrong balance'
            assert data['players'][player]['has_domination'] is False, 'wrong domination'
            assert data['players'][player]['awaiting_abilities'] == [], \
               'wrong abilities'
            assert len(data['players'][player]['agents']['current']) == 6, 'wrong agents'
            assert data['players'][player]['agents']['current'][0]['name'] == Agents.SPY.value, \
                'wrong agent name'
            assert data['players'][player]['agents']['current'][0]['is_revealed'] is False, \
                'wrong agent revealed'
            assert data['players'][player]['agents']['current'][0]['is_in_headquarter'] is True, \
                'wrong agent headquarter'
            assert data['players'][player]['agents']['current'][0]['is_terminated'] is False, \
                'wrong agent terminated'
            assert data['players'][player]['agents']['current'][0]['is_on_leave'] is False, \
                'wrong agent on leave'
            assert data['players'][player]['agents']['current'][0]['is_agent_x'] is False, \
                'wrong agent agent_x'

        assert len(data['decks']['groups']['current']) == 24, 'wrong groups'
        assert data['decks']['groups']['pile'] == [], 'wrong groups pile'
        assert data['decks']['groups']['owned_by_player'] == [], 'wrong groups owned'
        assert data['decks']['groups']['owned_by_opponent'] == [], 'wrong groups owned'
        assert data['decks']['groups']['current'][0]['name'] == Groups.GUERILLA.value, \
            'wrong group name'
        assert data['decks']['groups']['current'][0]['revealed_to_player'] is False, \
            'wrong group revealed'
        assert data['decks']['groups']['current'][0]['revealed_to_opponent'] is False, \
            'wrong revealed'
        assert data['decks']['groups']['current'][0]['is_active'] is True, \
            'wrong is active'

        assert len(data['decks']['objectives']['current']) == 21, 'wrong objectives'
        assert data['decks']['objectives']['pile'] == [], 'wrong pile'
        assert data['decks']['objectives']['owned_by_player'] == [], 'wrong objectives owned'
        assert data['decks']['objectives']['owned_by_opponent'] == [], 'wrong objectives owned'
        assert data['decks']['objectives']['last'] is None, 'wrong mission'
        assert data['decks']['objectives']['current'][0]['name'] == Objectives.NOBELPEACEPRIZE.value, \
            'wrong objective name'
        assert data['decks']['objectives']['current'][0]['revealed_to_player'] is False, \
            'wrong objective revealed'
        assert data['decks']['objectives']['current'][0]['revealed_to_opponent'] is False, \
            'wrong objective revealed'


    def test_create_new_game(
        self,
        game: crud_game_current.CRUDGame,
        connection: Generator,
            ) -> None:
        """Test create new game
        """
        assert connection['CurrentGameData'].objects().count() == 1, 'wrong count of data'

        game.create_new_game(settings.user0_login)
        assert connection['CurrentGameData'].objects().count() == 2, 'wrong count of data'
        assert connection['CurrentGameData'].objects[0].id != connection['CurrentGameData'].objects[1].id, \
            'not current'

    def test_save_game_logic(
        self,
        game: crud_game_current.CRUDGame,
        game_logic: GameLogic,
        connection: Generator,
            ) -> None:
        """Test save game processor returns game processor object
        """
        assert connection['CurrentGameData'].objects().count() == 1, 'wrong count of data'

        game.save_game_logic(game_logic)

        assert connection['CurrentGameData'].objects().count() == 1, 'wrong count of data'
