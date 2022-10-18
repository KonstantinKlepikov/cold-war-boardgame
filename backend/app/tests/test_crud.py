from typing import List, Dict
from app.crud import crud_user


class TestCRUDUser:
    """Test CRUDUser
    """

    def test_get_user_by_login_from_db(
        self, users_data: List[Dict[str, str]], collection
            ) -> None:
        """Test get user from db by login

        Args:
            users_data (List[Dict[str, str]]): mock users
        """
        for data in users_data:
            user = crud_user.user.get_by_login(login=data['login'])
            assert user.login == data['login'], 'wrong user'

        user = crud_user.user.get_by_login(login='notexisted')
        assert user is None, 'existed user'
