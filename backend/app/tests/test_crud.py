from typing import Dict, Generator
from mongoengine.context_managers import switch_db
from app.crud.crud_user import CRUDUser
from app.crud.crud_card import CRUDCards
from app.models import model_user, model_cards
from app.schemas.cards import (
    GameCards, AgentCard, GroupCard, ObjectiveCard
    )


class TestCRUDUser:
    """Test CRUDUser
    """

    def test_get_user_by_login_from_db(
        self,
        db_user: Dict[str, str],
        connection: Generator,
            ) -> None:
        """Test get user from db by login

        Args:
            users_data (List[Dict[str, str]]): mock users
        """
        with switch_db(model_user.User, 'test-db-alias') as User:
            crud_user = CRUDUser(User)
            user = crud_user.get_by_login(login=db_user['login'])
            assert user.login == db_user['login'], 'wrong user'

            user = crud_user.get_by_login(login='notexisted')
            assert user is None, 'existed user'


class TestCRUDCards:
    """Test CRUDCards
    """

    def test_get_all_cards(
        self,
        connection: Generator,
            ) -> None:
        with switch_db(model_cards.AgentCards, 'test-db-alias') as AgentCards, \
            switch_db(model_cards.GroupCards, 'test-db-alias') as GroupCards, \
            switch_db(model_cards.ObjectiveCards, 'test-db-alias') as ObjectiveCards:
                crud_cards = CRUDCards(
                    [AgentCards, GroupCards, ObjectiveCards],
                    GameCards
                    )
                cards = crud_cards.get_all_cards()
                assert isinstance(cards, GameCards), 'wrong type'
                assert isinstance(cards.agent_cards, list), 'wrong agents type'
                assert len(cards.agent_cards) == 6, 'wrong agent len'
                assert isinstance(cards.agent_cards[0], AgentCard), 'wrong agent type'
                assert isinstance(cards.group_cards, list), 'wrong groups type'
                assert len(cards.group_cards) == 24, 'wrong group len'
                assert isinstance(cards.group_cards[0], GroupCard), 'wrong group type'
                assert isinstance(cards.objective_cards, list), 'wrong objectives type'
                assert len(cards.objective_cards) == 21, 'wrong group len'
                assert isinstance(cards.objective_cards[0], ObjectiveCard), \
                    'wrong objective type'
