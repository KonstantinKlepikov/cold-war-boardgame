from app.constructs import (
    Agents, Groups, GroupFactions, Objectives, Icons, Phases,
    Factions, ObjectiveAbilities
        )
from app.crud.crud_game_static import CRUDStatic


class TestCRUDStatic:
    """Test CRUDStatic class
    """

    def test_get_static_game_data(self, static: CRUDStatic) -> None:
        """Test get static data from db
        """
        data = static.get_static_game_data()

        assert len(data.groups) == 24, 'wrong groups'
        assert data.groups[Groups.GUERILLA.value].id == Groups.GUERILLA.value, 'wrong id'
        assert data.groups[Groups.GUERILLA.value].faction == GroupFactions.MILITARY.value, \
            'wrong group faction'
        assert data.groups[Groups.GUERILLA.value].influence == 1, 'wrong group influence'
        assert 'to the discard pile' in data.groups[Groups.GUERILLA.value].power, \
            'wrong group power'

        assert len(data.objectives) == 21, 'wrong objects'
        assert data.objectives[Objectives.NOBELPEACEPRIZE.value].id == Objectives.NOBELPEACEPRIZE.value, \
            'wrong objective id'
        assert len(data.objectives[Objectives.NOBELPEACEPRIZE.value].bias_icons) == 4, 'wrong icons'
        assert data.objectives[Objectives.NOBELPEACEPRIZE.value].bias_icons[0] == Icons.MEDIA.value, \
            'wrong icon member'
        assert data.objectives[Objectives.NOBELPEACEPRIZE.value].population == 1, 'wrong population'
        assert data.objectives[Objectives.NOBELPEACEPRIZE.value].special_ability_phase == Phases.CEASEFIRE.value, \
            'wrong ability phase'
        assert 'Upon cansing' in data.objectives[Objectives.NOBELPEACEPRIZE.value].special_ability_text, \
            'wrong ability text'
        assert data.objectives[Objectives.NOBELPEACEPRIZE.value].stability == 6, 'wrong stability'
        assert data.objectives[Objectives.NOBELPEACEPRIZE.value].victory_points == 5, 'wrong victory points'

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
