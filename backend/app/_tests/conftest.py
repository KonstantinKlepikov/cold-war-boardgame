import pytest
from typing import Generator, Union
from mongoengine import disconnect, connect
from mongoengine.context_managers import switch_db
# from fastapi.testclient import TestClient
# from app.main import app
from app.config import settings
from app.models import model_user, model_game_current, model_game_static
# from app.crud import crud_game, crud_card, crud_user
from app.constructs import Agents, Groups, Objectives
from app.db.init_db import init_db_cards, init_db_users


agent_cards = [{'name': agent} for agent in Agents.get_values()]


@pytest.fixture(scope="session")
def users_data() -> dict[str, str]:
    """Get user data
    """
    return {
        'login': settings.user0_login,
        'password': settings.user0_password,
        'hashed_password': settings.user0_hashed_password,
            }


@pytest.fixture(scope="session")
def db_user(users_data: dict[str, str]) -> dict[str, str]:
    """Get db user data
    """
    return {
        'login': users_data['login'],
        'hashed_password': users_data['hashed_password']
            }


@pytest.fixture(scope="session")
def db_game_data() -> dict[str, Union[str, bool]]:
    """Get game data
    """
    return {
        'game_decks':
            {
                'group_deck': {
                    'deck': Groups.get_values(),
                    'deck_len': 24,
                        },
                'objective_deck': {
                    'deck': Objectives.get_values(),
                    'deck_len': 21,
                        }
            },
        'players':
            [
                {
                    'is_bot': False,
                    'player_cards': {'agent_cards':
                        {'db_cards': agent_cards},
                            },
                    'login': settings.user0_login,
                },
                {
                    'is_bot': True,
                    'player_cards': {'agent_cards':
                        {'db_cards': agent_cards},
                            },
                    'login': None,
                }
            ]
        }


# @pytest.fixture(scope="function")
# def client() -> Generator:
#     with TestClient(app) as c:
#         yield c


@pytest.fixture(scope="function")
def connection(
    db_game_data: dict[str, Union[str, bool]],
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
            # game = CurrentGameData(**db_game_data)
            # game.save()


            yield {
                'connection': conn,
                'User': User,
                # 'CurrentGameData': CurrentGameData,
                'Agent': Agent,
                'Group': Group,
                'Objective': Objective,
                }

    finally:
        conn.drop_database('test-db')
        disconnect(alias='test-db-alias')


# @pytest.fixture(scope="function")
# def game(connection: Generator) -> crud_game.CRUDGame:
#     """Get crud game object
#     """
#     return crud_game.CRUDGame(connection['CurrentGameData'])


# @pytest.fixture(scope="function")
# def user(connection: Generator) -> crud_user.CRUDUser:
#     """Get crud game object
#     """
#     return crud_user.CRUDUser(connection['User'])


# @pytest.fixture(scope="function")
# def cards(connection: Generator) -> crud_card.CRUDCards:
#     """Get game processor object
#     """
#     return crud_card.CRUDCards(
#         connection['Agent'],
#         connection['Group'],
#         connection['Objective'],
#             )


# @pytest.fixture(scope="function")
# def game_proc(
#     game: crud_game.CRUDGame,
#     cards: crud_card.CRUDCards,
#         ) -> processor_game.GameProcessor:
#     """Get game processor object
#     """
#     current_data = game.get_current_game_data(settings.user0_login)
#     return processor_game.GameProcessor(cards.get_all_cards(), current_data)


# @pytest.fixture(scope="function")
# def inited_game_proc(
#     game_proc: processor_game.GameProcessor,
#         ) -> processor_game.GameProcessor:
#     """Fill game processor object
#     """
#     return game_proc.fill()


# @pytest.fixture(scope="function")
# def started_game_proc(
#     inited_game_proc: processor_game.GameProcessor,
#         ) -> processor_game.GameProcessor:
#     """Init the game and return processor
#     """
#     return inited_game_proc.deal_and_shuffle_decks()