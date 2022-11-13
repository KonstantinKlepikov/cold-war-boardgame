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
        'login': 'DonaldTrump',
        'password': '12345678',
        'hashed_password':
            '$2b$12$Xy29A6zl6XdtEJICAzrt3eEzMlVQf6NJgG4nM2Ak4UFk8/AwpZU4q' # TODO: remove
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
def db_game(users_data: Dict[str, str]) -> Dict[str, Union[str, bool]]:
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
                    'user': {'login': None }
                }
            ]
        }


@pytest.fixture(scope="function")
def connection(
    db_user: Dict[str, str],
    db_game: Dict[str, Union[str, bool]],
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
            game = CurrentGameData(**db_game)
            game.save()

        yield conn

    finally:
        conn.drop_database('test-db')
        disconnect(alias='test-db-alias')
