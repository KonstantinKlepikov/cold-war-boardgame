# import random
from typing import Optional
from fastapi.encoders import jsonable_encoder
from fastapi import HTTPException
from app.core import game_logic
from app.crud import crud_base, crud_card, crud_game
from app.models import model_game
from app.schemas import schema_game
# from app.constructs import Priority, Faction
from app.config import settings


class CRUDGame(
    crud_base.CRUDBase[
        model_game.CurrentGameData,
        schema_game.CurrentGameData
            ]
        ):
    """Crud for game current state document
    """

    def get_current_game_data(self, login: str) -> Optional[model_game.CurrentGameData]:
        """Get current game data from db

        Args:
            login (str): player login

        Returns:
            CurrentGameData: bd data object
        """
        return self.model.objects(players__login=login).first()

    def get_game_processor(
        self,
        login: str,
            ) -> game_logic.GameProcessor:
        """Get game processor

        Args:
            current_data (CurrentGameData): bd data object
            login (str): user login

        Returns:
            game_logic.GameProcessor: processor
        """
        game_proc = game_logic.GameProcessor(
            crud_card.cards.get_all_cards(),
            crud_game.game.get_current_game_data(login)
                )
        return game_proc.fill()

    def create_new_game(self, obj_in: schema_game.CurrentGameData) -> None:
        """Create new game
        """
        db_data = jsonable_encoder(obj_in)
        current_data = self.model(**db_data)
        current_data.save()


game = CRUDGame(model_game.CurrentGameData)
