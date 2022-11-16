from enum import Enum


class Priority(str, Enum):
    """Priority enumeration
    """
    TRUE = 'true'
    FALSE = 'false'
    RANDOM = 'random'


class Faction(str, Enum):
    """Faction enumeration
    """
    CIA = 'cia'
    KGB = 'kgb'


class Phase(str, Enum):
    """Game phases
    """
    BRIEFING = 'briefing'
    PLANNING = 'planning'
    INFLUENCE = 'influence_struggle'
    CEASEFIRE = 'ceasefire'
    DEBRIFIENG = 'debriefing'
    DETENTE = 'detente'

    @classmethod
    def has_value(cls, value: str) -> bool:
        return value in cls._value2member_map_
