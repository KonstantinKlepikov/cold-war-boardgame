import json
from typing import Union, List, Dict, Type
from functools import lru_cache
from app.crud import crud_base
from app.models import model_cards
from app.schemas import schema_cards


class CRUDCards(crud_base.CRUDBase[Union[
    model_cards.AgentCard,
    model_cards.GroupCard,
    model_cards.ObjectiveCard
        ], schema_cards.GameCards]):

    def __init__(
        self,
        agent_card: Type[crud_base.ModelType],
        group_card: Type[crud_base.ModelType],
        objective_card: Type[crud_base.ModelType],
            ):
        """
        CRUD object for cards operation.

        **Parameters**

        * `agent_card`: A MongoDB model class of agent card
        * `group_card`: A MongoDB model class of group card
        * `objective_card`: A MongoDB model class of objective card
        """
        self.agent_card = agent_card
        self.group_card = group_card
        self.objective_card = objective_card

    @lru_cache
    def get_all_cards(self) -> Dict[str, List[Dict[str, Union[str, int]]]]:
        """Get all cards data from db

        Returns:
            Dict[str, List[Dict[str, Union[str, int]]]]: game cards data
        """
        db_cards = {
            'agent_cards': json.loads(self.agent_card.objects.to_json()),
            'group_cards': json.loads(self.group_card.objects.to_json()),
            'objective_cards': json.loads(self.objective_card.objects.to_json()),
        }

        return db_cards

    @lru_cache
    def get_cards_names(self) -> Dict[str, List[str]]:
        """Get cards names from db

        Returns:
            Dict[str, List[str]]: names of cards
        """
        db_cards = self.get_all_cards()
        return {
            key: [card['name'] for card in val]
            for key, val in db_cards.items()
                }

    @lru_cache
    def get_cards_dict(self) -> Dict[str, Dict[str, Union[str, int]]]:
        """Get cards data as dict by his names

        Returns:
            Dict[str, Dict[str, Union[str, int]]]: cards dict
        """
        db_cards = self.get_all_cards()
        return {
            key: {card['name']: card for card in val}
            for key, val in db_cards.items()
                }


cards = CRUDCards(
    agent_card=model_cards.AgentCard,
    group_card=model_cards.GroupCard,
    objective_card=model_cards.ObjectiveCard,
        )
