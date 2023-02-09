import datetime
import pytest
from typing import Generator, Callable
from fastapi import HTTPException
from app.core import security, security_user
from app.schemas import scheme_user
from app.crud import crud_user
from app.config import settings


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
        assert security.verify_password(
            settings.user0_password,
            settings.user0_hashed_password
            ), 'wrong hash'

    def test_create_access_token(self) -> None:
        """Test create access token
        """
        data = settings.user0_login
        token = security.create_access_token(data)
        assert len(token) == 109, 'wrong len'
        token = security.create_access_token(
            data, expires_delta=datetime.timedelta(minutes=1)
                )
        assert len(token) == 132, 'wrong len'


class TestSecurityUser:
    """Test security user functions
    """

    def test_get_current_user(
        self,
        monkeypatch,
        connection: Generator
            ) -> None:
        """Test get current user
        """
        def mockreturn(*args, **kwargs) -> Callable:
            user = crud_user.CRUDUser(connection['User'])
            return user.get_by_login(settings.user0_login)

        monkeypatch.setattr(crud_user.user, "get_by_login", mockreturn)

        user = security_user.get_current_user(settings.user0_token)
        assert user.login == settings.user0_login, 'wrong login'
        assert user.is_active, 'wrong is_active'
        with pytest.raises(
            HTTPException,
            ):
            security_user.get_current_user('12345')

    def test_get_current_active_user(self, connection: Generator) -> None:
        """Test get current active user
        """
        schema = scheme_user.User(login=settings.user0_login)
        user = security_user.get_current_active_user(schema)
        assert user.login == settings.user0_login, 'wrong login'
        assert user.is_active, 'wrong is_active'
        with pytest.raises(
            HTTPException,
            ):
            schema = scheme_user.User(login=settings.user0_login, is_active=None)
            security_user.get_current_active_user(schema)
