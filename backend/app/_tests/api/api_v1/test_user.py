from typing import Dict, Callable, Generator
from fastapi.testclient import TestClient
from app.crud import crud_user
from app.models import model_user
from app.config import settings


class TestUserLogin:
    """Test user/login
    """

    def test_login_return_200(
        self,
        monkeypatch,
        connection: Generator,
        client: TestClient,
            ) -> None:
        """Test login return 200 ok
        """
        def mock_user(*args, **kwargs) -> Callable:
            user = crud_user.CRUDUser(connection['User'])
            return user.get_by_login(settings.user0_login)

        monkeypatch.setattr(crud_user.user, "get_by_login", mock_user)

        response = client.post(
            f"{settings.api_v1_str}/user/login",
            data={
                'username': settings.user0_login,
                'password': settings.user0_password,
                    },
                )

        assert response.status_code == 200, f'{response.content=}'
        assert response.json()["access_token"], 'no token'
        assert response.json()["token_type"] == 'bearer', 'wrong type'

    def test_login_return_400_if_wrong_login(
        self,
        monkeypatch,
        client: TestClient,
            ) -> None:
        """Test login return 400 error if npo one user find
        """

        def mockreturn(*args, **kwargs) -> Callable:
            return None

        monkeypatch.setattr(crud_user.user, "get_by_login", mockreturn)
        response = client.post(
            f"{settings.api_v1_str}/user/login",
            data={
                'username': '111111',
                'password': settings.user0_password
                }
            )

        assert response.status_code == 400, f'{response.content=}'
        assert response.json()['detail'] == 'Wrong login or password', \
            'wrong error message'

    def test_login_return_400_if_wrong_password(
        self,
        db_user: Dict[str, str],
        monkeypatch,
        client: TestClient,
            ) -> None:
        """Test login return 400 error if password wrong
        """

        def mockreturn(*args, **kwargs) -> Callable:
            return model_user.User(**db_user)

        monkeypatch.setattr(crud_user.user, "get_by_login", mockreturn)
        response = client.post(
            f"{settings.api_v1_str}/user/login",
            data={
                'username': settings.user0_password,
                'password': '222222'
                }
            )

        assert response.status_code == 400, f'{response.content=}'
        assert response.json()['detail'] == 'Wrong login or password', \
            'wrong error message'
