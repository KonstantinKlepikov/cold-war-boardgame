import json
from typing import Union, Dict, List
from app.crud.crud_base import CRUDBaseRead
from app.models import model_cards
from app.schemas import schema_cards


class CRUDCards(CRUDBaseRead[Union[
    model_cards.AgentCard,
    model_cards.GroupCard,
    model_cards.ObjectiveCard
        ], schema_cards.GameCards]):
    """Crud for game cards document
    """

    def get_all_cards(self) -> Dict[str, List[Dict[str, Union[str, int]]]]:
        """Get all cards data

        Returns:
            Dict[str, List[Dict[str, Union[str, int]]]]: game cards data
        """

        db_cards = {
            'agent_cards': json.loads(self.models[0].objects.to_json()),
            'group_cards': json.loads(self.models[1].objects.to_json()),
            'objective_cards': json.loads(self.models[2].objects.to_json()),
        }

        result = self.schema.parse_obj(db_cards)

        return result


cards = CRUDCards(
    [model_cards.AgentCard, model_cards.GroupCard, model_cards.ObjectiveCard],
    schema_cards.GameCards
    )
