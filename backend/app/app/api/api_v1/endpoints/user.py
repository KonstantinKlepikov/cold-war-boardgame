from typing import Dict
from fastapi import HTTPException, Depends, APIRouter, status
from fastapi.security import OAuth2PasswordRequestForm
from app.crud import crud_user
from app.schemas import schema_user
from app.core import security
from app.config import settings


router = APIRouter()


@router.post(
    "/login",
    response_model=schema_user.Token,
    status_code=status.HTTP_200_OK,
    responses=settings.AUTHENTICATE_RESPONSE_ERRORS,
    summary='Authenticate user',
    response_description="OK. As response you receive access token. "
                         "Use it for bearer autentication."
        )
def login(
    user: OAuth2PasswordRequestForm = Depends(),
        ) -> Dict[str, str]:
    """Send for autorization:

    - **password**
    - **login**
    """
    db_user = crud_user.user.get_by_login(user.username)

    if not db_user or not security.verify_password(
        user.password, db_user.hashed_password
            ):
        raise HTTPException(
            status_code=400, detail='Wrong login or password'
                )

    else:
        return {
            'access_token': security.create_access_token(subject=user.username),
            "token_type": "bearer"
                }
