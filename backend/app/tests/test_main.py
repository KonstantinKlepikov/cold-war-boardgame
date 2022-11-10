import yaml
from typing import Dict, Callable
from fastapi.testclient import TestClient
from app.main import app, crud_user, crud_card
from app.models import model_user
from app.schemas import schema_cards


client = TestClient(app)


class TestUserLogin:
    """Test user/login
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

    def test_login_return_400_if_wrong_login(
        self,
        db_user: Dict[str, str],
        users_data: Dict[str, str],
        monkeypatch,
            ) -> None:
        """Test login return 400 error if npo one user find
        """

        def mockreturn(*args, **kwargs) -> Callable:
            return None

        monkeypatch.setattr(crud_user.user, "get_by_login", mockreturn)
        response = client.post(
            "/user/login",
            json={
                'login': '111111',
                'password': users_data['password']
                }
            )

        assert response.status_code == 400, 'not a error'
        assert response.json()['detail'] == 'Wrong login or password', \
            'wrong error message'

    def test_login_return_400_if_wrong_password(
        self,
        db_user: Dict[str, str],
        users_data: Dict[str, str],
        monkeypatch,
            ) -> None:
        """Test login return 400 error if password wrong
        """

        def mockreturn(*args, **kwargs) -> Callable:
            return model_user.User(**db_user)

        monkeypatch.setattr(crud_user.user, "get_by_login", mockreturn)
        response = client.post(
            "/user/login",
            json={
                'login': users_data['login'],
                'password': '222222'
                }
            )

        assert response.status_code == 400, 'not a error'
        assert response.json()['detail'] == 'Wrong login or password', \
            'wrong error message'


class TestGameDataStatic:
    """Test game/data/static
    """

    def test_game_data_static_return_200(
        self,
        monkeypatch,
        ):
        """Test game data static return correct data
        """

        def mockreturn(*args, **kwargs) -> Callable:
            with open('app/db/data/converted.yaml', "r") as stream:
                try:
                    y = yaml.safe_load(stream)
                    return schema_cards.GameCards.parse_obj(y)
                except yaml.YAMLError as exc:
                    print(exc)

        monkeypatch.setattr(crud_card.cards, "get_all_cards", mockreturn)
        response = client.get("/game/data/static")

        assert response.status_code == 200, 'wrong status'
        assert response.json()["agent_cards"], 'no agent_cards'
        assert response.json()["group_cards"], 'no group_cards'
        assert response.json()["objective_cards"], 'objective_cards'
