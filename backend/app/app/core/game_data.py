import bgameb
from fastapi import HTTPException
from app.schemas import schema_game
from app.crud import crud_card, crud_game


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

    def __init__(self, login: str) -> None:
        self.game = bgameb.Game('Cold War Game')
        self.cards = crud_card.cards.get_all_cards()
        current = crud_game.game.get_current_game_data(login)
        if current:
            self.current = current
        else:
            raise HTTPException(
                status_code=404,
                detail="Cant find current game data in db. For start "
                    "new game use /game/create endpoint",
                    )

    def init_new_objective_deck(self):
        """Init new objective deck
        """
        self.game.add(bgameb.Shaker('Objective Deck'))
        for card in self.cards['objective_cards']:
            self.game.objective_deck.add(bgameb.Card(card['name']))

    def init_player(self):
        """Init game player
        """
        players = self.current.players
        for p in players:
            player = bgameb.Player(p.get('login', 'bot'))
            player.has_priority = p.get('has_priority')
            player.is_bot = p.get('is_bot')
            player.score = p.get('score')
            player.faction = p.get('faction')
            player.player_cards = None # TODO: how?


    def init_new_decks(self):
        """Init new objective deck
        """

        # init agent decks


        # init groups
        self.game.add(bgameb.Shaker('Group Deck'))
        for val in self.cards['group_cards']:
            card = bgameb.Card(val['name'])
            card.faction = val.get('faction')
            card.influence = val.get('influence')
            card.power = val.get('pover')
            self.game.group_deck.add(card)

        # init objective
        self.game.add(bgameb.Shaker('Objective Deck'))
        for val in self.cards['objective_cards']:
            card = bgameb.Card(val['name'])
            card.bias_icons = val.get('bias_icons')
            card.population = val.get('population')
            card.special_ability = val.get('special_ability')
            card.stability = val.get('stability')
            card.victory_points = val.get('victory_points')
            self.game.objective_deck.add(card)
