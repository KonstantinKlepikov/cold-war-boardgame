from typing import Generator
from mongoengine.context_managers import switch_db
from app.crud import crud_user
from app.models import model_user
from app.config import settings


class TestCRUDUser:
    """Test CRUDUser class
    """

    def test_get_user_by_login_from_db(
        self,
        connection: Generator,
            ) -> None:
        """Test get user from db by login

        Args:
            users_data (List[Dict[str, str]]): mock users
        """
        with switch_db(model_user.User, 'test-db-alias') as User:
            crud = crud_user.CRUDUser(User)
            user = crud.get_by_login(login=settings.user0_login)
            assert user.login == settings.user0_login, 'wrong user'

            user = crud.get_by_login(login='notexisted')
            assert user is None, 'existed user'
