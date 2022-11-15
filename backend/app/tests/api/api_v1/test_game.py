import pytest
from typing import Callable, Generator
from fastapi.testclient import TestClient
from mongoengine.context_managers import switch_db
from app.crud import crud_game
from app.models import model_game
from app.config import settings


class TestCreateNewGame:
    """Test game/create
    """

    def test_game_create_return_201(
        self,
        monkeypatch,
        connection: Generator,
        client: TestClient,
            ) -> None:
        """Test create new game api resource
        """
        with switch_db(model_game.CurrentGameData, 'test-db-alias') as CurrentGameData:
            def mockreturn(*args, **kwargs) -> Callable:
                game = crud_game.CRUDGame(CurrentGameData)
                game.create_new_game(args[0])

            monkeypatch.setattr(crud_game.game, "create_new_game", mockreturn)

            response = client.post(
                f"{settings.api_v1_str}/game/create",
                headers={
                    'Authorization': f'Bearer {settings.user0_token}'
                    }
                )
            assert response.status_code == 201, 'wrong status'
            assert CurrentGameData.objects().count() == 2, 'wrong count of data'

    def test_game_create_return_401(self, client: TestClient) -> None:
        """Test game create return 401 for unauthorized
        """
        response = client.post(f"{settings.api_v1_str}/game/create")
        assert response.status_code == 401, 'wrong status'
        assert response.json()['detail'] == 'Not authenticated', 'wrong detail'


class TestPreset:
    """Test game/preset
    """

    @pytest.mark.parametrize("priority", ["true", "false", "random", ])
    @pytest.mark.parametrize("faction", ["kgb", "cia", ])
    def test_preset_return_200(
        self,
        monkeypatch,
        connection: Generator,
        client: TestClient,
        priority: str,
        faction: str
            ) -> None:
        """Test game/preset returns 200
        """
        with switch_db(model_game.CurrentGameData, 'test-db-alias') as CurrentGameData:
            def mockreturn(*args, **kwargs) -> Callable:
                game = crud_game.CRUDGame(CurrentGameData)
                return game.get_current_game_data(settings.user0_login)

            monkeypatch.setattr(crud_game.game, "get_current_game_data", mockreturn)

            response = client.patch(
                f"{settings.api_v1_str}/game/preset?faction={faction}&priority={priority}",
                headers={
                    'Authorization': f'Bearer {settings.user0_token}'
                    }
                )
            assert response.status_code == 200, 'wrong status'
            assert CurrentGameData.objects().count() == 1, 'wrong count of data'

    def test_preset_return_422(
        self,
        monkeypatch,
        connection: Generator,
        client: TestClient,
            ) -> None:
        """Test game/preset return 422 if setted data uncorect
        """
        with switch_db(model_game.CurrentGameData, 'test-db-alias') as CurrentGameData:
            def mockreturn(*args, **kwargs) -> Callable:
                game = crud_game.CRUDGame(CurrentGameData)
                return game.get_current_game_data(settings.user0_login)

            monkeypatch.setattr(crud_game.game, "get_current_game_data", mockreturn)

            response = client.patch(
                f"{settings.api_v1_str}/game/preset?faction=abc",
                headers={
                    'Authorization': f'Bearer {settings.user0_token}'
                    }
                )
            assert response.status_code == 422, 'wrong status'

            response = client.patch(
                f"{settings.api_v1_str}/game/preset?faction=abc&priority=false",
                headers={
                    'Authorization': f'Bearer {settings.user0_token}'
                    }
                )
            assert response.status_code == 422, 'wrong status'

            response = client.patch(
                f"{settings.api_v1_str}/game/preset",
                headers={
                    'Authorization': f'Bearer {settings.user0_token}'
                    }
                )
            assert response.status_code == 422, 'wrong status'

    def test_preset_return_401(self, client: TestClient) -> None:
        """Test game create return 401 for unauthorized
        """
        response = client.patch(f"{settings.api_v1_str}/game/preset?faction=kgb&priority=true")
        assert response.status_code == 401, 'wrong status'
        assert response.json()['detail'] == 'Not authenticated', 'wrong detail'
