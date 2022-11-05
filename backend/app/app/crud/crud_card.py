import json
from typing import Union
from app.crud.crud_base import CRUDBaseRead
from app.models.model_cards import AgentsCards, GroupCards, ObjectiveCards
from app.schemas import cards


class CRUDCards(CRUDBaseRead[
    Union[AgentsCards, GroupCards, ObjectiveCards],
    cards.GameCards

    ]):
    """_summary_

    Args:
        CRUDBase (_type_): _description_
    """

    def get_all_cards(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        # db_cards = {}
        # db_cards['agent_cards'] = [
        #     self.schemas[0].parse_raw(j.to_json()) for j in self.models[0].objects
        #     ]
        # db_cards['group_cards'] = [
        #     self.schemas[1].parse_raw(j.to_json()) for j in self.models[1].objects
        #     ]
        # db_cards['objective_cards'] = [
        #     self.schemas[2].parse_raw(j.to_json()) for j in self.models[2].objects
        #     ]
        # db_cards = f"'agent_cards':{self.models[0].objects.to_json()}" \
        #            f"'group_cards':{self.models[1].objects.to_json()}" \
        #            f"'objective_cards':{self.models[2].objects.to_json()}"

        db_cards = {
            'agent_cards': json.loads(self.models[0].objects.to_json()),
            'group_cards': json.loads(self.models[1].objects.to_json()),
            'objective_cards': json.loads(self.models[2].objects.to_json()),
        }


        # db_cards['agent_cards'] = self.models[0].objects.to_json()
        # db_cards['group_cards'] = self.models[1].objects.to_json()
        # db_cards['objective_cards'] = self.models[2].objects.to_json()

        # result = self.schema.parse_raw(db_cards)
        result = self.schema.parse_obj(db_cards)

        return result


cards = CRUDCards(
    [AgentsCards, GroupCards, ObjectiveCards],
    cards.GameCards
    )
