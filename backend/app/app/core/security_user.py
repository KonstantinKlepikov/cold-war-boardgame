from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from app.schemas import schema_user
from app.crud import crud_user
from app.config import settings


oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.api_v1_str}/user/login")


def get_current_user(token: str = Depends(oauth2_scheme)) -> schema_user.User:
    """Get current verified user
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
            )
        login: str = payload.get("sub")
        if login is None:
            raise credentials_exception
        token_data = schema_user.TokenData(login=login)
    except JWTError:
        raise credentials_exception

    user = crud_user.user.get_by_login(token_data.login)

    if user is None:
        raise credentials_exception

    return schema_user.User.parse_obj(user.to_mongo().to_dict())


def get_current_active_user(
    user: schema_user.User = Depends(get_current_user)
        ) -> schema_user.User:
    """Get current verified active user
    """
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    return user
