from typing import Dict, List, Optional, Any
from bgameb import Game, Player, Deck, Card, Steps
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json, Undefined


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass(repr=False)
class CustomGame(Game):
    mission_card: Optional[str] = None

    def __post_init__(self) -> None:
        super().__post_init__()


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass(repr=False)
class CustomSteps(Steps):
    game_turn: int = 0
    turn_phase: Optional[str] = None
    turn_phases_left: List[str] = field(default_factory=list)
    is_game_end: bool = False


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass(repr=False)
class CustomPlayer(Player):
    has_priority: Optional[bool] = None
    is_bot: Optional[bool] = None
    score: int = 0
    faction: Optional[str] = None
    player_cards: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)
    login: Optional[str] = None
    abilities: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        super().__post_init__()


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass(repr=False)
class CustomDeck(Deck):
    deck_len: int = 0
    pile: List[str] = field(default_factory=list)
    deck: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        super().__post_init__()


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass(repr=False)
class PlayerAgentCard(Card):
    name: Optional[str] = None
    is_dead: bool = False
    is_in_play: bool = False
    is_in_vacation: bool = False
    is_revealed: bool = False

    def __post_init__(self) -> None:
        super().__post_init__()


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass(repr=False)
class PlayerGroupObjCard(Card):
    name: Optional[str] = None
    is_in_deck: bool = True
    is_in_play: bool = False
    is_active: Optional[bool] = None
    pos_in_deck: Optional[int] = None

    def __post_init__(self) -> None:
        super().__post_init__()


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass(repr=False)
class GroupCard(Card):
    name: Optional[str] = None
    faction: Optional[str] = None
    influence: Optional[int] = None
    power: Optional[str] = None

    def __post_init__(self) -> None:
        super().__post_init__()


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass(repr=False)
class ObjectiveCard(Card):
    name: Optional[str] = None
    bias_icons: List[str] = field(default_factory=list)
    population: Optional[int] = None
    special_ability: Optional[str] = None
    stability: Optional[int] = None
    victory_points: Optional[int] = None

    def __post_init__(self) -> None:
        super().__post_init__()
