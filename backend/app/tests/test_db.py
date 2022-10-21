from typing import Generator
import pymongo
from mongoengine import get_connection, get_db
from mongoengine.context_managers import switch_db
from app.models import model_user


class TestDB:
    """Db connections tests
    """

    def test_dev_db_connection(self) -> None:
        """Test dev db is available
        """
        conn = get_connection()
        assert isinstance(conn, pymongo.mongo_client.MongoClient), \
            'wrong type of connection'

        db = get_db()
        assert isinstance(db, pymongo.database.Database), \
            'wrong type of db'
        assert db.name == "dev-db", 'wrong db name'

    def test_test_db_connection(
        self,
        connection: Generator
            ) -> None:
        """Test test db is available
        """
        assert isinstance(connection, pymongo.mongo_client.MongoClient), \
            'wrong type of connection'

        db = get_db(alias='test-db-alias')
        assert isinstance(db, pymongo.database.Database), \
            'wrong type of db'
        assert db.name == "test-db", 'wrong db name'
        with switch_db(model_user.User, 'test-db-alias') as User:
            assert User.objects().count() == 1, 'wrong count of test users'
