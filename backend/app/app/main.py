from typing import Dict
from fastapi import FastAPI, status, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from mongoengine import connect
from app.schemas import schema_cards, schema_user, schema_game
from app.crud import crud_user, crud_card, crud_game
from app.core import game_data, security, security_user
from app.config import settings
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
    OK. As response you receive access token,
    that must be used for all secure operations.
    """
        )
def login(
    user: OAuth2PasswordRequestForm = Depends(),
        ) -> Dict[str, str]:
    """Send for autorization:

    - **password**
    - **email**
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
            'access_token': security.create_access_token(user.username),
            "token_type": "bearer"
                }


@app.get(
    "/game/data/static",
    response_model=schema_cards.GameCards,
    status_code=status.HTTP_200_OK,
    tags=['game/data', ],
    summary='Static game data',
    response_description="""
    OK. As response you recieve static game data.
    """
        )
def get_static_data() -> schema_cards.GameCards:
    """Get all static game data (cards data).
    """
    db_cards = crud_card.cards.get_all_cards()
    return schema_cards.GameCards(**db_cards)


@app.post(
    "/game/data/current",
    response_model=schema_game.CurrentGameData,
    status_code=status.HTTP_200_OK,
    responses=settings.ACCESS_ERRORS,
    tags=['game/data', ],
    summary='Current game data',
    response_description="""
    OK. As response you recieve current game data.
    """
        )
def get_current_data(
    user: schema_user.User = Depends(security_user.get_current_active_user)
        ) -> schema_game.CurrentGameData:
    """Get all current game data (game statement) for current user.
    """
    data = crud_game.game.get_current_game_data(user.login)
    return data.to_mongo().to_dict()


@app.post(
    "/game/create",
    response_model=schema_game.CurrentGameData,
    status_code=status.HTTP_201_CREATED,
    responses=settings.ACCESS_ERRORS,
    tags=['game', ],
    summary='Create new game',
    response_description="""
    Created. New game object created in db.
    """
        )
def create_new_game(
    user: schema_user.User = Depends(security_user.get_current_active_user)
        ) -> None:
    """Create new game.
    """
    obj_in = game_data.make_game_data(user.login)
    crud_game.game.create_new_game(obj_in)
