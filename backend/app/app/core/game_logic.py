import bgameb
from typing import Dict, List, Union, Optional
from fastapi import HTTPException
from app.schemas import schema_game
from app.models import model_game
from app.config import settings


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


def chek_phase_conditions_before_next(
    current_data: Optional[model_game.CurrentGameData],
        ) -> None:
    """Check game conition before push to next phase
    and raise exception if any check fails

    Args:
        current_data (str): current game data for check
    """
    if current_data.game_steps.is_game_end:
        raise HTTPException(
            status_code=409,
            detail="Something can't be changed, because game is end."
                )

    phase = current_data.game_steps.turn_phase

    # briefing
    if phase == settings.phases[0]:

        # players has priority
        if not current_data.players[0].has_priority \
                and not current_data.players[1].has_priority:
            raise HTTPException(
                status_code=409,
                detail="No one player has priority. Cant push to next phase."
                    )

        # objective card defined
        if not current_data.game_decks.mission_card:
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


class GameProcessor:
    """Create the game object to manipulation of game tools
    """

    def __init__(
        self,
        cards: Dict[str, List[Dict[str, Union[str, int]]]],
            ) -> None:
        self.game = bgameb.Game('Cold War Game')
        self.cards = cards

    def _check_if_current(
        self,
        current_data: Optional[model_game.CurrentGameData]
            ):
        if not current_data:
            raise HTTPException(
                status_code=404,
                detail="Cant find current game data in db. For start "
                    "new game use /game/create endpoint",
                        )

    def init_game_data(
        self,
        current_data: Optional[model_game.CurrentGameData]
            ):
        """Init new objective deck

        Args:
            current_data (Optional[model_game.CurrentGameData])

        Returns:
            GameProcessor: initet game processor
        """
        self._check_if_current(current_data)

        # init ptayers
        for p in current_data.players:
            data: dict = p.to_mongo().to_dict()
            name = 'bot' if data['is_bot'] == True else 'player'
            player = bgameb.Player(name, **data)
            self.game.add(player)

        # init group deck
        self.game.add(bgameb.Deck('Group Deck'))
        for c in self.cards['group_cards']:
            c.pop('_id', None)
            card = bgameb.Card(
                c['name'],
                **c
                )
            self.game.group_deck.add(card)

        # init objective deck
        self.game.add(bgameb.Deck('Objective Deck'))
        for c in self.cards['objective_cards']:
            c.pop('_id', None)
            card = bgameb.Card(
                c['name'],
                **c
                )
            self.game.objective_deck.add(card)

        # init game steps
        self.game.add(bgameb.Steps('game_steps'))
        for num, val in enumerate(settings.phases):
            step = bgameb.Step(val, priority=num)
            self.game.game_steps.add(step)

        # fill game steps
        self.game.game_turn = current_data.game_steps.game_turn
        self.game.turn_phase = current_data.game_steps.turn_phase
        self.game.is_game_end = current_data.game_steps.is_game_end
        self.game.game_steps.deal(current_data.game_steps.turn_phases_left)

        # fill objective deck
        if current_data.game_decks.objective_deck.current:
            self.game.objective_deck.deal(
                current_data.game_decks.objective_deck.current
                    )
        m = current_data.game_decks.mission_card

        # fill mission card
        self.game.mission_card = m if m else None

        # from pprint import pprint
        # pprint(self.game.to_dict())
        # print('---'*20)

        return self
