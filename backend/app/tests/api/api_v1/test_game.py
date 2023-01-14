import pytest
from typing import Callable, Generator
from fastapi.testclient import TestClient
from app.crud import crud_game, crud_user
from app.core import processor_game
from app.config import settings
from app.constructs import Phases


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

        monkeypatch.setattr(crud_user.user, "get_by_login", mock_user)
        monkeypatch.setattr(crud_game.game, "create_new_game", mock_game)
        monkeypatch.setattr(crud_game.game, "get_game_processor", mock_process)

        response = client.post(
            f"{settings.api_v1_str}/game/create",
            headers={
                'Authorization': f'Bearer {settings.user0_token}'
                }
            )
        assert response.status_code == 201, 'wrong status'
        assert connection['CurrentGameData'].objects().count() == 2, 'wrong count of data'
        # assert connection['CurrentGameData'].objects().count() == 3, 'wrong count of data'


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

        monkeypatch.setattr(crud_user.user, "get_by_login", mock_user)
        monkeypatch.setattr(crud_game.game, "get_game_processor", mock_process)

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
        assert response.json()['detail'] == 'You cant change faction because is choosen yet', \
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


class TestNextTurn:
    """Test game/next_turn
    """

    @pytest.fixture(scope="function")
    def mock_return(
        self,
        user: crud_user.CRUDUser,
        game: crud_game.CRUDGame,
        started_game_proc: processor_game.GameProcessor,
        monkeypatch,
            ) -> None:
        """Mock user and game
        """

        def mock_user(*args, **kwargs) -> Callable:
            return user.get_by_login(settings.user0_login)

        def mock_process(*args, **kwargs) -> Callable:
            return started_game_proc

        monkeypatch.setattr(crud_user.user, "get_by_login", mock_user)
        monkeypatch.setattr(crud_game.game, "get_game_processor", mock_process)

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

    def test_next_turn_if_game_end_return_409(
        self,
        mock_return,
        started_game_proc: processor_game.GameProcessor,
        client: TestClient,
            ) -> None:
        """Test turn can't be pushed if game end
        """
        started_game_proc.G.c.steps.is_game_end = True

        response = client.patch(
            f"{settings.api_v1_str}/game/next_turn",
            headers={
                'Authorization': f'Bearer {settings.user0_token}'
                }
            )
        assert response.status_code == 409, 'wrong status'
        assert response.json()['detail'] == "Something can't be changed, because game is end"


class TestNextPhase:
    """Test game/next_phase
    """

    @pytest.fixture(scope="function")
    def mock_return(
        self,
        user: crud_user.CRUDUser,
        started_game_proc_fact: processor_game.GameProcessor,
        monkeypatch,
            ) -> None:
        """Mock user and game
        """
        def mock_user(*args, **kwargs) -> Callable:
            return user.get_by_login(settings.user0_login)

        def mock_process(*args, **kwargs) -> Callable:
            return started_game_proc_fact

        monkeypatch.setattr(crud_user.user, "get_by_login", mock_user)
        monkeypatch.setattr(crud_game.game, "get_game_processor", mock_process)

    def test_next_phase_return_200(
        self,
        mock_return,
        connection: Generator,
        client: TestClient,
            ) -> None:
        """Test game/next set next phase
        """
        current = connection['CurrentGameData'].objects().first()
        assert current.game_steps.turn_phase is None, 'wrong turn_phase'
        assert current.game_decks.mission_card is None, 'wrong mission card'

        response = client.patch(
            f"{settings.api_v1_str}/game/next_phase",
            headers={
                'Authorization': f'Bearer {settings.user0_token}'
                }
            )
        assert response.status_code == 200, 'wrong status'

        current = connection['CurrentGameData'].objects().first()
        assert current.game_steps.turn_phase == Phases.BRIEFING.value, 'wrong turn_phase'
        assert isinstance(current.game_decks.mission_card, str), 'wrong mission card'

    def test_next_phase_return_200_and_get_from_briefing(
        self,
        mock_return,
        connection: Generator,
        client: TestClient,
            ) -> None:
        """Test game/next set next phase from briefing
        """
        client.patch(
            f"{settings.api_v1_str}/game/next_phase",
            headers={
                'Authorization': f'Bearer {settings.user0_token}'
                }
            )
        response = client.patch(
            f"{settings.api_v1_str}/game/next_phase",
            headers={
                'Authorization': f'Bearer {settings.user0_token}'
                }
            )
        assert response.status_code == 200, 'wrong status'

        current = connection['CurrentGameData'].objects().first()
        assert current.game_steps.turn_phase == Phases.PLANNING.value, 'wrong turn_phase'
        assert isinstance(current.game_decks.mission_card, str), 'wrong mission card'

    def test_next_phase_if_last_return_409(
        self,
        mock_return,
        started_game_proc_fact: processor_game.GameProcessor,
        client: TestClient,
            ) -> None:
        """Test last phases cant'be pushed
        """
        started_game_proc_fact.G.c.steps.is_game_end = True

        response = client.patch(
            f"{settings.api_v1_str}/game/next_phase",
            headers={
                'Authorization': f'Bearer {settings.user0_token}'
                }
            )
        assert response.status_code == 409, 'wrong status'
        assert response.json()['detail'] == "Something can't be changed, because game is end"


