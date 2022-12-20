from typing import Dict, List, Union, Optional, Any
from fastapi import HTTPException
from app.schemas import schema_game
from app.models import model_game
from app.config import settings
from app.constructs import Priority, Faction
from bgameb import Game, Player, Deck, Card, Steps, Step, Dice, Bag
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
        # init game steps
        data: dict = self.current_data.game_steps.to_mongo().to_dict()
        self.G.add(CustomSteps('steps', **data))
        for num, val in enumerate(settings.phases):
            step = Step(val, priority=num)
            self.G.c.steps.add(step)

        if self.G.c.steps.turn_phases_left:
            self.G.c.steps.deal(
                self.G.c.steps.turn_phases_left
                    )
        else:
            self.G.c.steps.clear()

        if self.G.c.steps.turn_phase:
            self.G.c.steps.last = self.G.c.steps.c.by_id(
                self.G.c.steps.turn_phase
                    )
        else:
            self.G.c.steps.last = None

        # init ptayers
        for p in self.current_data.players:
            data: dict = p.to_mongo().to_dict()
            name = 'player' if data['is_bot'] == False else 'bot'
            player = CustomPlayer(name, **data)
            self.G.add(player)

            # player agents
            self.G.c[name].add(Bag('agents'))
            for c in p.player_cards.agent_cards:
                data: dict = c.to_mongo().to_dict()
                card = PlayerAgentCard(data['name'], **data)
                self.G.c[name].c.agents.add(card)
                self.G.c[name].c.agents.deal()

            # player groups
            self.G.c[name].add(Bag('groups'))
            for c in p.player_cards.group_cards:
                data: dict = c.to_mongo().to_dict()
                card = PlayerGroupObjCard(data['name'], **data)
                self.G.c[name].c.groups.add(card)
                self.G.c[name].c.groups.deal()

            # player groups
            self.G.c[name].add(Bag('objectives'))
            for c in p.player_cards.objective_cards:
                data: dict = c.to_mongo().to_dict()
                card = PlayerGroupObjCard(data['name'], **data)
                self.G.c[name].c.objectives.add(card)
                self.G.c[name].c.objectives.deal()

        # init game decks
        # group deck
        data: dict = self.current_data.game_decks.group_deck.to_mongo().to_dict()
        self.G.add(CustomDeck('groups', **data))
        for c in self.cards['group_cards']:
            card = GroupCard(c['name'], **c)
            self.G.c.groups.add(card)

        if self.G.c.groups.deck:
            self.G.c.groups.deal(self.G.c.groups.deck)
        else:
            self.G.c.groups.clear()

        # objective deck
        data: dict = self.current_data.game_decks.objective_deck.to_mongo().to_dict()
        self.G.add(CustomDeck('objectives', **data))
        for c in self.cards['objective_cards']:
            card = ObjectiveCard(c['name'], **c)
            self.G.c.objectives.add(card)

        if self.G.c.objectives.deck:
            self.G.c.objectives.deal(self.G.c.objectives.deck)
        else:
            self.G.c.objectives.clear()

        # mission card
        m = self.current_data.game_decks.mission_card
        self.G.mission_card = m if m else None

        # init engines
        self.G.add(Dice('coin'))

        return self

    def flusсh(self) -> model_game.CurrentGameData:
        """Save the game data to db"""

        # flusсh game steps
        schema = schema_game.GameStepsDb(**self.G.c.steps.to_dict())
        db_data = jsonable_encoder(schema)
        self.current_data.game_steps = model_game.GameSteps(**db_data)

        # flusсh players
        for num, val in enumerate(self.G.get_players().values()):
            schema = schema_game.Player(**val.to_dict())
            db_data = jsonable_encoder(schema)
            # cards
            cards = {
                'agent_cards': [c.to_dict() for c in val.c.agents.current],
                'group_cards': [c.to_dict() for c in val.c.groups.current],
                'objective_cards': [c.to_dict() for c in val.c.objectives.current],
                }
            schema = schema_game.PlayerCards(**cards)
            db_data['player_cards'] = jsonable_encoder(schema)
            self.current_data.players[num] = model_game.Player(**db_data)

        # flusсh game decks
        # objectives
        ids = self.G.c.objectives.current_ids()
        self.G.c.objectives.deck = ids
        self.G.c.objectives.deck_len = len(ids)
        schema = schema_game.GameDeckDb(**self.G.c.objectives.to_dict())
        db_data = jsonable_encoder(schema)
        self.current_data.game_decks.objective_deck = model_game.GameDeck(**db_data)

        # groups
        ids = self.G.c.groups.current_ids()
        self.G.c.groups.deck = ids
        self.G.c.groups.deck_len = len(ids)
        schema = schema_game.GameDeckDb(**self.G.c.groups.to_dict())
        db_data = jsonable_encoder(schema)
        self.current_data.game_decks.group_deck = model_game.GameDeck(**db_data)

        # mission card
        self.current_data.game_decks.mission_card = self.G.mission_card

        return self.current_data

    def deal_and_shuffle_decks(self) -> 'GameProcessor':
        """Shuffle objective and group decks

        Returns:
            GameProcessor
        """
        self.G.c.groups.deal().shuffle()
        self.G.c.objectives.deal().shuffle()

        return self

    def set_faction(self, faction: Faction) -> 'GameProcessor':
        """Set player and opponent faction

        Args:
            faction (Literal['kgb', 'cia']): player faction

        Returns:
            GameProcessor
        """

        if self.G.c.player.faction:
            raise HTTPException(
                status_code=409,
                detail="Factions is setted yet for this game"
                    )

        self.G.c.player.faction = faction.value
        self.G.c.bot.faction = 'kgb' if faction == Faction.CIA else 'cia'

        return self

    def set_priority(self, priority: Priority) -> 'GameProcessor':
        """Set priority for player

        Args:
            priority (Priority): priority.

        Returns:
            game_logic.GameProcessor
        """
        if self.G.c.player.has_priority \
                or self.G.c.bot.has_priority:
            raise HTTPException(
                status_code=409,
                detail="Priority yet setted for this game"
                    )

        if priority == Priority.TRUE:
            val = True
        elif priority == Priority.FALSE:
            val = False
        elif priority == Priority.RANDOM:
            val = True if self.G.c.coin.roll()[0] == 1 else False

        self.G.c.player.has_priority = val
        self.G.c.bot.has_priority = not val

        return self

    def set_next_turn(self) -> 'GameProcessor':
        """Set next turn

        Returns:
            GameProcessor
        """
        if self.G.c.steps.is_game_end:
            raise HTTPException(
                status_code=409,
                detail="Something can't be changed, because game is end"
                    )

        self.G.c.steps.game_turn += 1
        self.G.c.steps.turn_phases_left = self.G.c.steps.deal().current_ids()
        self.G.c.steps.turn_phase = None

        return self

    def set_next_phase(self) -> 'GameProcessor':
        """Set next phase

        Returns:
            GameProcessor
        """
        if not self.G.c.steps.last or self.G.c.steps.last.id != settings.phases[5]:
            self.G.c.steps.pull()
            self.G.c.steps.turn_phase = self.G.c.steps.last.id

        return self

    def set_mission_card(self) -> 'GameProcessor':
        """Set mission card on a turn

        Returns:
            GameProcessor
        """
        try:
            self.G.mission_card = self.G.c.objectives.pop().id
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
        if self.G.c.steps.game_turn == 0:
            val = True if self.G.c.coin.roll()[0] == 1 else False
        elif self.G.c.player.score < self.G.c.bot.score:
            val = True
        elif self.G.c.player.score > self.G.c.bot.score:
            val = False
        else:
            # TODO: change condition:
            # if loose previous seas fire phase -> True
            # if both loose -> return self
            return self

        self.G.c.player.has_priority = val
        self.G.c.bot.has_priority = not val

        return self

    def play_analyst_for_look_the_top(self) -> 'GameProcessor':
        """Play analyst abylity for look the top cards

        Returns:
            GameProcessor
        """
        if self.G.c.steps.turn_phase != settings.phases[0]:
            raise HTTPException(
                status_code=409,
                detail="Ability can't be played in any phases except 'briefing'."
                    )

        if not 'Analyst' in self.G.c.player.abilities:
            raise HTTPException(
                status_code=409,
                detail="No access to play ability of Analyst agent card."
                    )

        if len([
            card.id for card
            in self.G.c.player.c.groups.current
            if card.pos_in_deck in [-1, -2, -3]
                ]) == 3:
            raise HTTPException(
                status_code=409,
                detail="Top 3 group cards is yet revealed for player."
                    )

        for pos in range(-3, 0):
            card = self.G.c.groups.current[pos]
            try:
                self.G.c.player.c.groups.remove(card.id)
            except ValueError:
                pass
            self.G.c.player.c.groups.append(card)
            self.G.c.player.c.groups.current[-1].pos_in_deck = pos

        return self


    def chek_phase_conditions_before_next(self) -> 'GameProcessor':
        """Check game conition before push to next phase
        and raise exception if any check fails

        Returns:
            GameProcessor
        """
        if self.G.c.steps.is_game_end:
            raise HTTPException(
                status_code=409,
                detail="Something can't be changed, because game is end"
                    )

        phase = self.G.c.steps.turn_phase

        # briefing
        if phase == settings.phases[0]:

            # players has priority
            if not self.G.c.player.has_priority \
                    and not self.G.c.bot.has_priority:
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
        phase = self.G.c.steps.turn_phase

        # set briefing states after next
        if phase == settings.phases[0]:

            self.set_mission_card()
            self.set_turn_priority()
            self.G.c.groups.deal()
            self.G.c.groups.pile.clear()
            self.G.c.player.c.groups.clear()
            self.G.c.bot.c.groups.clear()

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
