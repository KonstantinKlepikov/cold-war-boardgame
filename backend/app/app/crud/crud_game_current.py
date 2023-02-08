from typing import Optional
from app.crud import crud_base
from app.models.model_game_current import CurrentGameData
from app.schemas.scheme_game_current import CurrentGameDataProcessor
from app.core.logic import GameLogic
from app.config import settings


class CRUDGame(
    crud_base.CRUDBase[
        CurrentGameData,
        CurrentGameDataProcessor
            ]
        ):
    """Crud for game current state document
    """

    def get_last_game(self, login: str) -> Optional[CurrentGameData]:
        """Get current game data from db

        Args:
            login (str): player login

        Returns:
            CurrentGameData, optional: bd data object
        """
        return self.model.objects(players__player__login=login).first()

    def create_new_game(
        self,
        login: str,
            ) -> CurrentGameData:
        """Create new game processor

        Args:
            login (str): player login

        Returns:
            CurrentGameData, optional: bd data object
        """
        data = {
            'players': {
                'player': {'login': login},
                'opponent': {'login': settings.user2_login},
                    }
                }
        game = self.model(**data)
        game.save()

        return game

    def save_game_processor(
        self,
        game_logic: GameLogic,
            ) -> GameLogic:
        """Flusch and save to db current data processor

        Args:
            proc (CurrentGameDataProcessor): game scheme processor

        Returns:
            CurrentGameDataProcessor: game scheme processor
        """
        game_logic.proc.flusch()
        data = game_logic.proc.dict(
            by_alias=True,
            exclude={
                'steps': {
                    'last_id', 'current_ids', 'current', 'last'
                    },
                'players': {
                    'player': {
                        'agents': {
                            'in_headquarter', 'terminated', 'agent_x',
                            'on_leave', 'last', 'last_id', 'current_ids',
                            },
                        },
                    'opponent': {
                        'agents': {
                            'in_headquarter', 'terminated', 'agent_x',
                            'on_leave', 'last', 'last_id', 'current_ids',
                            },
                        },

                    },
                'decks': {
                    'groups': {
                        'deck', 'current_ids', 'last', 'last_id',
                        },
                    'objectives': {
                        'deck', 'current_ids', 'last', 'last_id',
                        },
                    }
                },
            )
        # from pprint import pprintx
        # pprint(data)
        game_logic.game.modify(**data)
        return game_logic


game = CRUDGame(CurrentGameData)
