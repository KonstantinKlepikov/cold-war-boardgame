from typing import Dict, Generator
from mongoengine.context_managers import switch_db
from app.crud.crud_user import CRUDUser
from app.models import model_user


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
