import pytest
from typing import Callable, Generator
from fastapi.testclient import TestClient
from app.crud import crud_game_current, crud_user
from app.core import logic
from app.config import settings
from app.constructs import Factions, Agents, Phases, Groups


class TestCreateNewGame:
    """Test game/create
    """

    def test_game_create_return_201(
        self,
        monkeypatch,
        user: crud_user.CRUDUser,
        game: crud_game_current.CRUDGame,
        connection: Generator,
        client: TestClient,
            ) -> None:
        """Test create new game api resource
        """
        def mock_user(*args, **kwargs) -> Callable:
            return user.get_by_login(settings.user0_login)

        def mock_game(*args, **kwargs) -> Callable:
            return game.create_new_game(args[0])

        monkeypatch.setattr(crud_user.user, "get_by_login", mock_user)
        monkeypatch.setattr(crud_game_current.game, "create_new_game", mock_game)

        response = client.post(
            f"{settings.api_v1_str}/game/create",
            headers={
                'Authorization': f'Bearer {settings.user0_token}'
                }
            )
        assert response.status_code == 201, f'{response.content=}'
        assert connection['CurrentGameData'].objects().count() == 2, 'wrong count of data'


class TestPresetFaction:
    """Test game/preset
    """

    @pytest.mark.parametrize("faction", ["kgb", "cia", ])
    def test_preset_faction_return_200_409(
        self,
        user: crud_user.CRUDUser,
        game: crud_game_current.CRUDGame,
        monkeypatch,
        # connection: Generator,
        client: TestClient,
        faction: str
            ) -> None:
        """Test game/prese/faction returns 200
        """
        def mock_user(*args, **kwargs) -> Callable:
            return user.get_by_login(settings.user0_login)

        def mock_process(*args, **kwargs) -> Callable:
            return game.get_last_game(args[0])

        monkeypatch.setattr(crud_user.user, "get_by_login", mock_user)
        monkeypatch.setattr(crud_game_current.game, "get_last_game", mock_process)

        response = client.patch(
            f"{settings.api_v1_str}/game/preset?q={faction}",
            headers={
                'Authorization': f'Bearer {settings.user0_token}'
                }
            )
        assert response.status_code == 200, f'{response.content=}'
        # assert connection['CurrentGameData'].objects().count() == 1, 'wrong count of data'

        response = client.patch(
            f"{settings.api_v1_str}/game/preset?q={faction}",
            headers={
                'Authorization': f'Bearer {settings.user0_token}'
                }
            )
        assert response.status_code == 409, f'{response.content=}'
        assert response.json()['detail'] == 'You cant change faction because is chosen yet', \
            'wrong detail'

    def test_preset_faction_return_422(
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
            f"{settings.api_v1_str}/game/preset?q=abc",
            headers={
                'Authorization': f'Bearer {settings.user0_token}'
                }
            )
        assert response.status_code == 422, f'{response.content=}'

        response = client.patch(
            f"{settings.api_v1_str}/game/preset",
            headers={
                'Authorization': f'Bearer {settings.user0_token}'
                }
            )
        assert response.status_code == 422, f'{response.content=}'


