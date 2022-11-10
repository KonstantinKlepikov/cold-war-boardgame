from typing import Optional
from app.crud.crud_base import CRUDBase
from app.models import model_game
from app.schemas import schema_game


class CRUDGame(CRUDBase[model_game.CurrentGameData, schema_game.CurrentGameData]):
    """Crud for game current state document
    """

    def get_current_game_data(self) -> Optional[model_game.CurrentGameData]:
        """Get current game data from db

        Returns:
            CurrentGameData: bd data object
        """
        return model_game.CurrentGameData.objects().first()


schema_game = CRUDGame(model_game.CurrentGameData)
