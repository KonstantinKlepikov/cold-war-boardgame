import random
from typing import Optional
from fastapi.encoders import jsonable_encoder
from fastapi import HTTPException
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

        Returns:
            CurrentGameData: bd data object
        """
        return self.model.objects(players__login=login).first()

    def create_new_game(self, obj_in: schema_game.CurrentGameData) -> None:
        """Create new game
        """
        db_data = jsonable_encoder(obj_in)
        game = self.model(**db_data)

        # add current cards
        current = crud_card.cards.get_cards_names()
        game.game_decks.group_deck.current = current['group_cards']
        game.game_decks.objective_deck.current = current['objective_cards']

        game.save()

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

    def set_next_turn_phase(
        self,
        login: str,
        turn: bool,
        phase: bool,
            ) -> None:
        """Set next turn or/and next phase

        Args:
            login (str): player login
            turn (bool): push the turn
            phase (bool): push the phase
        """
        data = self.get_current_game_data(login)
        if data.game_steps.is_game_end:
            raise HTTPException(
                status_code=409,
                detail="Something can't be changed, because game is end"
                    )

        if turn:
            data.game_steps.game_turn += 1
            data.game_steps.turn_phase = settings.phases[0]
            data.save()

        if phase:
            if data.game_steps.turn_phase is None:
                data.game_steps.turn_phase = settings.phases[0]
                data.save()

            elif data.game_steps.turn_phase == settings.phases[-1]:
                raise HTTPException(
                    status_code=409,
                    detail="This phase is last in a turn. Change turn number "
                           "before get next phase"
                        )
            else:
                self._chek_phase_conditions(login)
                ind = settings.phases.index(data.game_steps.turn_phase) + 1
                data.game_steps.turn_phase = settings.phases[ind]
                data.save()

    def set_next_turn(
        self,
        login: str,
            ) -> None:
        """Set next turn

        Args:
            login (str): player login
        """
        data = self.get_current_game_data(login)
        if data.game_steps.is_game_end:
            raise HTTPException(
                status_code=409,
                detail="Something can't be changed, because game is end"
                    )

        data.game_steps.game_turn += 1
        data.game_steps.turn_phase = settings.phases[0]
        data.save()

    def set_next_phase(
        self,
        login: str,
            ) -> None:
        """Set next phase

        Args:
            login (str): player login
        """
        data = self.get_current_game_data(login)
        if data.game_steps.is_game_end:
            raise HTTPException(
                status_code=409,
                detail="Something can't be changed, because game is end"
                    )

        if data.game_steps.turn_phase is None:
            data.game_steps.turn_phase = settings.phases[0]
            data.save()

        elif data.game_steps.turn_phase == settings.phases[-1]:
            raise HTTPException(
                status_code=409,
                detail="This phase is last in a turn. Change turn number "
                        "before get next phase"
                    )
        else:
            self._chek_phase_conditions(login)
            ind = settings.phases.index(data.game_steps.turn_phase) + 1
            data.game_steps.turn_phase = settings.phases[ind]
            data.save()

    def set_mission_card(
        self,
        login: str
            ) -> None:
        """Set mission card on a turn

        Args:
            login (str): player login
        """

    def _chek_phase_conditions(
        self,
        login: str
            ) -> None:
        """_summary_

        Args:
            login (str): _description_
        """
        data = self.get_current_game_data(login)
        phase = data.game_steps.turn_phase

        # check briefing before next
        if phase == settings.phases[0]:

            # players has priority
            if not data.players[0].has_priority and not data.players[1].has_priority:
                raise HTTPException(
                    status_code=409,
                    detail="No one player has priority. Cant next from briefing."
                        )

            # objective card defined
            if not data.game_decks.mission_card:
                raise HTTPException(
                    status_code=409,
                    detail="Mission card undefined."
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


game = CRUDGame(model_game.CurrentGameData)
