import pytest
from typing import Generator, Dict, List
from mongoengine import disconnect, connect
from app.config import settings
from app.models.user import User


@pytest.fixture(scope="session")
def users_data() -> List[Dict[str, str]]:
    """Get user data
    """
    return [
        {'login': 'user1', 'password': '12345678'},
        {'login': 'user2', 'password': '87654321'},
        ]

@pytest.fixture(scope="function")
def collection(users_data: List[Dict[str, str]]) -> Generator:
    """Get mock mongodb
    """
    collection = connect(
        host=settings.test_mongodb_url,
        name='test-db',
        )
    collection.drop_database('test-db')
    for data in users_data:
        user = User(**data)
        user.save()
    yield collection
    disconnect()
