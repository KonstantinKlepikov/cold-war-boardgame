from typing import Dict
from fastapi import FastAPI, status, HTTPException
from app.schemas.user import Token, UserCreateUpdate
from app.crud import crud_user
from app.core.security import verify_password, create_access_token
from app.config import settings
from mongoengine import connect


connect(
    host=settings.mongodb_url,
    name=settings.db_name,
    alias='default',
    )

app = FastAPI(
    title=settings.title,
    description=settings.descriprion,
    version=settings.version,
    openapi_tags=settings.openapi_tags
        )


@app.post(
    "/user/login",
    response_model=Token,
    status_code=status.HTTP_200_OK,
    responses=settings.AUTHENTICATE_RESPONSE_ERRORS,
    tags=['user', ],
    summary='Authenticate user',
    response_description="""
    Created. As response you recieve access token,
    that must be used for all secured operation
    """
        )
def login(
    user: UserCreateUpdate,
        ) -> Dict[str, str]:
    """Autorizate user. Send for autorization:

    - **password**
    - **email**
    """
    db_user = crud_user.user.get_by_login(user.login)

    if not db_user or not verify_password(
        user.password, db_user.hashed_password
            ):
        raise HTTPException(
            status_code=400, detail='Wrong login or password'
                )

    else:
        return {'access_token': create_access_token(user.login)}
