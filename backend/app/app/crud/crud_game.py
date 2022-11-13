from typing import Optional, List
from app.crud import crud_user, crud_base, crud_card
from app.models import model_game
from app.schemas import schema_game, schema_user, schema_cards


# def make_user(
#     login: Optional[str] = None
#         ) -> Optional[schema_user.UserCurrentData]:
#     """Make user from schema

#     Args:
#         login (Optional[str], optional): Login of player. Defaults to None.

#     Returns:
#         Optional[UserCurrentData]: Existed user schema
#     """
#     if login:
#         user = crud_user.user.get_by_login(login)
#         if user:
#             return schema_user.UserCurrentData(login=login)
#         else:
#             raise KeyError
#     else:
#         return schema_user.UserCurrentData()


# def make_agents_cards() -> List[schema_game.PlayerAgentCard]:
#     """Make agents cards list

#     Returns:
#         List[PlayerAgentCard]: agent cards
#     """
#     all_cards = crud_card.cards.get_all_cards()
#     return [
#         schema_game.PlayerAgentCard(
#             agent_card=schema_cards.CardName(name=card.name)
#             ) for card in all_cards.agent_cards
#         ]


# def make_player(
#     login: Optional[str] = None
#         ) -> schema_game.Player:
#     """Make player from schema

#     Args:
#         login (Optional[str], optional): Login of player. Defaults to None.

#     Returns:
#         Player: Existed player or bot
#     """
#     player_cards=schema_game.PlayerCards(agent_cards=make_agents_cards())
#     user = make_user(login)
#     print(user)
#     if login:
#         return schema_game.Player(
#             is_bot=False,
#             player_cards=player_cards,
#             user=user.dict(),
#                 )
#     else:
#         return schema_game.Player(
#             is_bot=True,
#             player_cards=player_cards,
#             user=user.dict()
#                 )


# def make_players(
#     login: Optional[str] = None
#         ) -> List[schema_game.Player]:
#     """Make players for game

#     Args:
#         login (Optional[str], optional): Login of player. Defaults to None.

#     Returns:
#         List[Player]: lisat of players
#     """
#     return [make_player(login), make_player(), ]


class CRUDGame(crud_base.CRUDBase[model_game.CurrentGameData, schema_game.CurrentGameData]):
    """Crud for game current state document
    """

    def get_current_game_data(self, login: str) -> Optional[model_game.CurrentGameData]:
        """Get current game data from db

        Returns:
            CurrentGameData: bd data object
        """
        return self.model.objects(players__user__login=login).first()

    # def make_new_game(self, login: str) -> schema_game.CurrentGameData:
    #     """Make new current game data
    #     """
    #     return self.schema(players=make_players(login))

    def create_new_game(self, login: str) -> None:
        """Create new game
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
                            'user': {'login': login },
                        },
                        {
                            'is_bot': True,
                            'player_cards': {'agent_cards': agent_cards},
                            'user': None,
                        }
                    ]
                }

        # game = self.model(**self.make_new_game(login).dict())
        game = self.model(**new_game )
        game.save(cascade=True)


game = CRUDGame(model_game.CurrentGameData, schema_game.CurrentGameData)
