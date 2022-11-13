import datetime
import pytest
from fastapi import HTTPException
from app.core import security, security_user
from app.schemas import schema_user


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


class TestSecurityUser:
    """Test security user functions
    """

    def test_get_current_user(self) -> None:
        """Test get current user
        """
        user = security_user.get_current_user(
            'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJEb25hbGRUcnVtcCJ9.88z5C7fb1gW2jVTs-ut1aRyp--Z3IrGJqIEKu6VVn50'
                )
        assert user.login == 'DonaldTrump', 'wrong login'
        assert user.is_active, 'wrong is_active'
        with pytest.raises(
            HTTPException,
            ):
            security_user.get_current_user('12345')

    def test_get_current_active_user(self) -> None:
        """Test get current active user
        """
        schema = schema_user.User(login='DonaldTrump')
        user = security_user.get_current_active_user(schema)
        assert user.login == 'DonaldTrump', 'wrong login'
        assert user.is_active, 'wrong is_active'
        with pytest.raises(
            HTTPException,
            ):
            schema = schema_user.User(login='DonaldTrump', is_active=None)
            security_user.get_current_active_user(schema)
