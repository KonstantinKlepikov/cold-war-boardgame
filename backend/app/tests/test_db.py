import pymongo
import mongomock
from mongoengine import get_connection, get_db, disconnect
from app.db.collection import get_collection
from app.models.user import User


class TestDB:
    """Db connections tests
    """

    def test_dev_db_connection(self) -> None:
        """Test dev db is available
        """
        get_collection()

        conn = get_connection()
        assert isinstance(conn, pymongo.mongo_client.MongoClient), \
            'wrong type of connection'

        db = get_db()
        assert isinstance(db, pymongo.database.Database), \
            'wrong type of db'
        assert db.name == "dev-db", 'wrong db name'

        disconnect()


    def test_test_db_connection(self, collection) -> None:
        """Test test db is available
        """
        conn = get_connection()
        assert isinstance(conn, mongomock.mongo_client.MongoClient), \
            'wrong type of connection'

        db = get_db()
        assert isinstance(db, mongomock.database.Database), \
            'wrong type of db'
        assert db.name == "test-db", 'wrong db name'
        assert User.objects().count() == 2, 'wrong count of test users'
