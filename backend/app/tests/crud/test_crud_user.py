from typing import Generator
from app.crud import crud_user
from app.config import settings


class TestCRUDUser:
    """Test CRUDUser class
    """

    def test_get_user_by_login_from_db(
        self,
        user: crud_user.CRUDUser
        # connection: Generator,
            ) -> None:
        """Test get user from db by login
        """
        # crud = crud_user.CRUDUser(connection['User'])
        u = user.get_by_login(login=settings.user0_login)
        assert u.login == settings.user0_login, 'wrong user'

        u = user.get_by_login(login='notexisted')
        assert u is None, 'existed user'
