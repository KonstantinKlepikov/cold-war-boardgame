from typing import Generator
from collections import deque
from app.crud import crud_game_current
from app.schemas import scheme_game_current
from app.config import settings
from app.constructs import (
    Phases, Agents, Groups, Objectives, HiddenAgents,
    HiddenGroups, HiddenObjectives
        )


class TestCRUDGameCurrent:
    """Test CRUDGame class
    """

    def test_get_current_game_data_return_state(
        self,
        game: crud_game_current.CRUDGame,
            ) -> None:
        """Test get current game data return state
        """
        data = game.get_current_game_data(settings.user0_login)

        assert data['steps']['game_turn'] == 1, 'wrong game turn'
        assert data['steps']['turn_phase'] == Phases.BRIEFING.value, \
            'wrong phases'
        assert data['steps']['turn_phases_left'] == Phases.get_values()[1:], \
            'wrong turn phases left'
        assert data['steps']['is_game_ends'] is False, 'wrong end'
        assert data['steps']['is_game_starts'] is False, 'wrong start'

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
        assert data['decks']['objectives']['mission'] is None, 'wrong mission'
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

    def test_get_game_processor(
        self,
        game: crud_game_current.CRUDGame,
            ) -> None:
        """Test get game processor returns game processor object
        """
        current_model = game.get_current_game_data(settings.user0_login)
        game_proc = game.get_game_processor(current_model)
        assert isinstance(game_proc, scheme_game_current.CurrentGameDataProcessor), \
            'wrong return'

        assert game_proc.steps.turn_phase == Phases.BRIEFING.value, \
            'wrong phases'
        assert game_proc.steps.last_id == Phases.BRIEFING.value, \
            'wrong phases'
        assert game_proc.steps.turn_phases_left== Phases.get_values()[1:], \
            'wrong turn phases left'
        assert game_proc.steps.current_ids== Phases.get_values()[1:], \
            'wrong turn phases left'

        assert game_proc.players.player.login == settings.user0_login, \
            'wrong player login'

        assert len(game_proc.players.player.agents.c) == 6, \
            'player agents component not filled'
        assert isinstance(game_proc.players.player.agents.current, deque), \
            'wrong agents current'
        assert len(game_proc.players.player.agents.current) == 6, \
            'wrong player agents current len'
        assert game_proc.players.player.agents.current[0].id == Agents.SPY.value, \
            'wrong agent'

        assert game_proc.players.opponent.login == settings.user2_login, \
            'wrong player login'
        assert len(game_proc.players.opponent.agents.c) == 6, \
            'opponent agents component not filled'
        assert isinstance(game_proc.players.opponent.agents.current, deque), \
            'wrong agents current'
        assert len(game_proc.players.opponent.agents.current) == 6, \
            'wrong opponent agents current len'
        assert game_proc.players.opponent.agents.current[0].id == Agents.SPY.value, \
            'wrong agent'

        assert len(game_proc.decks.groups.c) == 24, 'groups component not filled'
        assert isinstance(game_proc.decks.groups.current, deque), \
            'wrong groups current'
        assert len(game_proc.decks.groups.current) == 24, 'wrong groups current'
        assert game_proc.decks.groups.current[0].id == Groups.GUERILLA.value, \
            'wrong group id'

        assert len(game_proc.decks.objectives.c) == 21, 'objectives component not filled'
        assert len(game_proc.decks.objectives.current) == 21, 'wrong objectives current'
        assert game_proc.decks.objectives.current[0].id == Objectives.NOBELPEACEPRIZE.value, \
            'wrong objective id'

    def test_save_game_processor(
        self,
        game: crud_game_current.CRUDGame,
        connection: Generator,
            ) -> None:
        """Test save game processor returns game processor object
        """
        assert connection['CurrentGameData'].objects().count() == 1, 'wrong count of data'

        current_model = game.get_current_game_data(settings.user0_login)
        current_proc = game.get_game_processor(current_model)
        game.save_game_processor(current_model, current_proc)

        assert connection['CurrentGameData'].objects().count() == 1, 'wrong count of data'

    def test_get_api_scheme(
        self,
        game: crud_game_current.CRUDGame,
        connection: Generator,
            ) -> None:
        current_model = game.get_current_game_data(settings.user0_login)
        current_proc = game.get_game_processor(current_model)
        data = game.get_api_scheme(current_proc).dict()

        assert data['steps']['game_turn'] == 1, 'wrong game turn'
        assert data['steps']['turn_phase'] == Phases.BRIEFING.value, \
            'wrong phases'
        assert data['steps']['turn_phases_left'] == Phases.get_values()[1:], \
            'wrong turn phases left'
        assert data['steps']['is_game_ends'] is False, 'wrong end'
        assert data['steps']['is_game_starts'] is False, 'wrong start'

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
            assert data['players'][player]['agents']['agent_x'] is None, \
                'wrong agent x'
            assert len(data['players'][player]['agents']['in_headquarter']) == 6, \
                'wrong headquarter'
            assert data['players'][player]['agents']['on_leave'] == [], \
                'wrong on_leave'
            assert data['players'][player]['agents']['terminated'] == [], \
                'wrong terminated'
        assert data['players']['player']['agents']['in_headquarter'][0] == Agents.SPY.value, \
                'wrong headquarter value'
        assert data['players']['opponent']['agents']['in_headquarter'][0] == HiddenAgents.HIDDEN.value, \
                'wrong headquarter value'

        assert len(data['decks']['groups']['deck']) == 24, 'wrong groups'
        assert data['decks']['groups']['deck'][0] == HiddenGroups.HIDDEN.value, \
            'wrong groups value'
        assert data['decks']['groups']['pile'] == [], 'wrong groups pile'

        assert len(data['decks']['objectives']['deck']) == 21, 'wrong objectives'
        assert data['decks']['objectives']['deck'][0] == HiddenObjectives.HIDDEN.value, \
            'wrong objectives value'
        assert data['decks']['objectives']['pile'] == [], 'wrong objectives pile'


