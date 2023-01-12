from typing import Dict, List, Union, Optional
from fastapi import HTTPException
from app.schemas import schema_game
from app.models import model_game
from app.config import settings
from app.constructs import Priority, Faction
from app.core.engine_game import (
    CustomGame, CustomDeck, CustomPlayer, CustomSteps, PlayerAgentCard,
    PlayerGroupObjCard, GroupCard, ObjectiveCard, CustomAgentBag
        )
from bgameb import Step, Dice, Bag
from fastapi.encoders import jsonable_encoder


def make_game_data(login: str) -> schema_game.CurrentGameDataDb:
    """Make game data for start the game

    Returns:
        CurrentGameDataDb: game data schema
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
                            'player_cards': {'agent_cards':
                                {'db_cards': agent_cards},
                                    },
                            'login': login,
                        },
                        {
                            'is_bot': True,
                            'player_cards': {'agent_cards':
                                {'db_cards': agent_cards},
                                    },
                            'login': None,
                        }
                    ]
                }

    return schema_game.CurrentGameDataDb(**new_game)


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

        if self.G.c.steps.turn_phase:
            self.G.c.steps.last = self.G.c.steps.c.by_id(
                self.G.c.steps.turn_phase
                    )
        # print(self.G.c.steps.current_ids())

        # init ptayers
        for p in self.current_data.players:
            data: dict = p.to_mongo().to_dict()
            name = 'player' if data['is_bot'] == False else 'bot'
            player = CustomPlayer(name, **data)
            self.G.add(player)

            # player agent_cards
            self.G.c[name].add(CustomAgentBag('agent_cards'))
            for c in p.player_cards.agent_cards.db_cards:
                data: dict = c.to_mongo().to_dict()
                card = PlayerAgentCard(data['name'], **data)
                self.G.c[name].c.agent_cards.add(card)
                self.G.c[name].c.agent_cards.deal()

            # player group_cards
            self.G.c[name].add(Bag('group_cards'))
            for c in p.player_cards.group_cards:
                data: dict = c.to_mongo().to_dict()
                card = PlayerGroupObjCard(data['name'], **data)
                self.G.c[name].c.group_cards.add(card)
                self.G.c[name].c.group_cards.deal()

            # player objective_cards
            self.G.c[name].add(Bag('objective_cards'))
            for c in p.player_cards.objective_cards:
                data: dict = c.to_mongo().to_dict()
                card = PlayerGroupObjCard(data['name'], **data)
                self.G.c[name].c.objective_cards.add(card)
                self.G.c[name].c.objective_cards.deal()

        # init game decks
        # group deck
        data: dict = self.current_data.game_decks.group_deck.to_mongo().to_dict()
        self.G.add(CustomDeck('group_deck', **data))
        for c in self.cards['group_cards']:
            card = GroupCard(c['name'], **c)
            self.G.c.group_deck.add(card)

        if self.G.c.group_deck.deck:
            self.G.c.group_deck.deal(self.G.c.group_deck.deck)

        # objective deck
        data: dict = self.current_data.game_decks.objective_deck.to_mongo().to_dict()
        self.G.add(CustomDeck('objective_deck', **data))
        for c in self.cards['objective_cards']:
            card = ObjectiveCard(c['name'], **c)
            self.G.c.objective_deck.add(card)

        if self.G.c.objective_deck.deck:
            self.G.c.objective_deck.deal(self.G.c.objective_deck.deck)

        # mission_card
        if self.current_data.game_decks.mission_card:
            self.G.c.objective_deck.last = self.G.c.objective_deck.c.by_id(
                self.current_data.game_decks.mission_card
                    )

        # init engines
        self.G.add(Dice('coin'))

        return self

    def flush(self) -> model_game.CurrentGameData:
        """Make ready to save game data object"""
        data = self.G.relocate_all().to_dict()
        schema = schema_game.CurrentGameDataDb(**data)
        db_data = jsonable_encoder(schema)
        self.current_data.modify(**db_data)

        return self.current_data

    def deal_and_shuffle_decks(self) -> 'GameProcessor':
        """Shuffle objective and group decks

        Returns:
            GameProcessor
        """
        self.G.c.group_deck.deal().shuffle()
        self.G.c.objective_deck.deal().shuffle()

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
                detail="You cant change faction because is choosen yet"
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
        self.G.c.steps.deal()
        self.G.c.steps.turn_phase = None

        return self

    def set_next_phase(self) -> 'GameProcessor':
        """Set next phase

        Returns:
            GameProcessor
        """
        if not self.G.c.steps.last or self.G.c.steps.last.id != settings.phases[5]:
            self.G.c.steps.pull()

        return self

    def set_mission_card(self) -> 'GameProcessor':
        """Set mission card on a turn

        Returns:
            GameProcessor
        """
        try:
            self.G.c.objective_deck.pop()
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

    def _check_analyct_condition(self) -> None:
        """Check conditions for play analyst ability
        """
        if self.G.c.steps.last is None or self.G.c.steps.last.id != settings.phases[0]:
            raise HTTPException(
                status_code=409,
                detail="Ability can't be played in any phases except 'briefing'."
                    )
        if not 'Analyst' in self.G.c.player.abilities:
            raise HTTPException(
                status_code=409,
                detail="No access to play ability of Analyst agent card."
                    )

    def play_analyst_for_look_the_top(self) -> 'GameProcessor':
        """Play analyst abylity for look the top cards

        Returns:
            GameProcessor
        """
        self._check_analyct_condition()

        if len([
            card.id for card
            in self.G.c.player.c.group_cards.current
            if card.pos_in_deck in [-1, -2, -3]
                ]) == 3:
            raise HTTPException(
                status_code=409,
                detail="Top 3 group cards is yet revealed for player."
                    )

        self.G.c.group_deck.temp_group = []

        for pos in range(-3, 0):
            card = self.G.c.group_deck.current[pos]
            try:
                self.G.c.player.c.group_cards.remove(card.id)
            except ValueError:
                pass
            self.G.c.player.c.group_cards.append(card)
            self.G.c.player.c.group_cards.current[-1].pos_in_deck = pos
            self.G.c.group_deck.temp_group.append(card.id)

        return self

    def play_analyst_for_arrange_the_top(
        self, top: List[str]) -> 'GameProcessor':
        """Play analyst abylity for rearrange the top cards

        Args:
            top (List[str]): arranged cards

        Returns:
            GameProcessor
        """
        self._check_analyct_condition()

        current = {}
        check = set()
        for _ in range(3):
            card = self.G.c.group_deck.pop()
            check.add(card.id)
            current[card.id] = card

        if check ^ set(top):

            for card in reversed(current.values()):
                self.G.c.group_deck.append(card)

            raise HTTPException(
                status_code=409,
                detail="Your list of cards and top cards not match."
                    )
        else:
            for card in top:
                self.G.c.group_deck.append(current[card])

        self.G.c.player.abilities.remove('Analyst')

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

        # phase = self.G.c.steps.turn_phase
        phase = self.G.c.steps.last.id if self.G.c.steps.last else None

        # briefing
        if phase == settings.phases[0]:

            # players has't priority
            if not self.G.c.player.has_priority \
                    and not self.G.c.bot.has_priority:
                raise HTTPException(
                    status_code=409,
                    detail="No one player has priority. Cant push to next phase."
                        )

            # objective card not defined
            if self.G.c.objective_deck.last is None:
                raise HTTPException(
                    status_code=409,
                    detail="Mission card undefined. Cant push to next phase."
                        )

            # analyst not used
            if 'Analyst' in self.G.c.player.abilities:
                raise HTTPException(
                    status_code=409,
                    detail="Analyst ability must be used."
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
        # phase = self.G.c.steps.turn_phase
        phase = self.G.c.steps.last.id if self.G.c.steps.last else None

        # set briefing states after next
        if phase == settings.phases[0]:

            self.set_mission_card()
            self.set_turn_priority()
            self.G.c.group_deck.deal()
            self.G.c.group_deck.pile.clear()
            self.G.c.player.c.group_cards.clear()
            self.G.c.bot.c.group_cards.clear()

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
