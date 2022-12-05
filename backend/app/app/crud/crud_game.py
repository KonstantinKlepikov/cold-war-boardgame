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

    def get_game_processor(
        self,
        current_data: model_game.CurrentGameData,
            ) -> game_logic.GameProcessor:
        """Get game processor

        Args:
            current_data (CurrentGameData): bd data object

        Returns:
            game_logic.GameProcessor: processor
        """
        game_proc = game_logic.GameProcessor(crud_card.cards.get_all_cards())
        return game_proc.init_game_data(current_data)

    def create_new_game(self, obj_in: schema_game.CurrentGameData) -> None:
        """Create new game
        """
        db_data = jsonable_encoder(obj_in)
        current_data = self.model(**db_data)
        current_data.save()

    def deal_and_shuffle_decks(
        self,
        current_data: model_game.CurrentGameData,
        game_proc: game_logic.GameProcessor,
            ) -> game_logic.GameProcessor:
        """Shuffle objective and group decks

        Args:
            current_data (model_game.CurrentGameData)
            game_proc (game_logic.GameProcessor)

        Returns:
            game_logic.GameProcessor
        """
        print(current_data.game_decks.group_deck.deck_len)
        print(current_data.game_decks.objective_deck.current)
        game_proc.game.group_deck.deal()
        game_proc.game.group_deck.shuffle()

        game_proc.game.objective_deck.deal()
        game_proc.game.objective_deck.shuffle()

        obj_current = game_proc.game.objective_deck.get_current_names()
        current_data.game_decks.objective_deck.current = obj_current
        current_data.game_decks.objective_deck.deck_len = len(obj_current)

        group_current = game_proc.game.group_deck.get_current_names()
        current_data.game_decks.group_deck.current = group_current
        current_data.game_decks.group_deck.deck_len = len(group_current)

        current_data.save()

        print("-"*20)
        print(current_data.game_decks.group_deck.deck_len)
        print(current_data.game_decks.objective_deck.current)

        return game_proc

    def set_faction(self, login: str, faction: Faction) -> None:
        """Set player and opponent faction

        Args:
            login (str): player login
            faction (Literal['kgb', 'cia']): player faction
        """
        current_data = self.get_current_game_data(login)

        if current_data.players[0].faction is None:
            current_data.players[0].faction = faction.value
            if faction == Faction.CIA:
                current_data.players[1].faction = 'kgb'
            else:
                current_data.players[1].faction = 'cia'
            current_data.save()

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
        current_data = self.get_current_game_data(login)

        if current_data.players[0].has_priority is None:
            val = None
            if priority.value == Priority.TRUE:
                val = True
            elif priority.value == Priority.FALSE:
                val = False
            elif priority.value == Priority.RANDOM:
                val = random.choice([True, False])
                # TODO: use bgameb here

            current_data.players[0].has_priority = val
            current_data.players[1].has_priority = not val
            current_data.save()

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
        current_data: model_game.CurrentGameData,
        game_proc: game_logic.GameProcessor,
            ) -> game_logic.GameProcessor:
        """Set next phase

        Args:
            current_data (model_game.CurrentGameData)
            game_proc (game_logic.GameProcessor)

        Returns:
            game_logic.GameProcessor
        """
        phase = current_data.game_steps.turn_phase
        if not phase == settings.phases[5] \
                and not current_data.game_steps.is_game_end == True:

            phase = game_proc.game.game_steps.pull().id

            current_data.game_steps.turn_phase = phase
            current_data.game_steps.turn_phases_current = game_proc.game.game_steps.get_current_names()
            game_proc.game.turn_phase = phase
            current_data.save()

        return game_proc

    def set_mission_card(
        self,
        current_data: model_game.CurrentGameData,
        game_proc: game_logic.GameProcessor,
            ) -> game_logic.GameProcessor:
        """Set mission card on a turn

        Args:
            current_data (model_game.CurrentGameData)
            game_proc (game_logic.GameProcessor)

        Returns:
            game_logic.GameProcessor
        """
        try:
            game_proc.game.mission_card = game_proc.game.objective_deck.current.pop().id
        except IndexError:
            raise HTTPException(
                status_code=409,
                detail="Objective deck is empty."
                    )

        current_names = game_proc.game.objective_deck.get_current_names()
        current_data.game_decks.objective_deck.current = current_names
        current_data.game_decks.objective_deck.deck_len = len(current_names)
        current_data.game_decks.mission_card = game_proc.game.mission_card

        current_data.save()

        return game_proc

    def set_phase_conditions_after_next(
        self,
        current_data: model_game.CurrentGameData,
        game_proc: game_logic.GameProcessor,
            ) -> None:
        """Set som phase conditions after push phase

        Args:
            current_data (model_game.CurrentGameData)
            game_proc (game_logic.GameProcessor)

        Returns:
            game_logic.GameProcessor
        """
        phase = current_data.game_steps.turn_phase

        # set briefing states after next
        if phase == settings.phases[0]:

            self.set_mission_card(current_data, game_proc)

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
