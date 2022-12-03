import random
from typing import Optional
from fastapi.encoders import jsonable_encoder
from fastapi import HTTPException
from app.core import game_logic
from app.crud import crud_base,crud_card
from app.models import model_game
from app.schemas import schema_game
from app.constructs import Priority, Faction
from app.config import settings


class CRUDGame(
    crud_base.CRUDBase[
        model_game.CurrentGameData,
        schema_game.CurrentGameData
            ]
        ):
    """Crud for game current state document
    """
    def get_current_game_data(self, login: str) -> Optional[model_game.CurrentGameData]:
        """Get current game data from db

        Args:
            login (str): player login

        Returns:
            CurrentGameData: bd data object
        """
        return self.model.objects(players__login=login).first()

    def get_game_processor(self, login: str) -> game_logic.GameProcessor:
        """Get game processor

        Args:
            login (str): player login

        Returns:
            game_logic.GameProcessor: processor
        """
        return game_logic.GameProcessor(
            cards=crud_card.cards.get_all_cards(),
            current_data=self.get_current_game_data(login)
                )

    def create_new_game(self, obj_in: schema_game.CurrentGameData) -> None:
        """Create new game
        """
        db_data = jsonable_encoder(obj_in)
        current_data = self.model(**db_data)

        current_data.save()

    def deal_and_shuffle_decks(self, login: str) -> None:
        """Shuffle objective and group decks

        Args:
            login (str): player login
        """
        # create game and add cards
        game_proc = self.get_game_processor(login)
        game_proc.init_game_data()

        # deal and shuffle cards
        game_proc.game.group_deck.deal()
        game_proc.game.group_deck.shuffle()

        game_proc.game.objective_deck.deal()
        game_proc.game.objective_deck.shuffle()

        obj_current = game_proc.game.objective_deck.get_current_names()
        game_proc.current_data.game_decks.objective_deck.current = obj_current
        game_proc.current_data.game_decks.objective_deck.deck_len = len(obj_current)

        group_current = game_proc.game.group_deck.get_current_names()
        game_proc.current_data.game_decks.group_deck.current = group_current
        game_proc.current_data.game_decks.group_deck.deck_len = len(group_current)

        game_proc.current_data.save()

    def set_faction(self, login: str, faction: Faction) -> None:
        """Set player and opponent faction

        Args:
            login (str): player login
            faction (Literal['kgb', 'cia']): player faction
        """
        data = self.get_current_game_data(login)

        if data.players[0].faction is None:
            data.players[0].faction = faction.value
            if faction == Faction.CIA:
                data.players[1].faction = 'kgb'
            else:
                data.players[1].faction = 'cia'
            data.save()

    def set_priority(
        self,
        login: str,
        priority: Priority
            ) -> None:
        """Set priority for player

        Args:
            login (str): player login
            priority (Priority): priority.
        """
        data = self.get_current_game_data(login)

        if data.players[0].has_priority is None:
            val = None
            if priority.value == Priority.TRUE:
                val = True
            elif priority.value == Priority.FALSE:
                val = False
            elif priority.value == Priority.RANDOM:
                val = random.choice([True, False])
                # TODO: use bgameb here

            data.players[0].has_priority = val
            data.players[1].has_priority = not val
            data.save()

    # def set_next_turn_phase(
    #     self,
    #     login: str,
    #     turn: bool,
    #     phase: bool,
    #         ) -> None:
    #     """Set next turn or/and next phase

    #     Args:
    #         login (str): player login
    #         turn (bool): push the turn
    #         phase (bool): push the phase
    #     """
    #     current_data = self.get_current_game_data(login)
    #     if current_data.game_steps.is_game_end:
    #         raise HTTPException(
    #             status_code=409,
    #             detail="Something can't be changed, because game is end"
    #                 )

    #     if turn:
    #         current_data.game_steps.game_turn += 1
    #         current_data.game_steps.turn_phase = settings.phases[0]
    #         current_data.save()

    #     if phase:
    #         if current_data.game_steps.turn_phase is None:
    #             current_data.game_steps.turn_phase = settings.phases[0]
    #             current_data.save()

    #         elif current_data.game_steps.turn_phase == settings.phases[-1]:
    #             raise HTTPException(
    #                 status_code=409,
    #                 detail="This phase is last in a turn. Change turn number "
    #                        "before get next phase"
    #                     )
    #         else:
    #             self.chek_phase_conditions_before_next(login)
    #             ind = settings.phases.index(current_data.game_steps.turn_phase) + 1
    #             current_data.game_steps.turn_phase = settings.phases[ind]
    #             current_data.save()

    def set_next_turn(
        self,
        login: str,
            ) -> None:
        """Set next turn

        Args:
            login (str): player login
        """
        current_data = self.get_current_game_data(login)
        if current_data.game_steps.is_game_end:
            raise HTTPException(
                status_code=409,
                detail="Something can't be changed, because game is end"
                    )

        current_data.game_steps.game_turn += 1
        current_data.game_steps.turn_phase = settings.phases[0]
        current_data.save()

    def set_next_phase(
        self,
        login: str,
            ) -> None:
        """Set next phase

        Args:
            login (str): player login
        """
        current_data = self.get_current_game_data(login)
        game_logic.chek_phase_conditions_before_next(current_data)

        #TODO: make it wth GameProcessor
        if current_data.game_steps.turn_phase is None:
            current_data.game_steps.turn_phase = settings.phases[0]
            current_data.save()

        else:
            ind = settings.phases.index(current_data.game_steps.turn_phase) + 1
            current_data.game_steps.turn_phase = settings.phases[ind]
            current_data.save()

    def set_mission_card(
        self,
        login: str
            ) -> None:
        """Set mission card on a turn

        Args:
            login (str): player login
        """

    def set_phase_conditions_after_next(
        self,
        login: str
            ) -> None:
        """_summary_

        Args:
            login (str): _description_
        """
        cards = crud_card.cards.get_all_cards()
        current_data = self.get_current_game_data(login)
        phase = current_data.game_steps.turn_phase
        game_proc = game_logic.GameProcessor(
            cards=cards, current_data=current_data
                )

        # set briefing states after next
        if phase == settings.phases[0]:

            # mission card
            try:
                mission_card = game_proc.game.objective_deck.current.pop().id
            except IndexError:
                raise HTTPException(
                    status_code=409,
                    detail="Objective deck is empty."
                        )

            obj_current = game_proc.game.objective_deck.current.get_current_names()
            current_data.game_decks.objective_deck.current = obj_current
            current_data.game_decks.objective_deck.deck_len = len(obj_current)
            current_data.game_decks.mission_card = mission_card

            current_data.save()

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


game = CRUDGame(model_game.CurrentGameData)
