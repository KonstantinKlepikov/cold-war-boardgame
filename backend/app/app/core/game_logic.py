import bgameb
from typing import Dict, List, Union, Optional
from fastapi import HTTPException
from app.schemas import schema_game
from app.models import model_game


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

    def init_game_data(self):
        """Init new objective deck
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
            del c['_id']
            card = bgameb.Card(
                c['name'],
                **c
                )
            self.game.group_deck.add(card)

        # init objective deck
        self.game.add(bgameb.Deck('Objective Deck'))
        for c in self.cards['objective_cards']:
            del c['_id']
            card = bgameb.Card(
                c['name'],
                **c
                )
            self.game.objective_deck.add(card)

        # from pprint import pprint
        # pprint(self.game.to_dict())
        # print('---'*20)