class TestAnalyst:
    """Test /phase/briefing/analyst_look
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

        monkeypatch.setattr(crud_user.user, "get_by_login", mock_user)
        monkeypatch.setattr(crud_game.game, "get_game_processor", mock_process)

    def test_analyst_get_return_200(
        self,
        mock_return,
        connection: Generator,
        client: TestClient,
            ) -> None:
        """Test /phase/briefing/analyst_look returns 200
        """
        current = connection['CurrentGameData'].objects().first()
        current.game_steps.turn_phase = Phases.BRIEFING.value
        current.players[0].abilities = ['Analyst', ]
        current.save()

        response = client.patch(
            f"{settings.api_v1_str}/game/phase/briefing/analyst_look",
            headers={
                'Authorization': f'Bearer {settings.user0_token}'
                }
            )
        assert response.status_code == 200, 'wrong status'
        assert len(response.json()["top_cards"]) == 3, 'no top cards in result'

        current = connection['CurrentGameData'].objects().first()
        assert len(current.players[0].player_cards.group_cards) == 3, \
            'wrong player groups'

    # TODO: here test 409

    def test_analyst_arrange_return_200(
        self,
        mock_return,
        connection: Generator,
        client: TestClient,
            ) -> None:
        """Test /phase/briefing/analyst_look returns 200
        """
        current = connection['CurrentGameData'].objects().first()
        current.game_steps.turn_phase = Phases.BRIEFING.value
        current.players[0].abilities = ['Analyst', ]
        current.save()
        top = current.game_decks.group_deck.deck[-3:]
        top.reverse()

        response = client.patch(
            f"{settings.api_v1_str}/game/phase/briefing/analyst_arrange",
            headers={
                'Authorization': f'Bearer {settings.user0_token}'
                },
            json={"top_cards": top},
            )
        assert response.status_code == 200, 'wrong status'

        current = connection['CurrentGameData'].objects().first()
        assert current.game_decks.group_deck.deck[-3:] == top, \
            'not arranged'

    # TODO: here test 409


class TestAutorizationError:
    """Test not acessed unautorized user
    """

    def test_game_create_return_401(self, client: TestClient) -> None:
        """Test game create return 401 for unauthorized
        """
        response = client.post(f"{settings.api_v1_str}/game/create")
        assert response.status_code == 401, 'wrong status'
        assert response.json()['detail'] == 'Not authenticated', 'wrong detail'

    def test_preset_faction_return_401(self, client: TestClient) -> None:
        """Test preset faction return 401
        """
        response = client.patch(f"{settings.api_v1_str}/game/preset/faction?q=kgb")
        assert response.status_code == 401, 'wrong status'
        assert response.json()['detail'] == 'Not authenticated', 'wrong detail'

    def test_next_turn_return_401(self, client: TestClient) -> None:
        """Test next turn return 401 for unauthorized
        """
        response = client.patch(f"{settings.api_v1_str}/game/next_turn")
        assert response.status_code == 401, 'wrong status'
        assert response.json()['detail'] == 'Not authenticated', 'wrong detail'

    def test_next_turn_return_401(self, client: TestClient) -> None:
        """Test next phase return 401 for unauthorized
        """
        response = client.patch(f"{settings.api_v1_str}/game/next_phase")
        assert response.status_code == 401, 'wrong status'
        assert response.json()['detail'] == 'Not authenticated', 'wrong detail'

    def test_analyst_get_return_401(self, client: TestClient) -> None:
        """Test analyst_look return 401 for unauthorized
        """
        response = client.patch(
            f"{settings.api_v1_str}/game/phase/briefing/analyst_arrange",
                )
        assert response.status_code == 401, 'wrong status'
        assert response.json()['detail'] == 'Not authenticated', 'wrong detail'

    def test_analyst_arrange_return_401(self, client: TestClient) -> None:
        """Test analyst_arrnage return 401 for unauthorized
        """
        response = client.patch(
            f"{settings.api_v1_str}/game/phase/briefing/analyst_arrange",
            json={"top_cards": ['one', 'two', 'three']},
                )
        assert response.status_code == 401, 'wrong status'
        assert response.json()['detail'] == 'Not authenticated', 'wrong detail'
