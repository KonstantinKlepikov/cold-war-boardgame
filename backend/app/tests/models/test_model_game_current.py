import pytest
import json
from typing import Generator
from app.constructs import Agents, Groups, Objectives, Phases
from app.schemas import scheme_game_current
from app.config import settings


class TestModelGameCurrent:
    """Test game static scheme
    """

    def test_game_current_data_in_db(
        self,
        connection: Generator
        ) -> None:
        """Test current data in db
        """

        data = json.loads(connection['CurrentGameData'].objects.to_json())[0]

        assert data['steps']['game_turn'] == 1, 'wrong game turn'
        assert data['steps']['turn_phase'] == Phases.BRIEFING.value, \
            'wrong phases'
        assert data['steps']['turn_phases_left'] == Phases.get_values()[1:], \
            'wrong turn phases left'
        assert data['steps']['is_game_ends'] is False, 'wrong end'
        assert data['steps']['is_game_starts'] is False, 'wrong start'

        for player in ['player', 'opponent']:
            assert data['players'][player]['login'] == settings.user0_login, \
                'wrong login'
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

    def test_game_current_data_scheme_db(
        self,
        connection: Generator
        ) -> None:
        """Test current data scheme to db output
        """

        data_db = json.loads(connection['CurrentGameData'].objects.to_json())[0]
        data = scheme_game_current.CurrentGameDataProcessor(**data_db).dict(
            exclude={
                'steps': {
                    'last_id', 'current_ids', 'current', 'last'
                        }
                },
            by_alias=True,
        )

        print(data['steps'])

        assert data['steps']['game_turn'] == 1, 'wrong game turn'
        assert data['steps']['turn_phase'] == Phases.BRIEFING.value, \
            'wrong phases'
        assert data['steps']['turn_phases_left'] == Phases.get_values()[1:], \
            'wrong turn phases left'
        assert data['steps']['is_game_ends'] is False, 'wrong end'
        assert data['steps']['is_game_starts'] is False, 'wrong start'
