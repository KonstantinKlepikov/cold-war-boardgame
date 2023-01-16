from enum import Enum
from typing import List


class BaseEnum(str, Enum):
    """Base class for enumeration
    """
    @classmethod
    def has_value(cls, value: str) -> bool:
        return value in cls._value2member_map_

    @classmethod
    def get_values(cls) -> List[str]:
        return [e.value for e in cls]


class Priority(BaseEnum):
    """Priority enumeration
    """
    TRUE = 'true'
    FALSE = 'false'
    RANDOM = 'random'


class Faction(BaseEnum):
    """Faction enumeration
    """
    CIA = 'cia'
    KGB = 'kgb'


class Phases(BaseEnum):
    """Game phases
    """
    BRIEFING = 'briefing'
    PLANNING = 'planning'
    INFLUENCE = 'influence_struggle'
    CEASEFIRE = 'ceasefire'
    DEBRIFIENG = 'debriefing'
    DETENTE = 'detente'


class Agents(BaseEnum):
    """Agent cards ids
    """
    SPY = 'Master Spy'
    DEPUTY = 'Deputy Director'
    DOUBLE = 'Double Agent'
    ANALYST = 'Analyst'
    ASSASSIN = 'Assassin'
    DIRECTOR = 'Director'


class HiddenAgents(BaseEnum):
    """Agent cards ids
    """
    SPY = 'Master Spy'
    DEPUTY = 'Deputy Director'
    DOUBLE = 'Double Agent'
    ANALYST = 'Analyst'
    ASSASSIN = 'Assassin'
    DIRECTOR = 'Director'
    HIDDEN = '_hidden'


class Groups(BaseEnum):
    """Groups cards ids
    """
    GUERILLA = 'Guerilla'
    MILITIA = 'Militia'
    MERCENARIES = 'Mercenaries'
    POLICE = 'Police'
    INFANTRY = 'Infantry'
    GENERALS = 'Generals'
    WORKERS = 'Workers'
    MAFIA = 'Mafia'
    FOODCOMPANIES = 'Food companies'
    INDUSTRY = 'Industry'
    OILTYCOONS = 'Oil Tycoons'
    BANKERS = 'Bankers'
    STUDENTS = 'Students'
    TRADEUNION = 'Trade Union'
    NATIONALISTS = 'Nationalists'
    FUNDAMENTALISTS = 'Fundamentalists'
    OPPOSITION = 'Opposition'
    GOVERNMENT = 'Government'
    ARTISTS = 'Artists'
    NGOS = 'NGOs'
    PHONECOMPANY = 'Phone company'
    NEWSPAPERS = 'Newspapers'
    RADIO = 'Radio'
    TELEVISION = 'Television'


class Objectives(BaseEnum):
    """Objectives cards ids
    """
    NOBELPEACEPRIZE = 'Nobel Peace Prize'
    LIVEBENEFIT = 'Live Benefit'
    NUCLEARESCALATION = 'Nuclear Escalation'
    SPACERACE = 'Space Race'
    OLYMPICGAMES = 'Olympic Games'
    SUMMITMEETING = 'Summit Meeting'
    EGYPT = 'Egypt'
    VIETNAM = 'Vietnam'
    PANAMA = 'Panama'
    ANGOLA = 'Angola'
    AFGHANISTAN = 'Afghanistan'
    HOUNDARAS = 'Houndaras'
    LIBYA = 'Libya'
    GREECE = 'Greece'
    TURKEY = 'Turkey'
    IRAN = 'Iran'
    CUBA = 'Cuba'
    CONGO = 'Congo'
    CZECHOSLOVAKIA = 'Czechoslovakia'
    CHILE = 'Chile'
    KOREA = 'Korea'


class ObjectiveAbilities(BaseEnum):
    """Objectives with abilities cards ids
    """
    NOBELPEACEPRIZE = 'Nobel Peace Prize'
    LIVEBENEFIT = 'Live Benefit'
    NUCLEARESCALATION = 'Nuclear Escalation'
    SPACERACE = 'Space Race'
    OLYMPICGAMES = 'Olympic Games'
    SUMMITMEETING = 'Summit Meeting'


class Icons(BaseEnum):
    """Bias icons
    """
    ECONOMIC = 'Economic'
    MILITARY = 'Military'
    MEDIA = 'Media'
    POLITICAL = 'Political'


class GroupFactions(BaseEnum):
    """Factions of group
    """
    ECONOMIC = 'Economic'
    MILITARY = 'Military'
    MEDIA = 'Media'
    POLITICAL = 'Political'
    GOVERMENY = 'Government',
