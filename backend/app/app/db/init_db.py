import yaml
from typing import Dict, Any
from app.models import model_cards
from mongoengine.context_managers import switch_db


def get_yaml(source: str) -> Dict[str, Any]:
    """Get yaml from source
    """
    with open(source, "r") as stream:
        try:
            y = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    return y


def init_db(alias: str = 'default') -> None:
    """Init database with requred static data
    """
    cards = get_yaml('app/db/data/converted.yaml')

    with switch_db(model_cards.AgentCard, alias) as AgentCards:
        for card in cards['agent_cards']:
            data = AgentCards(**card)
            data.save()

    with switch_db(model_cards.GroupCard, alias) as GroupCards:
        for card in cards['group_cards']:
            data = GroupCards(**card)
            data.save()

    with switch_db(model_cards.ObjectiveCard, alias) as ObjectiveCards:
        for card in cards['objective_cards']:
            data = ObjectiveCards(**card)
            data.save()


def check_db_init(alias: str = 'default') -> bool:
    """Check is db initializes
    """
    with switch_db(model_cards.AgentCard, alias) as AgentCards:
        count = AgentCards.objects().count()
        if count == 6:
            return True
        return False
