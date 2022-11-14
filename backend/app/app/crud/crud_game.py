from typing import Optional
from fastapi.encoders import jsonable_encoder
from app.crud import crud_base
from app.models import model_game
from app.schemas import schema_game


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

        Returns:
            CurrentGameData: bd data object
        """
        return self.model.objects(players__user__login=login).first()

    def create_new_game(self, obj_in: schema_game.CurrentGameData) -> None:
        """Create new game
        """
        db_data = jsonable_encoder(obj_in)
        game = self.model(**db_data)
        game.save(cascade=True)


game = CRUDGame(model_game.CurrentGameData)
