import pymongo
from typing import Generator
from mongoengine import get_connection, get_db
from app.db.init_db import check_db_cards_init, check_db_users_init


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
        assert isinstance(connection['connection'], pymongo.mongo_client.MongoClient), \
            'wrong type of connection'

        db = get_db(alias='test-db-alias')
        assert isinstance(db, pymongo.database.Database), \
            'wrong type of db'
        assert db.name == "test-db", 'wrong db name'
        assert connection['User'].objects().count() == 3, 'wrong count of test users'

    def test_db_init_cards(
        self,
        connection: Generator
            ) -> None:
        """Test init_db_cards() cards initialisation
        """
        assert connection['AgentCard'].objects().count() == 6, \
            'wrong count of test agents cards'
        assert connection['GroupCard'].objects().count() == 24, \
            'wrong count of test groups cards'
        assert connection['ObjectiveCard'].objects().count() == 21, \
            'wrong count of test objective cards'

    def test_db_init_users(
        self,
        connection: Generator
            ) -> None:
        """Test init_db_users() users initialisation
        """
        assert connection['AgentCard'].objects().count() == 6, \
            'wrong count of test agents cards'
        assert connection['GroupCard'].objects().count() == 24, \
            'wrong count of test groups cards'
        assert connection['ObjectiveCard'].objects().count() == 21, \
            'wrong count of test objective cards'

    def test_check_db_cards_init(
        self,
        connection: Generator
            ) -> None:
        """Test database init check function
        """
        assert check_db_cards_init('test-db-alias'), 'db not inited'

    def test_check_db_users_init(
        self,
        connection: Generator
            ) -> None:
        """Test database гыукы init check function
        """
        assert check_db_users_init('test-db-alias'), 'db not inited'
