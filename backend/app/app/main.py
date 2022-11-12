from typing import Dict, Union, List
from fastapi import FastAPI, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.schemas import schema_cards, schema_user, schema_game
from app.crud import crud_user, crud_card, crud_game
from app.core.security import verify_password, create_access_token
from app.config import settings
from mongoengine import connect
from app.db.init_db import check_db_init, init_db


connect(
    host=settings.mongodb_url,
    name=settings.db_name,
    alias='default',
    )

if not check_db_init('default'):
    init_db('default')


app = FastAPI(
    title=settings.title,
    description=settings.descriprion,
    version=settings.version,
    openapi_tags=settings.openapi_tags
        )


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post(
    "/user/login",
    response_model=schema_user.Token,
    status_code=status.HTTP_200_OK,
    responses=settings.AUTHENTICATE_RESPONSE_ERRORS,
    tags=['user', ],
    summary='Authenticate user',
    response_description="""
    OK. As response you recieve access token,
    that must be used for all secured operations.
    """
        )
def login(
    user: schema_user.UserCreateUpdate,
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


@app.get(
    "/game/data/static",
    response_model=schema_cards.GameCards,
    status_code=status.HTTP_200_OK,
    tags=['game', ],
    summary='Static cards data',
    response_description="""
    OK. As response you recieve static game data.
    """
        )
def get_static_data() -> schema_cards.GameCards:
    """Get all static game data (cards data)
    """
    return crud_card.cards.get_all_cards()


# TODO: token and test me
@app.post(
    "/game/data/current",
    response_model=schema_game.CurrentGameData,
    status_code=status.HTTP_200_OK,
    tags=['game', ],
    summary='Current game data',
    response_description="""
    OK. As response you recieve current game data.
    """
        )
def get_static_data() -> schema_game.CurrentGameData:
    """Get all current game data (game statement)
    """
    return crud_game.game.get_current_game_data()
