import pytest
import bgameb
from typing import Generator
from fastapi import HTTPException
from app.crud import crud_game
from app.config import settings
from app.core import game_logic


class TestGameData:
    """Test game data functions
    """

    def test_make_game_data(self) -> None:
        """Test make_game_data()
        """
        data = game_logic.make_game_data(settings.user0_login)

        assert data, 'empty state'
        assert data.game_steps.game_turn == 0, 'wrong game turn'
        assert not data.game_steps.turn_phase, 'wrong turn phase'
        assert not data.game_steps.is_game_end, 'game end'

        assert data.players[0].login == settings.user0_login, 'wrong user'
        assert not data.players[0].has_priority, 'wrong priority'
        assert data.players[0].is_bot == False, 'wrong is_bot'
        assert not data.players[0].faction, 'wrong faction'
        assert data.players[0].score == 0, 'wrong score'
        assert len(data.players[0].player_cards.agent_cards) == 6, 'hasnt cards'
        assert data.players[0].player_cards.group_cards == [], 'hasnt cards'
        assert data.players[0].player_cards.objective_cards == [], 'hasnt cards'

        assert not data.players[1].login, 'wrong user'
        assert not data.players[1].has_priority, 'wrong priority'
        assert data.players[1].is_bot == True, 'wrong is_bot'
        assert not data.players[1].faction, 'wrong faction'
        assert data.players[1].score == 0, 'wrong score'
        assert len(data.players[1].player_cards.agent_cards) == 6, 'hasnt cards'
        assert data.players[1].player_cards.group_cards == [], 'hasnt cards'
        assert data.players[1].player_cards.objective_cards == [], 'hasnt cards'

        assert data.game_decks.group_deck.deck_len == 0, 'wrong group len'
        assert data.game_decks.group_deck.pile == [], 'wrong group pile'
        with pytest.raises(
            AttributeError,
            match="object has no attribute"
                ):
            data.game_decks.group_deck.current
        assert data.game_decks.objective_deck.deck_len == 0, \
            'wrong objective len'
        assert data.game_decks.objective_deck.pile == [], \
            'wrong objective pile'
        with pytest.raises(
            AttributeError,
            match="object has no attribute"
                ):
            data.game_decks.objective_deck.current
        assert not data.game_decks.mission_card, 'wrong mission card'


class TestGameProcessor:
    """Test GameProcessor class
    """

    def test_create_game(self, game_proc: game_logic.GameProcessor) -> None:
        """Test game is created
        """
        assert isinstance(game_proc.game, bgameb.Game), 'wrong game'
        assert isinstance(game_proc.cards, dict), 'not a cards'

    def _check_if_current_raise_exception(
        self,
        game_proc: game_logic.GameProcessor
            ) -> None:
        """Exception is raised if player not starts any games
        """
        with pytest.raises(
            HTTPException,
            ):
            game_proc._check_if_current()

    def test_init_game_data(
        self,
        game: crud_game.CRUDGame,
        game_proc: game_logic.GameProcessor
            ) -> None:
        """Test init new deck init deck in Game objects
        """
        game_proc = game_proc.init_game_data(
            game.get_current_game_data(settings.user0_login)
                )
        # game
        assert isinstance(game_proc, game_logic.GameProcessor), 'wrong proc'
        assert game_proc.game.player, 'player not inited'
        assert len(game_proc.game.player.other) > 0, 'empty player other'
        assert game_proc.game.bot, 'bot not inited'
        assert len(game_proc.game.bot.other) > 0, 'empty bot other'

        # steps
        assert game_proc.game.game_turn == 0, 'wrong turn'
        assert game_proc.game.turn_phase is None, 'wrong phase'
        assert game_proc.game.is_game_end == False, 'game is end'
        assert len(game_proc.game.game_steps.current) == 6, 'wrong current'

        # objectives
        assert len(game_proc.game.objective_deck) == 24, 'wrong objective args len' # TODO: change in bgameb
        assert game_proc.game.mission_card is None, 'wrong mission card'
        assert not game_proc.game.objective_deck.current, 'nonempty objective current'
        with pytest.raises(AttributeError):
            game_proc.game.objective_deck.other._id

        # groups
        assert len(game_proc.game.group_deck) == 27, 'wrong group args len' # TODO: change in bgameb
        assert not game_proc.game.group_deck.current, 'group current'
        with pytest.raises(AttributeError):
            game_proc.game.group_deck.other._id

    # def test_feel_the_decks_if_current_exist(
    #     self,
    #     game: crud_game.CRUDGame,
    #     game_proc: game_logic.GameProcessor,
    #         ) -> None:
    #     """Test deal_cards_from_db()
    #     """
    #     obj_in = game_logic.make_game_data(settings.user0_login)
    #     game.create_new_game(obj_in)
    #     game.deal_and_shuffle_decks(settings.user0_login)

    #     game_proc.deal_cards_from_db(
    #         game.get_current_game_data(settings.user0_login)
    #             )
    #     assert len(game_proc.game.objective_deck.current) == 22, \
    #         'wring proc current obj deck'


class TestCheckPhaseConditions:
    """Test chek_phase_conditions_before_next()
    """

    def test_chek_phase_conditions_before_next_raise_if_no_priority(
        self,
        connection: Generator,
            ) -> None:
        """Test chek_phase_conditions_before_next() if no player has
        priority in briefing
        """
        data = connection['CurrentGameData'].objects().first()
        data.game_steps.turn_phase = settings.phases[0]
        data.save()

        with pytest.raises(
            HTTPException,
            ):
            game_logic.chek_phase_conditions_before_next(data)

    def test_chek_phase_conditions_before_next_if_last_phase(
        self,
        connection: Generator,
            ) -> None:
        """Test chek_phase_conditions_before_next() if last phase
        and needed push to next tun
        """
        data = connection['CurrentGameData'].objects().first()
        data.game_steps.turn_phase = settings.phases[5]
        data.save()

        with pytest.raises(
            HTTPException,
                ):
            game_logic.chek_phase_conditions_before_next(data)

    def test_chek_phase_conditions_before_next_if_game_end(
        self,
        connection: Generator,
            ) -> None:
        """Test chek_phase_conditions_before_next() if game end
        """
        data = connection['CurrentGameData'].objects().first()
        data.game_steps.is_game_end = True
        data.save()

        with pytest.raises(
            HTTPException,
            ):
            game_logic.chek_phase_conditions_before_next(data)