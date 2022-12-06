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
        user: crud_user.CRUDUser,
        game: crud_game.CRUDGame,
        connection: Generator,
        client: TestClient,
            ) -> None:
        """Test create new game api resource
        """
        def mock_user(*args, **kwargs) -> Callable:
            return user.get_by_login(settings.user0_login)

        def mock_game(*args, **kwargs) -> Callable:
            return game.create_new_game(args[0])

        def mock_process(*args, **kwargs) -> Callable:
            return game.get_game_processor(args[0])

        def mock_shuffle(*args, **kwargs) -> Callable:
            return game.deal_and_shuffle_decks(args[0])

        monkeypatch.setattr(crud_user.user, "get_by_login", mock_user)
        monkeypatch.setattr(crud_game.game, "create_new_game", mock_game)
        monkeypatch.setattr(crud_game.game, "get_game_processor", mock_process)
        monkeypatch.setattr(crud_game.game, "deal_and_shuffle_decks", mock_shuffle)

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


class TestPresetFaction:
    """Test game/preset/faction
    """

    @pytest.mark.parametrize("faction", ["kgb", "cia", ])
    def test_preset_faction_return_200(
        self,
        user: crud_user.CRUDUser,
        game: crud_game.CRUDGame,
        monkeypatch,
        connection: Generator,
        client: TestClient,
        faction: str
            ) -> None:
        """Test game/prese/faction returns 200
        """
        def mock_user(*args, **kwargs) -> Callable:
            return user.get_by_login(settings.user0_login)

        def mock_process(*args, **kwargs) -> Callable:
            return game.get_game_processor(args[0])

        def mock_faction(*args, **kwargs) -> Callable:
            return game.set_faction(args[0], args[1])

        monkeypatch.setattr(crud_user.user, "get_by_login", mock_user)
        monkeypatch.setattr(crud_game.game, "get_game_processor", mock_process)
        monkeypatch.setattr(crud_game.game, "set_faction", mock_faction)

        response = client.patch(
            f"{settings.api_v1_str}/game/preset/faction?q={faction}",
            headers={
                'Authorization': f'Bearer {settings.user0_token}'
                }
            )
        assert response.status_code == 200, 'wrong status'
        assert connection['CurrentGameData'].objects().count() == 1, 'wrong count of data'

        response = client.patch(
            f"{settings.api_v1_str}/game/preset/faction?q={faction}",
            headers={
                'Authorization': f'Bearer {settings.user0_token}'
                }
            )
        assert response.status_code == 409, 'wrong status'
        assert response.json()['detail'] == 'Factions yet setted for this game', \
            'wrong detail'

    def test_preset_faction_return_422_404(
        self,
        user: crud_user.CRUDUser,
        monkeypatch,
        client: TestClient,
            ) -> None:
        """Test game/prese/faction returns 422/404 if data incorrect
        """
        def mock_user(*args, **kwargs) -> Callable:
            return user.get_by_login(settings.user0_login)

        monkeypatch.setattr(crud_user.user, "get_by_login", mock_user)

        response = client.patch(
            f"{settings.api_v1_str}/game/preset/faction/q=abc",
            headers={
                'Authorization': f'Bearer {settings.user0_token}'
                }
            )
        assert response.status_code == 404, 'wrong status'

        response = client.patch(
            f"{settings.api_v1_str}/game/preset/faction",
            headers={
                'Authorization': f'Bearer {settings.user0_token}'
                }
            )
        assert response.status_code == 422, 'wrong status'

    def test_preset_faction_return_401(self, client: TestClient) -> None:
        """Test preset faction return 401
        """
        response = client.patch(f"{settings.api_v1_str}/game/preset/faction?q=kgb")
        assert response.status_code == 401, 'wrong status'
        assert response.json()['detail'] == 'Not authenticated', 'wrong detail'


class TestPresetPriority:
    """Test game/preset/priority
    """

    @pytest.mark.parametrize("priority", ["true", "false", "random", ])
    def test_preset_priority_return_200(
        self,
        user: crud_user.CRUDUser,
        game: crud_game.CRUDGame,
        monkeypatch,
        connection: Generator,
        client: TestClient,
        priority: str,
            ) -> None:
        """Test game/prese/priority returns 200
        """
        def mock_user(*args, **kwargs) -> Callable:
            return user.get_by_login(settings.user0_login)

        def mock_process(*args, **kwargs) -> Callable:
            return game.get_game_processor(args[0])

        def mock_priority(*args, **kwargs) -> Callable:
            return game.set_priority(args[0], args[1])

        monkeypatch.setattr(crud_user.user, "get_by_login", mock_user)
        monkeypatch.setattr(crud_game.game, "get_game_processor", mock_process)
        monkeypatch.setattr(crud_game.game, "set_priority", mock_priority)

        response = client.patch(
            f"{settings.api_v1_str}/game/preset/priority?q={priority}",
            headers={
                'Authorization': f'Bearer {settings.user0_token}'
                }
            )
        assert response.status_code == 200, 'wrong status'
        assert connection['CurrentGameData'].objects().count() == 1, 'wrong count of data'


        response = client.patch(
            f"{settings.api_v1_str}/game/preset/priority?q={priority}",
            headers={
                'Authorization': f'Bearer {settings.user0_token}'
                }
            )
        assert response.status_code == 409, 'wrong status'
        assert response.json()['detail'] == 'Priority yet setted for this game', \
            'wrong detail'

    def test_preset_priority_return_422_404(
        self,
        user: crud_user.CRUDUser,
        monkeypatch,
        client: TestClient,
            ) -> None:
        """Test game/prese/priority returns 422/404 if data incorrect
        """
        def mock_user(*args, **kwargs) -> Callable:
            return user.get_by_login(settings.user0_login)

        monkeypatch.setattr(crud_user.user, "get_by_login", mock_user)

        response = client.patch(
            f"{settings.api_v1_str}/game/preset/priority/q=abc",
            headers={
                'Authorization': f'Bearer {settings.user0_token}'
                }
            )
        assert response.status_code == 404, 'wrong status'

        response = client.patch(
            f"{settings.api_v1_str}/game/preset/priority",
            headers={
                'Authorization': f'Bearer {settings.user0_token}'
                }
            )
        assert response.status_code == 422, 'wrong status'

    def test_preset_faction_return_401(self, client: TestClient) -> None:
        """Test preset faction return 401
        """
        response = client.patch(f"{settings.api_v1_str}/game/preset/priority?q=true")
        assert response.status_code == 401, 'wrong status'
        assert response.json()['detail'] == 'Not authenticated', 'wrong detail'


