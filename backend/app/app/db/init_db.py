import yaml
from typing import Any
from app.models import model_game_static, model_user
from app.config import settings
from mongoengine.context_managers import switch_db


def get_yaml(source: str) -> dict[str, Any]:
    """Get yaml from source
    """
    with open(source, "r") as stream:
        try:
            y = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    return y


def init_db_cards(alias: str = 'default') -> None:
    """Init database with cards
    """
    cards = get_yaml('app/db/data/converted.yaml')

    with switch_db(model_game_static.Agent, alias) as Agent:
        for card in cards['agent_cards']:
            data = Agent(**card)
            data.save()

    with switch_db(model_game_static.Group, alias) as Group:
        for card in cards['group_cards']:
            data = Group(**card)
            data.save()

    with switch_db(model_game_static.Objective, alias) as Objective:
        for card in cards['objective_cards']:
            data = Objective(**card)
            data.save()


def init_db_users(alias: str = 'default') -> None:
    """Init database with users
    """
    with switch_db(model_user.User, alias) as User:
        if settings.user0_login:
            data = User(
                login=settings.user0_login,
                hashed_password=settings.user0_hashed_password
                    )
            data.save()

        if settings.user1_login:
            data = User(
                login=settings.user1_login,
                hashed_password=settings.user1_hashed_password
                    )
            data.save()

        if settings.user2_login:
            data = User(
                login=settings.user2_login,
                hashed_password=settings.user2_hashed_password
                    )
            data.save()


def check_db_cards_init(alias: str = 'default') -> bool:
    """Check is cards in db initialized
    """
    with switch_db(model_game_static.Agent, alias) as Agent:
        count = Agent.objects().count()
        if count == 6:
            return True
        return False


def check_db_users_init(alias: str = 'default') -> bool:
    """Check is user in db initialized
    """
    with switch_db(model_user.User, alias) as User:
        trump = User.objects(login=settings.user0_login)
        if trump:
            return True
        return False
