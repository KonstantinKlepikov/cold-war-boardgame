from typing import Dict, List, Union, Optional, Any
from fastapi import HTTPException
from app.schemas import schema_game
from app.models import model_game
from app.config import settings
from app.constructs import Priority, Faction
from bgameb import Game, Player, Deck, Card, Steps, Step, Dice
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json, Undefined
from fastapi.encoders import jsonable_encoder


def make_game_data(login: str) -> schema_game.CurrentGameData:
    """Make game data for start the game

    Returns:
        CurrentGameData: game data schema
    """
    agent_cards = [
            {'name': 'Master Spy'},
            {'name': 'Deputy Director'},
            {'name': 'Double Agent'},
            {'name': 'Analyst'},
            {'name': 'Assassin'},
            {'name': 'Director'},
            ]

    new_game = {
                'players':
                    [
                        {
                            'is_bot': False,
                            'player_cards': {'agent_cards': agent_cards},
                            'login': login,
                        },
                        {
                            'is_bot': True,
                            'player_cards': {'agent_cards': agent_cards},
                            'login': None,
                        }
                    ]
                }

    return schema_game.CurrentGameData(**new_game)


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
# @dataclass_json(undefined=Undefined.INCLUDE)
@dataclass(repr=False)
class CustomPlayer(Player):
    has_priority: Optional[bool] = None
    is_bot: Optional[bool] = None
    score: int = 0
    faction: Optional[str] = None
    player_cards: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)
    login: Optional[str] = None
    # abilities: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        super().__post_init__()


@dataclass_json(undefined=Undefined.EXCLUDE)
# @dataclass_json(undefined=Undefined.INCLUDE)
@dataclass(repr=False)
class CustomDeck(Deck):
    pile: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        super().__post_init__()


@dataclass_json(undefined=Undefined.EXCLUDE)
# @dataclass_json(undefined=Undefined.INCLUDE)
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
# @dataclass_json(undefined=Undefined.INCLUDE)
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
# @dataclass_json(undefined=Undefined.INCLUDE)
@dataclass(repr=False)
class GroupCard(Card):
    name: Optional[str] = None
    faction: Optional[str] = None
    influence: Optional[int] = None
    power: Optional[str] = None

    def __post_init__(self) -> None:
        super().__post_init__()


@dataclass_json(undefined=Undefined.EXCLUDE)
# @dataclass_json(undefined=Undefined.INCLUDE)
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


