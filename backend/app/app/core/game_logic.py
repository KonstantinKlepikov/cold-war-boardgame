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

    # before start first turn
    if phase is None:
        pass

    # briefing
    elif phase == settings.phases[0]:

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
        current_data: Optional[model_game.CurrentGameData],
            ) -> None:
        self.game = bgameb.Game('Cold War Game')
        self.cards = cards

        if current_data:
            self.current_data = current_data
        else:
            raise HTTPException(
                status_code=404,
                detail="Cant find current game data in db. For start "
                    "new game use /game/create endpoint",
                    )

    def init_game_data(self) -> bgameb.Game:
        """Init new objective deck

        Returns:
            bgameb.Game: initet game object
        """
        # init ptayers
        for p in self.current_data.players:
            data: dict = p.to_mongo().to_dict()
            name = 'bot' if data['is_bot'] == True else 'player'
            player = bgameb.Player(name, **data)
            self.game.add(player)

            # init agent deck
            # self.game[name].add(bgameb.Shaker('Agent Deck'))
            # for c in data['player_cards']['agent_cards']:
            #     m = {**c, **self._cards['agent_cards'][c['name']]}
            # # for c in self.cards['agent_cards']:

            #     card = bgameb.Card(
            #         c['name'],
            #         **m
            #         )
            #     self.game[name].agent_deck.add(card)

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

        # from pprint import pprint
        # pprint(self.game.to_dict())
        # print('---'*20)

        return self.game
