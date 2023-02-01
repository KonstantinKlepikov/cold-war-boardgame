from typing import Optional
from app.crud import crud_base
from app.models.model_game_current import CurrentGameData
from app.schemas.scheme_game_current import (
    CurrentGameDataProcessor, AgentInPlayProcessor, GroupInPlayProcessor,
    ObjectiveInPlayProcessor
         )
from app.schemas.scheme_game_current_api import CurrentGameDataApi
from app.constructs import Phases, Agents, Groups, Objectives
from app.config import settings
from bgameb import Step


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
        current_model = self.model(**data)
        current_model.save()

        return current_model

    def get_game_processor(
        self,
        current_model: CurrentGameData,
            ) -> CurrentGameDataProcessor:
        """Get game processor with db game data

        Args:
            login (str): user login

        Returns:
            CurrentGameDataProcessor, optional: processor
        """
        current = current_model.to_mongo().to_dict()
        current_proc = CurrentGameDataProcessor(**current)

        # fill steps
        for num, step in enumerate(Phases):
            current_proc.steps.add(Step(id=step.value, priority=num))

        # fill players

        for card in Agents:
            current_proc.players.player.agents.add(
                AgentInPlayProcessor(id=card.value)
                    )
            current_proc.players.opponent.agents.add(
                AgentInPlayProcessor(id=card.value)
                    )

        # fill decks
        for card in Groups:
            current_proc.decks.groups.add(
                GroupInPlayProcessor(id=card.value)
                    )
        for card in Objectives:
            current_proc.decks.objectives.add(
                ObjectiveInPlayProcessor(id=card.value)
                    )

        current_proc.fill()

        return current_proc

    def save_game_processor(
        self,
        current_model: CurrentGameData,
        current_proc: CurrentGameDataProcessor
            ) -> CurrentGameDataProcessor:
        """Flusch and save to db current data processor

        Args:
            proc (CurrentGameDataProcessor): game scheme processor

        Returns:
            CurrentGameDataProcessor: game scheme processor
        """
        current_proc.flusch()
        data = current_proc.dict(
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
        from pprint import pprint
        pprint(data)
        current_model.modify(**data)
        return current_proc

    def get_api_scheme(
        self,
        current_proc: CurrentGameDataProcessor
            ) -> CurrentGameDataApi:
        data = current_proc.dict(by_alias=True)
        return CurrentGameDataApi(**data)


game = CRUDGame(CurrentGameData)
