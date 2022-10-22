import datetime
from app.core import security


class TestSecurity:
    """Test security functions
    """

    def test_password_is_hashed(self) -> None:
        """Test password is hashed
        """
        plain_password = '123456789'
        hashed_password = security.get_password_hash(plain_password)
        assert len(hashed_password) == 60, 'wrong hashed password len'

    def test_verify_hashed_password(self) -> None:
        """Test verify hashed password
        """
        plain_password = '123456789'
        hashed_password = security.get_password_hash(plain_password)
        assert security.verify_password(plain_password, hashed_password), \
            'wrong hash'

    def test_create_access_token(self) -> None:
        """Test create access token
        """
        data = 'DonaldTrump'
        token = security.create_access_token(data)
        assert len(token) == 109, 'wrong len'
        token = security.create_access_token(
            data, expires_delta=datetime.timedelta(minutes=1)
                )
        assert len(token) == 132, 'wrong len'
