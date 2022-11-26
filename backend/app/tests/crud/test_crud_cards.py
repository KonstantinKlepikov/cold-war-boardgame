from typing import Generator
from app.crud import crud_card


class TestCRUDCards:
    """Test CRUDCards class
    """

    def test_get_all_cards(
        self,
        connection: Generator,
            ) -> None:
            """Test get all cards from db
            """
            crud = crud_card.CRUDCards(
                connection['AgentCard'],
                connection['GroupCard'],
                connection['ObjectiveCard'],
                    )
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
