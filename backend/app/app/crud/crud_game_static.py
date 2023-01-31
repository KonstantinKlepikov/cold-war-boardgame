import json
from typing import Union, Type
from functools import lru_cache
from app.crud import crud_base
from app.models.model_game_static import Agent, Group, Objective
from app.schemas.scheme_game_static import StaticGameData


class CRUDStatic(
    crud_base.CRUDBase[
        Union[Agent, Group, Objective],
        StaticGameData,
            ]
        ):

    def __init__(
        self,
        agent: Type[crud_base.ModelType],
        group: Type[crud_base.ModelType],
        objective: Type[crud_base.ModelType],
            ):
        """
        CRUD object for static data operation.

        **Parameters**

        * `agent`: A MongoDB model class of agent card
        * `group`: A MongoDB model class of group card
        * `objective`: A MongoDB model class of objective card
        """
        self.agent = agent
        self.group = group
        self.objective = objective

    @lru_cache
    def get_static_game_data(self) -> StaticGameData:
        """Get current game data from db

        Returns:
            CurrentGameData: bd data object
        """
        db_cards = {
            'agents': {
                card['name']: card for card in json.loads(self.agent.objects.to_json())
                    },
            'groups': {
                card['name']: card for card in json.loads(self.group.objects.to_json())
                    },
            'objectives': {
                card['name']: card for card in json.loads(self.objective.objects.to_json())
                    },
                }
        return StaticGameData(**db_cards)

static = CRUDStatic(Agent, Group, Objective)