class TestNextTurn:
    """Test game/next_turn
    """

    @pytest.fixture(scope="function")
    def mock_return(
        self,
        user: crud_user.CRUDUser,
        game: crud_game.CRUDGame,
        monkeypatch,
            ) -> None:
        """Mock user and game
        """

        def mock_user(*args, **kwargs) -> Callable:
            return user.get_by_login(settings.user0_login)

        def mock_process(*args, **kwargs) -> Callable:
            return game.get_game_processor(args[0])

        def mock_next_turn(*args, **kwargs) -> Callable:
            return game.set_next_turn(args[0])

        monkeypatch.setattr(crud_user.user, "get_by_login", mock_user)
        monkeypatch.setattr(crud_game.game, "get_game_processor", mock_process)
        monkeypatch.setattr(crud_game.game, "set_next_turn", mock_next_turn)

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
        assert connection['CurrentGameData'].objects().first() \
            .game_steps.game_turn == 1, 'wrong game_turn'

    def test_next_if_game_end_return_409(
        self,
        mock_return,
        game: crud_game.CRUDGame,
        client: TestClient,
            ) -> None:
        """Test turn can't be pushed if game end
        """
        data = game.get_current_game_data(settings.user0_login)
        data.game_steps.is_game_end = True
        data.save()

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
    def mock_return(
        self,
        user: crud_user.CRUDUser,
        game: crud_game.CRUDGame,
        monkeypatch,
            ) -> None:
        """Mock user and game
        """
        def mock_user(*args, **kwargs) -> Callable:
            return user.get_by_login(settings.user0_login)

        def mock_process(*args, **kwargs) -> Callable:
            game_proc = game.get_game_processor(args[0])
            game_proc = game.deal_and_shuffle_decks(game_proc)
            game_proc = game.set_faction(crud_game.Faction.KGB, game_proc)
            game_proc = game.set_priority(crud_game.Priority.TRUE, game_proc)
            return game_proc

        def mock_next_phase(*args, **kwargs) -> Callable:
            return game.set_next_phase(args[0])

        def mock_conditions(*args, **kwargs) -> Callable:
            return game.set_phase_conditions_after_next(args[0])

        monkeypatch.setattr(crud_user.user, "get_by_login", mock_user)
        monkeypatch.setattr(crud_game.game, "get_game_processor", mock_process)
        monkeypatch.setattr(crud_game.game, "set_next_phase", mock_next_phase)
        monkeypatch.setattr(crud_game.game, "set_phase_conditions_after_next", mock_conditions)

    def test_next_phase_return_200(
        self,
        mock_return,
        connection: Generator,
        client: TestClient,
            ) -> None:
        """Test game/next set next phase
        """
        current = connection['CurrentGameData'].objects().first()
        assert current.game_steps.turn_phase is None, 'wrong turn_tphase'
        assert current.game_decks.mission_card is None, 'wrong mission card'

        response = client.patch(
            f"{settings.api_v1_str}/game/next_phase",
            headers={
                'Authorization': f'Bearer {settings.user0_token}'
                }
            )
        assert response.status_code == 200, 'wrong status'

        current = connection['CurrentGameData'].objects().first()
        assert current.game_steps.turn_phase == settings.phases[0], 'wrong turn_phase'
        assert isinstance(current.game_decks.mission_card, str), 'wrong mission card'

    def test_next_phase_if_last_return_409(
        self,
        mock_return,
        game: crud_game.CRUDGame,
        client: TestClient,
            ) -> None:
        """Test last phases cant'be pushed
        """
        data = game.get_current_game_data(settings.user0_login)
        data.game_steps.is_game_end = True
        data.save()

        response = client.patch(
            f"{settings.api_v1_str}/game/next_phase",
            headers={
                'Authorization': f'Bearer {settings.user0_token}'
                }
            )
        assert response.status_code == 409, 'wrong status'
        assert response.json()['detail'] == "Something can't be changed, because game is end"

    def test_next_turn_return_401(self, client: TestClient) -> None:
        """Test next phase return 401 for unauthorized
        """
        response = client.patch(f"{settings.api_v1_str}/game/next_phase")
        assert response.status_code == 401, 'wrong status'
        assert response.json()['detail'] == 'Not authenticated', 'wrong detail'
