import yaml
from typing import Dict, Callable, Generator
from fastapi.testclient import TestClient
from mongoengine.context_managers import switch_db
from app.main import app, crud_user, crud_card, crud_game
from app.models import model_user, model_game
from app.config import settings


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
            data={
                'username': users_data['login'],
                'password': users_data['password']
                },
            )

        assert response.status_code == 200, 'wrong status'
        assert response.json()["access_token"], 'no token'
        assert response.json()["token_type"] == 'bearer', 'wrong type'

    def test_login_return_400_if_wrong_login(
        self,
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
            data={
                'username': '111111',
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
            data={
                'username': users_data['login'],
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
                    return y
                except yaml.YAMLError as exc:
                    print(exc)

        monkeypatch.setattr(crud_card.cards, "get_all_cards", mockreturn)
        response = client.get("/game/data/static")

        assert response.status_code == 200, 'wrong status'
        assert response.json()["agent_cards"], 'no agent_cards'
        assert response.json()["group_cards"], 'no group_cards'
        assert response.json()["objective_cards"], 'objective_cards'


class TestGameDataCurrent:
    """Test game/data/current
    """

    def test_game_data_current_return_200(
        self,
        monkeypatch,
        connection: Generator,
            ):
        """Test game data current return correct data
        """
        def mockreturn(*args, **kwargs) -> Callable:
            with switch_db(model_game.CurrentGameData, 'test-db-alias') as CurrentGameData:
                game = crud_game.CRUDGame(CurrentGameData)
                return game.get_current_game_data('DonaldTrump')

        monkeypatch.setattr(crud_game.game, "get_current_game_data", mockreturn)

        response = client.post(
            "/game/data/current",
            headers={
                'Authorization': f'Bearer {settings.user0_token}'
                }
            )
        assert response.status_code == 200, 'wrong status'

    def test_game_data_current_return_401(self):
        """Test game data current return 401 for unauthorized
        """
        response = client.post("/game/data/current")
        assert response.status_code == 401, 'wrong status'
        assert response.json()['detail'] == 'Not authenticated', 'wrong detail'


class TestCreateNewGame:
    """Test game/create
    """

    def test_game_create_return_201(
        self,
        monkeypatch,
        connection: Generator,
            ):
        """Test create new game api resource
        """
        def mockreturn(*args, **kwargs) -> Callable:
            with switch_db(model_game.CurrentGameData, 'test-db-alias') as CurrentGameData:
                game = crud_game.CRUDGame(CurrentGameData)
                game.create_new_game(args[0])

        monkeypatch.setattr(crud_game.game, "create_new_game", mockreturn)

        response = client.post(
            "/game/create",
            headers={
                'Authorization': f'Bearer {settings.user0_token}'
                }
            )
        assert response.status_code == 201, 'wrong status'
        with switch_db(model_game.CurrentGameData, 'test-db-alias') as CurrentGameData:
            assert CurrentGameData.objects().count() == 2, 'wrong count of data'

    def test_game_create_return_401(self):
        """Test game create return 401 for unauthorized
        """
        response = client.post("/game/create")
        assert response.status_code == 401, 'wrong status'
        assert response.json()['detail'] == 'Not authenticated', 'wrong detail'