class GameProcessor:
    """Create the game object to manipulation of game tools

    Args:
        cards (Dict[str, List[Dict[str, Union[str, int]]]])
        current_data (Optional[model_game.CurrentGameData])
    """

    def __init__(
        self,
        cards: Dict[str, List[Dict[str, Union[str, int]]]],
        current_data: Optional[model_game.CurrentGameData]
            ) -> None:
        self.G: CustomGame = CustomGame('Cold War Game')
        self.cards = cards
        self._check_if_current(current_data)

    def _check_if_current(
        self,
        current_data: Optional[model_game.CurrentGameData]
            ) -> None:
        if not current_data:
            raise HTTPException(
                status_code=404,
                detail="Cant find current game data in db. For start "
                    "new game use /game/create endpoint",
                        )
        else:
            self.current_data = current_data

    def fill(self) -> 'GameProcessor':
        """Init new objective deck

        Returns:
            GameProcessor: initet game processor
        """
        # init ptayers
        for p in self.current_data.players:
            data: dict = p.to_mongo().to_dict()
            name = 'player' if data['is_bot'] == False else 'bot'
            player = CustomPlayer(name, **data)
            self.G.add(player)

        # init group deck
        self.G.add(CustomDeck('groups'))
        for c in self.cards['group_cards']:
            card = GroupCard(
                c['name'],
                **c
                )
            self.G.t.groups.add(card)

        # init objective deck
        self.G.add(CustomDeck('objectives'))
        for c in self.cards['objective_cards']:
            card = ObjectiveCard(
                c['name'],
                **c
                )
            self.G.t.objectives.add(card)

        # init game steps
        data: dict = self.current_data.game_steps.to_mongo().to_dict()
        self.G.add(CustomSteps('steps', **data))
        for num, val in enumerate(settings.phases):
            step = Step(val, priority=num)
            self.G.t.steps.add(step)

        # init coin for random choice
        self.G.add(Dice('coin'))

        # merge group current
        if self.current_data.game_decks.group_deck.current:
            self.G.t.groups.deal(
                self.current_data.game_decks.group_deck.current
                    )
        self.G.t.groups.pile = self.current_data.game_decks.group_deck.pile

        # merge objective current
        if self.current_data.game_decks.objective_deck.current:
            self.G.t.objectives.deal(
                self.current_data.game_decks.objective_deck.current
                    )
        self.G.t.objectives.pile = self.current_data.game_decks.objective_deck.pile
        m = self.current_data.game_decks.mission_card

        # merge current mission card
        self.G.mission_card = m if m else None

        # merge steps
        if self.G.t.steps.turn_phases_left:
            self.G.t.steps.deal(
                self.G.t.steps.turn_phases_left
                    )
        else:
            self.G.t.steps.clear()

        if self.G.t.steps.turn_phase:
            self.G.t.steps.last = self.G.t.steps.i.by_id(
                self.G.t.steps.turn_phase
                    )
        else:
            self.G.t.steps.last = None

        return self

    def flush(self) -> model_game.CurrentGameData:
        """Save the game data to db"""

        # flush plauers
        for num, val in enumerate(self.G.p.values()):
            schema = schema_game.Player(**val.to_dict())
            db_data = jsonable_encoder(schema)
            self.current_data.players[num] = model_game.Player(**db_data)

        # flush game steps
        schema = schema_game.CurrentGameSteps(**self.G.t.steps.to_dict())
        db_data = jsonable_encoder(schema)
        self.current_data.game_steps = model_game.GameSteps(**db_data)

        # flush objectives
        self.current_data.game_decks.mission_card = self.G.mission_card
        ids = self.G.t.objectives.current_ids()
        self.current_data.game_decks.objective_deck.current = ids
        self.current_data.game_decks.objective_deck.deck_len = len(ids)
        self.current_data.game_decks.objective_deck.pile = self.G.t.objectives.pile

        # flush groups
        ids = self.G.t.groups.current_ids()
        self.current_data.game_decks.group_deck.current = ids
        self.current_data.game_decks.group_deck.deck_len = len(ids)
        self.current_data.game_decks.group_deck.pile = self.G.t.groups.pile

        return self.current_data

    def deal_and_shuffle_decks(self) -> 'GameProcessor':
        """Shuffle objective and group decks

        Returns:
            GameProcessor
        """
        self.G.t.groups.deal().shuffle()
        self.G.t.objectives.deal().shuffle()

        return self

    def set_faction(self, faction: Faction) -> 'GameProcessor':
        """Set player and opponent faction

        Args:
            faction (Literal['kgb', 'cia']): player faction

        Returns:
            GameProcessor
        """

        if self.G.p.player.faction:
            raise HTTPException(
                status_code=409,
                detail="Factions is setted yet for this game"
                    )

        self.G.p.player.faction = faction.value
        self.G.p.bot.faction = 'kgb' if faction == Faction.CIA else 'cia'

        return self

    def set_priority(self, priority: Priority) -> 'GameProcessor':
        """Set priority for player

        Args:
            priority (Priority): priority.

        Returns:
            game_logic.GameProcessor
        """
        if self.G.p.player.has_priority \
                or self.G.p.bot.has_priority:
            raise HTTPException(
                status_code=409,
                detail="Priority yet setted for this game"
                    )

        if priority == Priority.TRUE:
            val = True
        elif priority == Priority.FALSE:
            val = False
        elif priority == Priority.RANDOM:
            val = True if self.G.i.coin.roll()[0] == 1 else False

        self.G.p.player.has_priority = val
        self.G.p.bot.has_priority = not val

        return self

    def set_next_turn(self) -> 'GameProcessor':
        """Set next turn

        Returns:
            GameProcessor
        """
        if self.G.t.steps.is_game_end:
            raise HTTPException(
                status_code=409,
                detail="Something can't be changed, because game is end"
                    )

        self.G.t.steps.game_turn += 1
        self.G.t.steps.turn_phases_left = self.G.t.steps.deal().current_ids()
        self.G.t.steps.turn_phase = self.G.t.steps.last = None # NOTE: change in bgameb - when deal, last to None

        return self

    def set_next_phase(self) -> 'GameProcessor':
        """Set next phase

        Returns:
            GameProcessor
        """
        if not self.G.t.steps.last or self.G.t.steps.last.id != settings.phases[5]:
            self.G.t.steps.pull()
            self.G.t.steps.turn_phase = self.G.t.steps.last.id

        return self

    def set_mission_card(self) -> 'GameProcessor':
        """Set mission card on a turn

        Returns:
            GameProcessor
        """
        try:
            self.G.mission_card = self.G.t.objectives.pop().id
        except IndexError:
            raise HTTPException(
                status_code=409,
                detail="Objective deck is empty."
                    )

        return self

    def set_turn_priority(self) -> 'GameProcessor':
        """Set priority to the turn. It used in influence struggle.

        Returns:
            GameProcessor
        """
        if self.G.t.steps.game_turn == 0:
            val = True if self.G.i.coin.roll()[0] == 1 else False
        elif self.G.p.player.score < self.G.p.bot.score:
            val = True
        elif self.G.p.player.score > self.G.p.bot.score:
            val = False
        else:
            # TODO: change condition:
            # if loose previous seas fire phase -> True
            # if both loose -> return self
            return self

        self.G.p.player.has_priority = val
        self.G.p.bot.has_priority = not val

        return self

    def play_analyst_for_look_the_top(self) -> 'GameProcessor':
        """Play annalyt abylity

        Returns:
            GameProcessor
        """
        if self.G.t.steps.turn_phase != settings.phases[0]:
            raise HTTPException(
                status_code=409,
                detail="Ability can't be played in any phases except 'briefing'."
                    )

        # if not 'Analyst' in self.G.p.player.abilitie:
        #     raise HTTPException(
        #         status_code=409,
        #         detail="You havent access to olay ability of Analyst agent card."
        #             )

        top = self.G.t.groups.current[0:2]
        check = set()
        for card in top:
            pass


    def chek_phase_conditions_before_next(self) -> 'GameProcessor':
        """Check game conition before push to next phase
        and raise exception if any check fails

        Returns:
            GameProcessor
        """
        if self.G.t.steps.is_game_end:
            raise HTTPException(
                status_code=409,
                detail="Something can't be changed, because game is end"
                    )

        phase = self.G.t.steps.turn_phase

        # briefing
        if phase == settings.phases[0]:

            # players has priority
            if not self.G.p.player.has_priority \
                    and not self.G.p.bot.has_priority:
                raise HTTPException(
                    status_code=409,
                    detail="No one player has priority. Cant push to next phase."
                        )

            # objective card defined
            if not self.G.mission_card:
                raise HTTPException(
                    status_code=409,
                    detail="Mission card undefined. Cant push to next phase."
                        )

        # planning
        elif phase == settings.phases[1]:
            pass

        # influence_struggle
        elif phase == settings.phases[2]:
            pass

        # ceasefire
        elif phase == settings.phases[3]:
            pass

        # debriefing
        elif phase == settings.phases[4]:
            pass

        # detente
        elif phase == settings.phases[5]:
            raise HTTPException(
                status_code=409,
                detail="This phase is last in a turn. Change turn number "
                        "before get next phase"
                    )

        return self

    def set_phase_conditions_after_next(self) -> 'GameProcessor':
        """Set som phase conditions after push phase

        Returns:
            GameProcessor
        """
        phase = self.G.t.steps.turn_phase

        # set briefing states after next
        if phase == settings.phases[0]:

            self.set_mission_card()
            self.set_turn_priority()

        # planning
        elif phase == settings.phases[1]:
            pass

        # influence_struggle
        elif phase == settings.phases[2]:
            pass

        # ceasefire
        elif phase == settings.phases[3]:
            pass

        # debriefing
        elif phase == settings.phases[4]:
            pass

        # detente
        elif phase == settings.phases[5]:
            pass

        return self