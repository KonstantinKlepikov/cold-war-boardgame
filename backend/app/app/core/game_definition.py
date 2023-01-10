from typing import Dict, List, Optional, Any
from bgameb import Game, Player, Deck, Card, Steps
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json, Undefined


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class CustomGame(Game):
    game_steps: dict = field(default_factory=dict)
    players: list = field(default_factory=list)
    game_decks: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        super().__post_init__()

        self._to_relocate = {
            "players": "players_field",
            "game_steps": "game_steps_field",
            "game_decks": "game_decks_field",
                }

    def players_field(self):
        return list(self.get_players().values())

    def game_steps_field(self):
        return self.get_tools()['steps']

    def game_decks_field(self):
        f = {}
        tools = self.get_tools()
        if tools['objectives'].last:
            f['mission_card'] = tools['objectives'].last.id
        else:
            f['mission_card'] = None
        f['group_deck'] = tools['groups']
        f['objective_deck'] = tools['objectives']
        return f


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class CustomSteps(Steps):
    game_turn: int = 0
    turn_phase: Optional[str] = None
    turn_phases_left: List[str] = field(default_factory=list)
    is_game_end: bool = False

    def __post_init__(self) -> None:
        super().__post_init__()

        self._to_relocate = {
            "turn_phase": "turn_phase_field",
            "turn_phases_left": "current_ids",
                }

    def turn_phase_field(self):
        if self.last:
            return self.last.id


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
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

        self._to_relocate = {
            "player_cards": "player_cards_field",
                }

    def player_cards_field(self):
        f = {}
        tools = self.get_tools()
        f['agent_cards'] = tools['agents'].current
        f['group_cards'] = tools['groups'].current
        f['objective_cards'] = tools['objectives'].current
        return f



@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class CustomDeck(Deck):
    deck_len: int = 0
    pile: List[str] = field(default_factory=list)
    deck: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        super().__post_init__()

        self._to_relocate = {
            "deck_len": "deck_len_field",
            "deck": "current_ids",
            }

    def deck_len_field(self):
        return len(self.current)


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class PlayerAgentCard(Card):
    name: Optional[str] = None
    is_dead: bool = False
    is_in_play: bool = False
    is_in_vacation: bool = False
    is_revealed: bool = False


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class PlayerGroupObjCard(Card):
    name: Optional[str] = None
    is_in_deck: bool = True
    is_in_play: bool = False
    is_active: Optional[bool] = None
    pos_in_deck: Optional[int] = None


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class GroupCard(Card):
    name: Optional[str] = None
    faction: Optional[str] = None
    influence: Optional[int] = None
    power: Optional[str] = None


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class ObjectiveCard(Card):
    name: Optional[str] = None
    bias_icons: List[str] = field(default_factory=list)
    population: Optional[int] = None
    special_ability: Optional[str] = None
    stability: Optional[int] = None
    victory_points: Optional[int] = None
