import bgameb
from app.schemas import schema_game
from app.crud import crud_card


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

    def __init__(self) -> None:
        self.game = bgameb.Game('Cold War Game')
        self.cards = crud_card.cards.get_all_cards()


    def init_new_objective_deck(self):
        """Init new objective deck
        """
        self.game.add(bgameb.Shaker('Objective Deck'))
        for card in self.cards['objective_cards']:
            self.game.objective_deck.add(bgameb.Card(card['name']))
