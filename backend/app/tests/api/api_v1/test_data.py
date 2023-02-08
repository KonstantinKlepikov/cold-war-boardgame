import yaml
from typing import Callable, Generator
from fastapi.testclient import TestClient
from app.crud import crud_game_static, crud_game_current, crud_user
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

                    db_cards = {
                        'agents': {
                            card['name']: card for card in y['agent_cards']
                                },
                        'groups': {
                            card['name']: card for card in y['group_cards']
                                },
                        'objectives': {
                            card['name']: card for card in y['objective_cards']
                                },
                            }
                    return crud_game_static.StaticGameData(**db_cards)
                except yaml.YAMLError as exc:
                    print(exc)

        monkeypatch.setattr(crud_game_static.static, "get_static_game_data", mockreturn)
        response = client.get(f"{settings.api_v1_str}/game/data/static")

        assert response.status_code == 200, f'{response.content=}'
        assert response.json()["agents"], 'no agent cards'
        assert response.json()["groups"], 'no group cards'
        assert response.json()["objectives"], 'objective cards'


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
            game = crud_game_current.CRUDGame(connection['CurrentGameData'])
            return game.get_last_game(settings.user0_login)

        def mock_user(*args, **kwargs) -> Callable:
            user = crud_user.CRUDUser(connection['User'])
            return user.get_by_login(settings.user0_login)

        monkeypatch.setattr(crud_game_current.game, "get_last_game", mockreturn)
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
