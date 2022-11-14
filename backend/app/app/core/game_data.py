from app.schemas import schema_game


def make_game_data(login: str) -> schema_game.CurrentGameData:
    """Make game data for start the game

    Returns:
        CurrentGameData: game data schema
    """
    agent_cards = [
            {'agent_card': {'name': 'Master Spy'}},
            {'agent_card': {'name': 'Deputy Director'}},
            {'agent_card': {'name': 'Double Agent'}},
            {'agent_card': {'name': 'Analyst'}},
            {'agent_card': {'name': 'Assassin'}},
            {'agent_card': {'name': 'Director'}}
            ]

    new_game = {
                'players':
                    [
                        {
                            'is_bot': False,
                            'player_cards': {'agent_cards': agent_cards},
                            'user': {'login': login},
                        },
                        {
                            'is_bot': True,
                            'player_cards': {'agent_cards': agent_cards},
                            'user': None,
                        }
                    ]
                }

    return schema_game.CurrentGameData(**new_game)
