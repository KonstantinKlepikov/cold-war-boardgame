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

    def test_create_game(self, game_proc: game_logic.GameProcessor_) -> None:
        """Test game is created
        """
        assert isinstance(game_proc.G, bgameb.Game), 'wrong game'
        assert isinstance(game_proc.cards, dict), 'not a cards'

    def test_check_if_current_raise_exception(
        self,
        game_proc: game_logic.GameProcessor_
            ) -> None:
        """Exception is raised if player not starts any games
        """
        with pytest.raises(
            HTTPException,
            ):
            game_proc._check_if_current(None)

    def test_fill_data(
        self,
        game_proc: game_logic.GameProcessor_
            ) -> None:
        """Test init new deck init deck in Game objects
        """
        game_proc = game_proc.fill()
        assert isinstance(game_proc, game_logic.GameProcessor_), 'wrong proc'

        # players
        assert game_proc.G.p.player, 'player not inited'
        assert game_proc.G.p.player.login == 'DonaldTrump', 'wrong login'
        assert game_proc.G.p.player.is_bot == False, 'wrong bot status'
        assert game_proc.G.p.player.has_priority is None, 'wrong turn priority'
        assert game_proc.G.p.player.faction is None, 'wrong faction'
        assert game_proc.G.p.player.score == 0, 'wrong score'
        assert game_proc.G.p.player.login == 'DonaldTrump', 'wrong login'
        assert len(game_proc.G.p.player.other) == 0, 'empty player other'

        assert game_proc.G.p.bot, 'bot not inited'
        assert game_proc.G.p.bot.is_bot == True, 'wrong bot status'
        assert game_proc.G.p.bot.has_priority is None, 'wrong turn priority'
        assert game_proc.G.p.bot.faction is None, 'wrong faction'
        assert game_proc.G.p.bot.score == 0, 'wrong score'
        assert game_proc.G.p.bot.login is None, 'wrong login'
        assert len(game_proc.G.p.bot.other) == 0, 'empty bot other'

        # objectives
        assert len(game_proc.G.t.objectives.i) == 21, 'wrong objective len'
        assert game_proc.G.mission_card is None, 'wrong mission card'
        assert not game_proc.G.t.objectives.current, 'nonempty objective current'

        # groups
        assert len(game_proc.G.t.groups.i) == 24, 'wrong group len'
        assert not game_proc.G.t.groups.current, 'group current'

        # steps
        assert game_proc.G.game_turn == 0, 'wrong turn'
        assert game_proc.G.turn_phase is None, 'wrong phase'
        assert game_proc.G.is_game_end == False, 'game is end'
        assert len(game_proc.G.t.steps.i) == 6, 'wrong len'
        assert len(game_proc.G.t.steps.current) == 6, 'wrong current'
        assert not game_proc.G.t.steps.last, 'wrong last'

        # coin
        assert isinstance(game_proc.G.i.coin, bgameb.Dice), 'wrong coin'
        assert game_proc.G.i.coin.sides == 2, 'wrong sides'


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