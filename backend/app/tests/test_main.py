from typing import List, Dict, Callable
from fastapi.testclient import TestClient
from app.main import app, crud_user
from app.models import model_user


client = TestClient(app)


class TestLogin:
    """Test login resource
    """

    def test_login_return_200(
        self,
        db_user: Dict[str, str],
        users_data: Dict[str, str],
        monkeypatch,
            ) -> None:
        """Test login return 200 ok
        """

        def mockreturn(*args, **kwargs) -> Callable:
            return model_user.User(**db_user)

        monkeypatch.setattr(crud_user.user, "get_by_login", mockreturn)
        response = client.post(
            "/user/login",
            json={
                'login': users_data['login'],
                'password': users_data['password']
                }
            )

        assert response.status_code == 200, 'wrong status'
        assert response.json()["access_token"], 'no token'