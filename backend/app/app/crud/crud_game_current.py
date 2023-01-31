from typing import Optional
from fastapi.encoders import jsonable_encoder
from app.crud import crud_base, crud_game_static
from app.models.model_game_current import CurrentGameData
from app.schemas.scheme_game_current import CurrentGameDataProcessor


class CRUDGame(
    crud_base.CRUDBase[
        CurrentGameData,
        CurrentGameDataProcessor
            ]
        ):
    """Crud for game current state document
    """

    def get_current_game_data(self, login: str) -> Optional[CurrentGameData]:
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
            ) -> Optional[CurrentGameDataProcessor]:
        """Get game processor

        Args:
            login (str): user login

        Returns:
            CurrentGameDataProcessor, optional: processor
        """
        current = self.get_current_game_data(login)
        if current:
            proc = CurrentGameDataProcessor(**current)
            proc.steps.fill()
            return proc
        else:
            return

    def create_new_game(self, obj_in: CurrentGameDataProcessor) -> None:
        """Create new game processor
        """
        db_data = jsonable_encoder(obj_in)
        current_data = self.model(**db_data)
        current_data.save()


    def get_old_game(
        self,
        login: str,
            ) -> Optional[CurrentGameDataProcessor]:
        """Get game processor with db game data

        Args:
            login (str): user login

        Returns:
            CurrentGameDataProcessor, optional: processor
        """
        static = crud_game_static.static.get_static_game_data()
        current = self.get_current_game_data(login)
        if current:
            proc = CurrentGameDataProcessor(**current)

            # fill steps
            proc.steps.fill()

            # fill players

            # fill decks

            return proc
        else:
            return

game = CRUDGame(CurrentGameData)
