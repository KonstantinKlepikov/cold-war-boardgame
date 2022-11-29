import pytest
from typing import Generator
from app.crud import crud_card


class TestCRUDCards:
    """Test CRUDCards class
    """

    @pytest.fixture(scope="function")
    def crud(self, connection: Generator) -> crud_card.CRUDCards:
        """Get game processor object
        """
        return crud_card.CRUDCards(
            connection['AgentCard'],
            connection['GroupCard'],
            connection['ObjectiveCard'],
                )

    def test_get_all_cards(self, crud: crud_card.CRUDCards) -> None:
            """Test get all cards from db
            """
            cards = crud.get_all_cards()
            assert isinstance(cards, dict), 'wrong type'
            assert isinstance(cards['agent_cards'], list), 'wrong agents type'
            assert len(cards['agent_cards']) == 6, 'wrong agent len'
            assert isinstance(cards['agent_cards'][0], dict), 'wrong agent type'
            assert isinstance(cards['group_cards'], list), 'wrong groups type'
            assert len(cards['group_cards']) == 24, 'wrong group len'
            assert isinstance(cards['group_cards'][0], dict), 'wrong group type'
            assert isinstance(cards['objective_cards'], list), 'wrong objectives type'
            assert len(cards['objective_cards']) == 21, 'wrong group len'
            assert isinstance(cards['objective_cards'][0], dict), \
                'wrong objective type'

    def test_get_cards_names(self, crud: crud_card.CRUDCards) -> None:
        """Get cards names from db
        """
        cards = crud.get_cards_names()
        assert isinstance(cards, dict), 'wrong type'
        assert isinstance(cards['agent_cards'], list), 'wrong agents type'
        assert len(cards['agent_cards']) == 6, 'wrong agent len'
        assert cards['agent_cards'][0] == 'Master Spy', 'wrong agent name'
        assert isinstance(cards['group_cards'], list), 'wrong groups type'
        assert len(cards['group_cards']) == 24, 'wrong group len'
        assert cards['group_cards'][0] == 'Guerilla', 'wrong group name'
        assert isinstance(cards['objective_cards'], list), 'wrong objectives type'
        assert len(cards['objective_cards']) == 21, 'wrong group len'
        assert cards['objective_cards'][0] == 'Nobel Peace Prize', \
            'wrong objective name'
