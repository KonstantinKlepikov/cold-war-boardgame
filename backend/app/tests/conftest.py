import pytest
from typing import Generator, Dict, Union
from mongoengine import disconnect, connect
from mongoengine.context_managers import switch_db
from app.config import settings
from app.models import model_user, model_game
from app.db.init_db import init_db


@pytest.fixture(scope="session")
def users_data() -> Dict[str, str]:
    """Get user data
    """
    return {
        'login': settings.user0_login,
        'password': settings.user0_password,
        'hashed_password': settings.user0_hashed_password,
            }


@pytest.fixture(scope="session")
def db_user(users_data: Dict[str, str]) -> Dict[str, str]:
    """Get db user data
    """
    return {
        'login': users_data['login'],
        'hashed_password': users_data['hashed_password']
            }


@pytest.fixture(scope="session")
def db_game_data(users_data: Dict[str, str]) -> Dict[str, Union[str, bool]]:
    """Get game data
    """
    agent_cards = [
        {'agent_card': {'name': 'Master Spy'}},
        {'agent_card': {'name': 'Deputy Director'}},
        {'agent_card': {'name': 'Double Agent'}},
        {'agent_card': {'name': 'Analyst'}},
        {'agent_card': {'name': 'Assassin'}},
        {'agent_card': {'name': 'Director'}}
        ]

    return {
        'players':
            [
                {
                    'is_bot': False,
                    'player_cards': {'agent_cards': agent_cards},
                    'user': {'login': users_data['login']}
                },
                {
                    'is_bot': True,
                    'player_cards': {'agent_cards': agent_cards},
                    'user': None
                }
            ]
        }


@pytest.fixture(scope="function")
def connection(
    db_user: Dict[str, str],
    db_game_data: Dict[str, Union[str, bool]],
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

        # init test users
        with switch_db(model_user.User, 'test-db-alias') as User:
            user = User(**db_user)
            user.save()

        # init constant data
        init_db('test-db-alias')

        # init test user current game
        with switch_db(model_game.CurrentGameData, 'test-db-alias') as CurrentGameData:
            game = CurrentGameData(**db_game_data)
            game.save()

        yield conn

    finally:
        conn.drop_database('test-db')
        disconnect(alias='test-db-alias')
