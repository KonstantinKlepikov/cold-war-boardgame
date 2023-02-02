import pytest
from typing import Generator, Union, Any
from mongoengine import disconnect, connect
from mongoengine.context_managers import switch_db
# from fastapi.testclient import TestClient
from app.main import app
from app.config import settings
from app.models import model_user, model_game_current, model_game_static
from app.crud import crud_game_static, crud_user, crud_game_current
from app.core.logic import GameLogic
# from app.constructs import Agents, Groups, Objectives
from app.db.init_db import init_db_cards, init_db_users, get_yaml



@pytest.fixture(scope="session")
def users_data() -> dict[str, str]:
    """Get user data
    """
    return {
        'login': settings.user0_login,
        'password': settings.user0_password,
        'hashed_password': settings.user0_hashed_password,
            }


@pytest.fixture(scope='session')
def cards_data() -> dict[str, Any]:
    """Get cards data
    """

    cards = get_yaml('app/db/data/converted.yaml')
    return {
        'agents': cards['agent_cards'],
        'groups': cards['group_cards'],
        'objectives': cards['objective_cards'],
            }


@pytest.fixture(scope="session")
def db_user(users_data: dict[str, str]) -> dict[str, str]:
    """Get db user data
    """
    return {
        'login': users_data['login'],
        'hashed_password': users_data['hashed_password'],
        'is_active': True,
            }


@pytest.fixture(scope="session")
def db_game_data(
    cards_data: dict[str, Any],
        ) -> dict[str, Any]:
    """Get game data
    """
    return {
        'players':
            {
                'player': {
                    'login': settings.user0_login,
                    'agents':
                        {
                            'current': [
                                {'name': card['name']} for card in cards_data['agents']
                            ]
                        }
                    },
                'opponent': {
                    'login': settings.user2_login,
                    'agents':
                        {
                            'current': [
                                {'name': card['name']} for card in cards_data['agents']
                            ]
                        }
                    },
                },
        'decks':
            {
                'groups':
                    {
                        'current': [
                            {'name': card['name']} for card in cards_data['groups']
                        ]
                     },
                'objectives':
                    {
                        'current': [
                            {'name': card['name']} for card in cards_data['objectives']
                        ]
                    },
                },
            }


# @pytest.fixture(scope="function")
# def client() -> Generator:
#     with TestClient(app) as c:
#         yield c


@pytest.fixture(scope="function")
def connection(
    db_game_data: dict[str, Any],
        ) -> Generator:
    """Get mock mongodb
    """
    try:
        conn = connect(
            host=settings.test_mongodb_url,
            name='test-db',
            alias='test-db-alias'
                )
        conn.drop_database('test-db')

        init_db_cards('test-db-alias')
        init_db_users('test-db-alias')

        with switch_db(model_user.User, 'test-db-alias') as User, \
            switch_db(model_game_current.CurrentGameData, 'test-db-alias') as CurrentGameData, \
            switch_db(model_game_static.Agent, 'test-db-alias') as Agent, \
            switch_db(model_game_static.Group, 'test-db-alias') as Group, \
            switch_db(model_game_static.Objective, 'test-db-alias') as Objective \
                :

            # init test user current game
            game = CurrentGameData(**db_game_data)
            game.save()


            yield {
                'connection': conn,
                'User': User,
                'CurrentGameData': CurrentGameData,
                'Agent': Agent,
                'Group': Group,
                'Objective': Objective,
                }

    finally:
        conn.drop_database('test-db')
        disconnect(alias='test-db-alias')


@pytest.fixture(scope="function")
def game(connection: Generator) -> crud_game_current.CRUDGame:
    """Get crud game object
    """
    return crud_game_current.CRUDGame(connection['CurrentGameData'])


@pytest.fixture(scope="function")
def user(connection: Generator) -> crud_user.CRUDUser:
    """Get crud game object
    """
    return crud_user.CRUDUser(connection['User'])


@pytest.fixture(scope="function")
def static(connection: Generator) -> crud_game_static.CRUDStatic:
    """Get game processor object
    """
    return crud_game_static.CRUDStatic(
        connection['Agent'],
        connection['Group'],
        connection['Objective'],
            )


@pytest.fixture(scope="function")
def game_logic(
    game: crud_game_current.CRUDGame,
    static: crud_game_static.CRUDStatic,
        ) -> GameLogic:
    """Get game processor object
    """
    game = game.get_last_game(settings.user0_login)
    return GameLogic(static, game)


# @pytest.fixture(scope="function")
# def started_game_proc(
#     inited_game_proc: processor_game.GameProcessor,
#         ) -> processor_game.GameProcessor:
#     """Init the game and return processor
#     """
#     return inited_game_proc.deal_and_shuffle_decks()
