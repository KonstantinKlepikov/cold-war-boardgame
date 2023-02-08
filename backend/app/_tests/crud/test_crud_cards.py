from app.crud import crud_card


class TestCRUDCards:
    """Test CRUDCards class
    """

    def test_get_all_cards(self, cards: crud_card.CRUDCards) -> None:
        """Test get all cards from db
        """
        all_cards = cards.get_all_cards()
        assert isinstance(all_cards, dict), 'wrong type'
        assert isinstance(all_cards['agent_cards'], list), 'wrong agents type'
        assert len(all_cards['agent_cards']) == 6, 'wrong agent len'
        assert isinstance(all_cards['agent_cards'][0], dict), 'wrong agent type'
        assert isinstance(all_cards['group_cards'], list), 'wrong groups type'
        assert len(all_cards['group_cards']) == 24, 'wrong group len'
        assert isinstance(all_cards['group_cards'][0], dict), 'wrong group type'
        assert isinstance(all_cards['objective_cards'], list), 'wrong objectives type'
        assert len(all_cards['objective_cards']) == 21, 'wrong group len'
        assert isinstance(all_cards['objective_cards'][0], dict), \
            'wrong objective type'

    def test_get_cards_names(self, cards: crud_card.CRUDCards) -> None:
        """Get cards names from db
        """
        all_cards = cards.get_cards_names()
        assert isinstance(all_cards, dict), 'wrong type'
        assert isinstance(all_cards['agent_cards'], list), 'wrong agents type'
        assert len(all_cards['agent_cards']) == 6, 'wrong agent len'
        assert all_cards['agent_cards'][0] == 'Master Spy', 'wrong agent name'
        assert isinstance(all_cards['group_cards'], list), 'wrong groups type'
        assert len(all_cards['group_cards']) == 24, 'wrong group len'
        assert all_cards['group_cards'][0] == 'Guerilla', 'wrong group name'
        assert isinstance(all_cards['objective_cards'], list), 'wrong objectives type'
        assert len(all_cards['objective_cards']) == 21, 'wrong group len'
        assert all_cards['objective_cards'][0] == 'Nobel Peace Prize', \
            'wrong objective name'
