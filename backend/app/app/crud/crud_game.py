import random
from typing import Optional
from fastapi.encoders import jsonable_encoder
from fastapi import HTTPException
from app.core import game_logic
from app.crud import crud_base, crud_card, crud_game
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
        login: str,
            ) -> game_logic.GameProcessor:
        """Get game processor

        Args:
            current_data (CurrentGameData): bd data object
            login (str): user login

        Returns:
            game_logic.GameProcessor: processor
        """
        game_proc = game_logic.GameProcessor(
            crud_card.cards.get_all_cards(),
            crud_game.game.get_current_game_data(login)
                )
        return game_proc.init_game_data()

    def create_new_game(self, obj_in: schema_game.CurrentGameData) -> None:
        """Create new game
        """
        db_data = jsonable_encoder(obj_in)
        current_data = self.model(**db_data)
        current_data.save()

    def deal_and_shuffle_decks(
        self,
        game_proc: game_logic.GameProcessor,
            ) -> game_logic.GameProcessor:
        """Shuffle objective and group decks

        Args:
            game_proc (game_logic.GameProcessor)

        Returns:
            game_logic.GameProcessor
        """
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

        return game_proc

    def set_faction(
        self,
        faction: Faction,
        game_proc: game_logic.GameProcessor,
            ) -> game_logic.GameProcessor:
        """Set player and opponent faction

        Args:
            faction (Literal['kgb', 'cia']): player faction
            game_proc (game_logic.GameProcessor)

        Returns:
            game_logic.GameProcessor
        """
        if game_proc.current_data.players[0].faction:
            raise HTTPException(
                status_code=409,
                detail="Factions yet setted for this game"
                    )

        game_proc.game.player.faction = faction.value
        game_proc.game.bot.faction = 'kgb' if faction == Faction.CIA else 'cia'

        game_proc.current_data.players[0].faction = faction.value
        game_proc.current_data.players[1].faction = game_proc.game.bot.faction

        game_proc.current_data.save()

        return game_proc

    def set_priority(
        self,
        priority: Priority,
        game_proc: game_logic.GameProcessor,
            ) -> game_logic.GameProcessor:
        """Set priority for player

        Args:
            priority (Priority): priority.
            game_proc (game_logic.GameProcessor)

        Returns:
            game_logic.GameProcessor
        """
        if game_proc.current_data.players[0].has_priority \
                or game_proc.current_data.players[1].has_priority:
            raise HTTPException(
                status_code=409,
                detail="Priority yet setted for this game"
                    )

        if priority == Priority.TRUE:
            val = True
        elif priority == Priority.FALSE:
            val = False
        elif priority == Priority.RANDOM:
            val = random.choice([True, False])

        game_proc.game.player.has_priority = val
        game_proc.game.bot.has_priority = not val

        game_proc.current_data.players[0].has_priority = val
        game_proc.current_data.players[1].has_priority = not val

        game_proc.current_data.save()

        return game_proc

    def set_next_turn(
        self,
        game_proc: game_logic.GameProcessor,
            ) -> game_logic.GameProcessor:
        """Set next turn

        Args:
            game_proc (game_logic.GameProcessor)

        Returns:
            game_logic.GameProcessor
        """
        if game_proc.current_data.game_steps.is_game_end:
            raise HTTPException(
                status_code=409,
                detail="Something can't be changed, because game is end"
                    )

        game_proc.game.game_turn += 1

        game_proc.current_data.game_steps.game_turn += 1
        game_proc.current_data.game_steps.turn_phase = settings.phases[0]
        game_proc.current_data.save()

        return game_proc

    def set_next_phase(
        self,
        game_proc: game_logic.GameProcessor,
            ) -> game_logic.GameProcessor:
        """Set next phase

        Args:
            game_proc (game_logic.GameProcessor)

        Returns:
            game_logic.GameProcessor
        """
        if game_proc.current_data.game_steps.is_game_end:
            raise HTTPException(
                status_code=409,
                detail="Something can't be changed, because game is end"
                    )

        phase = game_proc.current_data.game_steps.turn_phase
        if not phase == settings.phases[5] \
                and not game_proc.current_data.game_steps.is_game_end == True:

            phase = game_proc.game.game_steps.pull().id

            game_proc.current_data.game_steps.turn_phase = phase
            game_proc.current_data.game_steps.turn_phases_current = \
                game_proc.game.game_steps.get_current_names()
            game_proc.game.turn_phase = phase
            game_proc.current_data.save()

        return game_proc

    def set_mission_card(
        self,
        game_proc: game_logic.GameProcessor,
            ) -> game_logic.GameProcessor:
        """Set mission card on a turn

        Args:
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

        game_proc.current_data.game_decks.objective_deck.current = current_names
        game_proc.current_data.game_decks.objective_deck.deck_len = len(current_names)
        game_proc.current_data.game_decks.mission_card = game_proc.game.mission_card
        game_proc.current_data.save()

        return game_proc

    def set_phase_conditions_after_next(
        self,
        game_proc: game_logic.GameProcessor,
            ) -> game_logic.GameProcessor:
        """Set som phase conditions after push phase

        Args:
            game_proc (game_logic.GameProcessor)

        Returns:
            game_logic.GameProcessor
        """
        phase = game_proc.current_data.game_steps.turn_phase

        # set briefing states after next
        if phase == settings.phases[0]:

            game_proc = self.set_mission_card(game_proc)

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

        return game_proc


game = CRUDGame(model_game.CurrentGameData)
