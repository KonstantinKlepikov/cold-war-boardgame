import os
import pymongo


class TestDB:
    """Db tests
    """

    def test_external_db_connection(self):
        """Test external db ia available
        """
        MONGODB_URL = os.environ.get('MONGODB_URL')
        client = pymongo.MongoClient(MONGODB_URL)
        db = client.test
        assert isinstance(db, pymongo.database.Database), \
            'External db isnt available'
        assert db.connect != True, 'External db not connected'
