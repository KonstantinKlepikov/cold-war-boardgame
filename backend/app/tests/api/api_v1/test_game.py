import pytest
from typing import Callable, Generator
from fastapi.testclient import TestClient
from app.crud import crud_game, crud_user
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
        def mockreturn(*args, **kwargs) -> Callable:
            game = crud_game.CRUDGame(connection['CurrentGameData'])
            game.create_new_game(args[0])

        def mock_user(*args, **kwargs) -> Callable:
            user = crud_user.CRUDUser(connection['User'])
            return user.get_by_login(settings.user0_login)

        monkeypatch.setattr(crud_game.game, "create_new_game", mockreturn)
        monkeypatch.setattr(crud_user.user, "get_by_login", mock_user)

        response = client.post(
            f"{settings.api_v1_str}/game/create",
            headers={
                'Authorization': f'Bearer {settings.user0_token}'
                }
            )
        assert response.status_code == 201, 'wrong status'
        assert connection['CurrentGameData'].objects().count() == 2, 'wrong count of data'

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
        def mockreturn(*args, **kwargs) -> Callable:
            game = crud_game.CRUDGame(connection['CurrentGameData'])
            game.create_new_game(args[0])

        def mock_user(*args, **kwargs) -> Callable:
            user = crud_user.CRUDUser(connection['User'])
            return user.get_by_login(settings.user0_login)

        monkeypatch.setattr(crud_game.game, "create_new_game", mockreturn)
        monkeypatch.setattr(crud_user.user, "get_by_login", mock_user)

        response = client.patch(
            f"{settings.api_v1_str}/game/preset?faction={faction}&priority={priority}",
            headers={
                'Authorization': f'Bearer {settings.user0_token}'
                }
            )
        assert response.status_code == 200, 'wrong status'
        assert connection['CurrentGameData'].objects().count() == 1, 'wrong count of data'

    def test_preset_return_422(
        self,
        monkeypatch,
        connection: Generator,
        client: TestClient,
            ) -> None:
        """Test game/preset return 422 if setted data uncorect
        """
        def mockreturn(*args, **kwargs) -> Callable:
            game = crud_game.CRUDGame(connection['CurrentGameData'])
            game.create_new_game(args[0])

        def mock_user(*args, **kwargs) -> Callable:
            user = crud_user.CRUDUser(connection['User'])
            return user.get_by_login(settings.user0_login)

        monkeypatch.setattr(crud_game.game, "create_new_game", mockreturn)
        monkeypatch.setattr(crud_user.user, "get_by_login", mock_user)

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


class TestNextTurn:
    """Test game/next_turn
    """

    @pytest.fixture(scope="function")
    def mock_return(self, monkeypatch, connection: Generator) -> None:
        """Mock user and game
        """

        def mock_game(*args, **kwargs) -> Callable:
            game = crud_game.CRUDGame(connection['CurrentGameData'])
            game.create_new_game(args[0])

        def mock_user(*args, **kwargs) -> Callable:
            user = crud_user.CRUDUser(connection['User'])
            return user.get_by_login(settings.user0_login)

        monkeypatch.setattr(crud_user.user, "get_by_login", mock_user)
        monkeypatch.setattr(crud_game.game, "create_new_game", mock_game)


    def test_next_turn_return_200(
        self,
        mock_return,
        connection: Generator,
        client: TestClient,
            ) -> None:
        """Test game/next set next turn
        """
        response = client.patch(
            f"{settings.api_v1_str}/game/next_turn",
            headers={
                'Authorization': f'Bearer {settings.user0_token}'
                }
            )
        assert response.status_code == 200, 'wrong status'

    def test_next_if_game_end_return_409(
        self,
        monkeypatch,
        connection: Generator,
        client: TestClient,
            ) -> None:
        """Test turn can't be pushed if game end
        """
        def mock_game(*args, **kwargs) -> Callable:
            game = crud_game.CRUDGame(connection['CurrentGameData'])
            data = game.get_current_game_data(settings.user0_login)
            data.game_steps.is_game_end = True
            data.save()
            return game.get_current_game_data(settings.user0_login)

        def mock_user(*args, **kwargs) -> Callable:
            user = crud_user.CRUDUser(connection['User'])
            return user.get_by_login(settings.user0_login)

        monkeypatch.setattr(crud_user.user, "get_by_login", mock_user)
        monkeypatch.setattr(crud_game.game, "get_current_game_data", mock_game)

        response = client.patch(
            f"{settings.api_v1_str}/game/next_turn",
            headers={
                'Authorization': f'Bearer {settings.user0_token}'
                }
            )
        assert response.status_code == 409, 'wrong status'
        assert response.json()['detail'] == "Something can't be changed, because game is end"

    def test_next_turn_return_401(self, client: TestClient) -> None:
        """Test next turn return 401 for unauthorized
        """
        response = client.patch(f"{settings.api_v1_str}/game/next_turn")
        assert response.status_code == 401, 'wrong status'
        assert response.json()['detail'] == 'Not authenticated', 'wrong detail'


class TestNextPhase:
    """Test game/next_phase
    """

    @pytest.fixture(scope="function")
    def mock_return(self, monkeypatch, connection: Generator) -> None:
        """Mock user and game
        """

        def mock_game(*args, **kwargs) -> Callable:
            game = crud_game.CRUDGame(connection['CurrentGameData'])
            game.create_new_game(args[0])

        def mock_user(*args, **kwargs) -> Callable:
            user = crud_user.CRUDUser(connection['User'])
            return user.get_by_login(settings.user0_login)

        monkeypatch.setattr(crud_user.user, "get_by_login", mock_user)
        monkeypatch.setattr(crud_game.game, "create_new_game", mock_game)

    def test_next_phase_return_200(
        self,
        mock_return,
        connection: Generator,
        client: TestClient,
            ) -> None:
        """Test game/next set next phase
        """
        response = client.patch(
            f"{settings.api_v1_str}/game/next_phase",
            headers={
                'Authorization': f'Bearer {settings.user0_token}'
                }
            )
        assert response.status_code == 200, 'wrong status'

    def test_next_phase_if_last_return_409(
        self,
        monkeypatch,
        connection: Generator,
        client: TestClient,
            ) -> None:
        """Test last phases cant'be pushed
        """
        def mock_game(*args, **kwargs) -> Callable:
            game = crud_game.CRUDGame(connection['CurrentGameData'])
            data = game.get_current_game_data(settings.user0_login)
            data.game_steps.turn_phase = 'detente'
            data.save()
            return game.get_current_game_data(settings.user0_login)

        def mock_user(*args, **kwargs) -> Callable:
            user = crud_user.CRUDUser(connection['User'])
            return user.get_by_login(settings.user0_login)

        monkeypatch.setattr(crud_user.user, "get_by_login", mock_user)
        monkeypatch.setattr(crud_game.game, "get_current_game_data", mock_game)

        response = client.patch(
            f"{settings.api_v1_str}/game/next_phase",
            headers={
                'Authorization': f'Bearer {settings.user0_token}'
                }
            )
        assert response.status_code == 409, 'wrong status'
        assert response.json()['detail'] == "This phase is last in a turn. " \
                                            "Change turn number " \
                                            "before get next phase", 'wrong detail'

    def test_next_turn_return_401(self, client: TestClient) -> None:
        """Test next phase return 401 for unauthorized
        """
        response = client.patch(f"{settings.api_v1_str}/game/next_phase")
        assert response.status_code == 401, 'wrong status'
        assert response.json()['detail'] == 'Not authenticated', 'wrong detail'
