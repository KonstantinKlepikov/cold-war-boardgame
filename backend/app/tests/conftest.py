import pytest
from typing import Generator, Dict, List
from mongoengine import disconnect, connect
from mongoengine.context_managers import switch_db
from app.config import settings
from app.models import model_user


@pytest.fixture(scope="session")
def users_data() -> Dict[str, str]:
    """Get user data
    """
    return {
        'login': 'DonaldTrump',
        'password': '12345678',
        'hashed_password': '$2b$12$Xy29A6zl6XdtEJICAzrt3eEzMlVQf6NJgG4nM2Ak4UFk8/AwpZU4q'
            }

@pytest.fixture(scope="session")
def db_user(users_data: Dict[str, str]) -> Dict[str, str]:
    """Get db user data
    """
    return {
        'login': users_data['login'],
        'hashed_password': users_data['hashed_password']
            }

@pytest.fixture(scope="function")
def connection(db_user: Dict[str, str]) -> Generator:
    """Get mock mongodb
    """
    try:
        conn = connect(
            host=settings.test_mongodb_url,
            name='test-db',
            alias='test-db-alias'
            )
        with switch_db(model_user.User, 'test-db-alias') as User:
            User.drop_collection()
            user = User(**db_user)
            user.save()
        yield conn
    finally:
        disconnect(alias='test-db-alias')
