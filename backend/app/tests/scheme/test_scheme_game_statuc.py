import pytest
import json
from typing import Generator
from app.constructs import (
    Agents, Groups, GroupFactions, Objectives, Icons, Phases,
    Factions, ObjectiveAbilities
        )
from app.schemas import scheme_game_static


class TestSchemeGameStatic:
    """Test game static scheme
    """

    def test_make_game_static_data(
        self,
        connection: Generator
        ) -> None:
        """Test make_game_data()
        """
        agents = json.loads(connection['Agent'].objects.to_json())
        groups = json.loads(connection['Group'].objects.to_json())
        objectives = json.loads(connection['Objective'].objects.to_json())
        data = {
            'agents': agents,
            'groups': groups,
            'objectives': objectives,
        }
        data = scheme_game_static.StaticGameData(**data)

        assert len(data.agents) == 6, 'wrong agents'
        assert data.agents[0].id == Agents.SPY.value, 'wrong agent id'
        assert 'You claim' in data.agents[0].agenda_lose, \
            'wrong agenda lose'
        assert 'Your opponent claims' in data.agents[0].agenda_win, \
            'wrong agenda win'
        assert data.agents[0].initiative == 1, 'wrong initiative'

        assert len(data.groups) == 24, 'wrong groups'
        assert data.groups[0].id == Groups.GUERILLA.value, 'wrong id'
        assert data.groups[0].faction == GroupFactions.MILITARY.value, \
            'wrong group faction'
        assert data.groups[0].influence == 1, 'wrong group influence'
        assert 'to the discard pile' in data.groups[0].power, \
            'wrong group power'

        assert len(data.objectives) == 21, 'wrong objects'
        assert data.objectives[0].id == Objectives.NOBELPEACEPRIZE.value, \
            'wrong objective id'
        assert len(data.objectives[0].bias_icons) == 4, 'wrong icons'
        assert data.objectives[0].bias_icons[0] == Icons.MEDIA.value, \
            'wrong icon member'
        assert data.objectives[0].population == 1, 'wrong population'
        assert data.objectives[0].special_ability_phase == Phases.CEASEFIRE.value, \
            'wrong ability phase'
        assert 'Upon cansing' in data.objectives[0].special_ability_text, \
            'wrong ability text'
        assert data.objectives[0].stability == 6, 'wrong stability'
        assert data.objectives[0].victory_points == 5, 'wrong victory points'

        assert data.phases == Phases.get_values(), 'wrong phases'
        assert data.player_factions == Factions.get_values(), 'wrong factions'
        assert data.objectives_ids == Objectives.get_values(), 'wrong objectives'
        assert data.objectie_icons == Icons.get_values(), 'wrong icons'
        assert data.objectives_ablilities == ObjectiveAbilities.get_values(), \
            'wrong objectives abilities'
        assert data.groups_ids == Groups.get_values(), 'wrong groups'
        assert data.groups_factions == GroupFactions.get_values(), \
            'wrong groups factions'
        assert data.agents_ids == Agents.get_values(), 'wrong agents'