class TestNextTurn:
    """Test game/next_turn
    """

    @pytest.fixture(scope="function")
    def mock_return(
        self,
        user: crud_user.CRUDUser,
        started_game: crud_game_current.CRUDGame,
        game_logic: logic.GameLogic,
        monkeypatch,
            ) -> None:
        """Mock user and game
        """
        game_logic.proc.steps.last = game_logic.proc.steps.c.by_id(Phases.DETENTE)
        started_game.save_game_logic(game_logic)

        def mock_user(*args, **kwargs) -> Callable:
            return user.get_by_login(settings.user0_login)

        def mock_process(*args, **kwargs) -> Callable:
            return started_game.get_last_game(args[0])

        monkeypatch.setattr(crud_user.user, "get_by_login", mock_user)
        monkeypatch.setattr(crud_game_current.game, "get_last_game", mock_process)

    def test_next_turn_return_200(
        self,
        mock_return,
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
        assert response.status_code == 200, f'{response.content=}'

    def test_next_turn_if_game_end_return_409(
        self,
        mock_return,
        started_game: crud_game_current.CRUDGame,
        game_logic: logic.GameLogic,
        client: TestClient,
            ) -> None:
        """Test turn can't be pushed if game end
        """
        game_logic.proc.steps.is_game_ends = True
        started_game.save_game_logic(game_logic)

        response = client.patch(
            f"{settings.api_v1_str}/game/next_turn",
            headers={
                'Authorization': f'Bearer {settings.user0_token}'
                }
            )
        assert response.status_code == 409, f'{response.content=}'
        assert response.json()['detail'] == "Something can't be changed, because game is end"

class TestNextPhase:
    """Test game/next_phase
    """

    @pytest.fixture(scope="function")
    def mock_return(
        self,
        user: crud_user.CRUDUser,
        started_game: crud_game_current.CRUDGame,
        game_logic: logic.GameLogic,
        monkeypatch,
            ) -> None:
        """Mock user and game
        """
        game_logic.proc.players.player.faction = Factions.KGB
        game_logic.proc.players.opponent.faction = Factions.CIA
        game_logic.proc.players.player.agents.current[0].is_agent_x = True
        game_logic.proc.players.opponent.agents.current[0].is_agent_x = True
        game_logic.proc.players.player.has_balance = True
        game_logic.proc.players.opponent.has_balance= False
        game_logic.proc.decks.objectives.pop()
        started_game.save_game_logic(game_logic)

        def mock_user(*args, **kwargs) -> Callable:
            return user.get_by_login(settings.user0_login)

        def mock_process(*args, **kwargs) -> Callable:
            return started_game.get_last_game(args[0])

        monkeypatch.setattr(crud_user.user, "get_by_login", mock_user)
        monkeypatch.setattr(crud_game_current.game, "get_last_game", mock_process)

    def test_next_phase_return_200_and_get_from_briefing(
        self,
        mock_return,
        client: TestClient,
            ) -> None:
        """Test game/next set next phase from briefing
        """
        response = client.patch(
            f"{settings.api_v1_str}/game/next_phase",
            headers={
                'Authorization': f'Bearer {settings.user0_token}'
                }
            )
        assert response.status_code == 200, f'{response.content=}'

    # TODO: test her errors

    def test_next_phase_if_last_return_409(
        self,
        mock_return,
        started_game: crud_game_current.CRUDGame,
        game_logic: logic.GameLogic,
        client: TestClient,
            ) -> None:
        """Test last phases cant'be pushed
        """
        game_logic.proc.steps.is_game_ends = True
        started_game.save_game_logic(game_logic)

        response = client.patch(
            f"{settings.api_v1_str}/game/next_phase",
            headers={
                'Authorization': f'Bearer {settings.user0_token}'
                }
            )
        assert response.status_code == 409, f'{response.content=}'
        assert response.json()['detail'] == "Something can't be changed, because game is end"


class TestAnalyst:
    """Test /phase/briefing/analyst_look
    """

    @pytest.fixture(scope="function")
    def mock_return(
        self,
        user: crud_user.CRUDUser,
        started_game: crud_game_current.CRUDGame,
        game_logic: logic.GameLogic,
        monkeypatch,
            ) -> None:
        """Mock user and game
        """
        game_logic.proc.players.player.awaiting_abilities.append(Agents.ANALYST)
        started_game.save_game_logic(game_logic)

        def mock_user(*args, **kwargs) -> Callable:
            return user.get_by_login(settings.user0_login)

        def mock_process(*args, **kwargs) -> Callable:
            return started_game.get_last_game(args[0])

        monkeypatch.setattr(crud_user.user, "get_by_login", mock_user)
        monkeypatch.setattr(crud_game_current.game, "get_last_game", mock_process)

    def test_analyst_get_return_200(
        self,
        mock_return,
        client: TestClient,
            ) -> None:
        """Test /phase/briefing/analyst_look returns 200
        """
        response = client.patch(
            f"{settings.api_v1_str}/game/phase/briefing/analyst_look",
            headers={
                'Authorization': f'Bearer {settings.user0_token}'
                }
            )
        assert response.status_code == 200, f'{response.content=}'

    # TODO: here test 409

    def test_analyst_arrange_return_200(
        self,
        mock_return,
        client: TestClient,
        game_logic: logic.GameLogic,
            ) -> None:
        """Test /phase/briefing/analyst_look returns 200
        """
        top = game_logic.proc.decks.groups.current_ids[-3:]
        top.reverse()

        response = client.patch(
            f"{settings.api_v1_str}/game/phase/briefing/analyst_arrange",
            headers={
                'Authorization': f'Bearer {settings.user0_token}'
                },
            json=top,
            )
        assert response.status_code == 200, f'{response.content=}'

    # TODO: here test 409


class TestSetAgentX:
    """Test set_agent_x
    """

    @pytest.fixture(scope="function")
    def mock_return(
        self,
        user: crud_user.CRUDUser,
        started_game: crud_game_current.CRUDGame,
        game_logic: logic.GameLogic,
        monkeypatch,
            ) -> None:
        """Mock user and game
        """
        game_logic.proc.steps.last = game_logic.proc.steps.c.by_id(Phases.PLANNING)
        started_game.save_game_logic(game_logic)

        def mock_user(*args, **kwargs) -> Callable:
            return user.get_by_login(settings.user0_login)

        def mock_process(*args, **kwargs) -> Callable:
            return started_game.get_last_game(args[0])

        monkeypatch.setattr(crud_user.user, "get_by_login", mock_user)
        monkeypatch.setattr(crud_game_current.game, "get_last_game", mock_process)

    def test_set_agent_x_return_200(
        self,
        mock_return,
        client: TestClient,
            ) -> None:
        """Test /phase/planning/agent_x returns 200
        """
        response = client.patch(
            f"{settings.api_v1_str}/game/phase/planning/agent_x?q={Agents.DEPUTY.value}",
            headers={
                'Authorization': f'Bearer {settings.user0_token}'
                }
            )
        assert response.status_code == 200, f'{response.content=}'

    def test_set_agent_x_return_422(
        self,
        mock_return,
        client: TestClient,
            ) -> None:
        """Test /phase/planning/agent_x returns 422
        """
        response = client.patch(
            f"{settings.api_v1_str}/game/phase/planning/agent_x?q=wrong_agent",
            headers={
                'Authorization': f'Bearer {settings.user0_token}'
                }
            )
        assert response.status_code == 422, f'{response.content=}'

    def test_set_agent_x_return_409(
        self,
        mock_return,
        started_game: crud_game_current.CRUDGame,
        game_logic: logic.GameLogic,
        client: TestClient,
            ) -> None:
        """Test /phase/planning/agent_x returns 409
        """
        game_logic.proc.steps.last = game_logic.proc.steps.c.by_id(Phases.BRIEFING)
        started_game.save_game_logic(game_logic)

        response = client.patch(
            f"{settings.api_v1_str}/game/phase/planning/agent_x?q={Agents.DEPUTY.value}",
            headers={
                'Authorization': f'Bearer {settings.user0_token}'
                }
            )
        assert response.status_code == 409, f'{response.content=}'


class TestInfluenceStruggleGroupsResources:
    """Test influence struggle groups subgame
    """

    @pytest.fixture(scope="function")
    def mock_return(
        self,
        user: crud_user.CRUDUser,
        started_game: crud_game_current.CRUDGame,
        game_logic: logic.GameLogic,
        monkeypatch,
            ) -> None:
        """Mock user and game
        """
        game_logic.proc.steps.last = game_logic.proc.steps.c.by_id(Phases.INFLUENCE)
        game_logic.proc.decks.groups.owned_by_player.append(game_logic.proc.decks.groups.pop())
        started_game.save_game_logic(game_logic)

        def mock_user(*args, **kwargs) -> Callable:
            return user.get_by_login(settings.user0_login)

        def mock_process(*args, **kwargs) -> Callable:
            return started_game.get_last_game(args[0])

        monkeypatch.setattr(crud_user.user, "get_by_login", mock_user)
        monkeypatch.setattr(crud_game_current.game, "get_last_game", mock_process)

    def test_recruit_return_200(
        self,
        mock_return,
        client: TestClient,
            ) -> None:
        """Test /game/influence_struggle/recruit returns 200
        """
        response = client.patch(
            f"{settings.api_v1_str}/game/influence_struggle/recruit",
            headers={
                'Authorization': f'Bearer {settings.user0_token}'
                }
            )
        assert response.status_code == 200, f'{response.content=}'

    def test_pass_return_200(
        self,
        mock_return,
        client: TestClient,
            ) -> None:
        """Test /game/influence_struggle/pass returns 200
        """
        response = client.patch(
            f"{settings.api_v1_str}/game/influence_struggle/pass",
            headers={
                'Authorization': f'Bearer {settings.user0_token}'
                }
            )
        assert response.status_code == 200, f'{response.content=}'

    def test_activate_return_200(
        self,
        mock_return,
        client: TestClient,
            ) -> None:
        """Test /game/influence_struggle/pass returns 200
        """
        response = client.patch(
            f"{settings.api_v1_str}/game/influence_struggle/activate?source{Groups.ARTISTS}",
            headers={
                'Authorization': f'Bearer {settings.user0_token}'
                }
            )
        assert response.status_code == 200, f'{response.content=}'



class TestAutorizationError:
    """Test not acessed unautorized user
    """

    @pytest.mark.parametrize("test_input", [
        '/game/preset?q=kgb',
        '/game/next_turn',
        '/game/next_phase',
        '/game/phase/briefing/analyst_look',
        '/game/influence_struggle/recruit',
        '/game/influence_struggle/pass',
        f'/game/influence_struggle/activate?source{Groups.ARTISTS}',
            ])
    def test_resource_return_401(
        self,
        test_input: str,
        client: TestClient
            ) -> None:
        """Test resource return 401 for unauthorized
        """
        response = client.patch(f"{settings.api_v1_str}{test_input}")
        assert response.status_code == 401, f'{test_input=}, {response.content=}'
        assert response.json()['detail'] == 'Not authenticated', 'wrong detail'

    def test_create_the_game_return_401(self, client: TestClient) -> None:
        """Test create game return 401
        """
        response = client.post(f"{settings.api_v1_str}/game/create")
        assert response.status_code == 401, f'{response.content=}'
        assert response.json()['detail'] == 'Not authenticated', 'wrong detail'

    def test_analyst_arrange_return_401(self, client: TestClient) -> None:
        """Test analyst_arrnage return 401 for unauthorized
        """
        response = client.patch(
            f"{settings.api_v1_str}/game/phase/briefing/analyst_arrange",
            json=['one', 'two', 'three'],
                )
        assert response.status_code == 401, f'{response.content=}'
        assert response.json()['detail'] == 'Not authenticated', 'wrong detail'
