import yaml
from typing import Callable, Generator
from fastapi.testclient import TestClient
from app.crud import crud_card, crud_game, crud_user
from app.config import settings


class TestGameDataStatic:
    """Test game/data/static
    """

    def test_game_data_static_return_200(
        self,
        monkeypatch,
        client: TestClient,
            ) -> None:
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
        response = client.get(f"{settings.api_v1_str}/game/data/static")

        assert response.status_code == 200, f'{response.content=}'
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
        client: TestClient,
            ) -> None:
        """Test game data current return correct data
        """
        def mockreturn(*args, **kwargs) -> Callable:
            game = crud_game.CRUDGame(connection['CurrentGameData'])
            return game.get_current_game_data(settings.user0_login)

        def mock_user(*args, **kwargs) -> Callable:
            user = crud_user.CRUDUser(connection['User'])
            return user.get_by_login(settings.user0_login)

        monkeypatch.setattr(crud_game.game, "get_current_game_data", mockreturn)
        monkeypatch.setattr(crud_user.user, "get_by_login", mock_user)

        response = client.post(
            f"{settings.api_v1_str}/game/data/current",
            headers={
                'Authorization': f'Bearer {settings.user0_token}'
                }
            )
        assert response.status_code == 200, f'{response.content=}'

    def test_game_data_current_return_401(self, client: TestClient,) -> None:
        """Test game data current return 401 for unauthorized
        """
        response = client.post(f"{settings.api_v1_str}/game/data/current")
        assert response.status_code == 401, f'{response.content=}'
        assert response.json()['detail'] == 'Not authenticated', 'wrong detail'
