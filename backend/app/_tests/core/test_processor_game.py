import pytest
import bgameb
from typing import Tuple
from fastapi import HTTPException
from app.config import settings
from app.constructs import Balance, Factions, Phases, Agents
from app.core import processor_game


class TestGameData:
    """Test game data functions
    """

    def test_make_game_data(self) -> None:
        """Test make_game_data()
        """
        data = processor_game.make_game_data(settings.user0_login)

        assert data, 'empty state'
        assert data.game_steps.game_turn == 0, 'wrong game turn'
        assert not data.game_steps.turn_phase, 'wrong turn phase'
        assert not data.game_steps.is_game_end, 'game end'

        assert data.players[0].login == settings.user0_login, 'wrong user'
        assert not data.players[0].has_priority, 'wrong priority'
        assert data.players[0].is_bot == False, 'wrong is_bot'
        assert not data.players[0].faction, 'wrong faction'
        assert data.players[0].score == 0, 'wrong score'
        assert len(data.players[0].player_cards.agent_cards.db_cards) == 6, 'hasnt cards'
        assert data.players[0].player_cards.agent_cards.dead == [], 'wrong dead'
        assert data.players[0].player_cards.agent_cards.in_play == None, 'wrong in play'
        assert data.players[0].player_cards.agent_cards.in_vacation == [], 'wrong vacation'
        assert data.players[0].player_cards.agent_cards.in_headquarter == [], 'wrong in_headquarter'
        assert data.players[0].player_cards.group_cards == [], 'hasnt cards'
        assert data.players[0].player_cards.objective_cards == [], 'hasnt cards'

        assert not data.players[1].login, 'wrong user'
        assert not data.players[1].has_priority, 'wrong priority'
        assert data.players[1].is_bot == True, 'wrong is_bot'
        assert not data.players[1].faction, 'wrong faction'
        assert data.players[1].score == 0, 'wrong score'
        assert len(data.players[1].player_cards.agent_cards.db_cards) == 6, 'hasnt cards'
        assert data.players[1].player_cards.agent_cards.dead == [], 'wrong dead'
        assert data.players[1].player_cards.agent_cards.in_play == None, 'wrong in play'
        assert data.players[1].player_cards.agent_cards.in_vacation == [], 'wrong vacation'
        assert data.players[1].player_cards.agent_cards.in_headquarter == [], 'wrong in_headquarter'
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

    def test_create_game(self, game_proc: processor_game.GameProcessor) -> None:
        """Test game is created
        """
        assert isinstance(game_proc.G, bgameb.Game), 'wrong game'
        assert isinstance(game_proc.cards, dict), 'not a cards'

    def test_check_if_current_raise_exception(
        self,
        game_proc: processor_game.GameProcessor
            ) -> None:
        """Exception is raised if player not starts any games
        """
        with pytest.raises(
            HTTPException,
            ):
            game_proc._check_if_current(None)

    def test_fill_data(
        self,
        game_proc: processor_game.GameProcessor
            ) -> None:
        """Test init new deck init deck in Game objects
        """
        game_proc = game_proc.fill()
        assert isinstance(game_proc, processor_game.GameProcessor), 'wrong proc'

        # players
        assert game_proc.G.c.player, 'player not inited'
        assert game_proc.G.c.player.login == 'DonaldTrump', 'wrong login'
        assert game_proc.G.c.player.is_bot == False, 'wrong bot status'
        assert game_proc.G.c.player.has_priority is None, 'wrong turn priority'
        assert game_proc.G.c.player.faction is None, 'wrong faction'
        assert game_proc.G.c.player.score == 0, 'wrong score'
        assert game_proc.G.c.player.login == 'DonaldTrump', 'wrong login'
        assert len(game_proc.G.c.player.c.agent_cards.c) == 6, 'wrong agents'
        assert len(game_proc.G.c.player.c.group_cards.c) == 0, 'wrong groups'
        assert len(game_proc.G.c.player.c.objective_cards.c) == 0, 'wrong objectives'
        assert len(game_proc.G.c.player.c.agent_cards.current) == 6, 'wrong agents'
        assert len(game_proc.G.c.player.c.group_cards.current) == 0, 'wrong group_cards'
        assert len(game_proc.G.c.player.c.objective_cards.current) == 0, 'wrong objectives'
        assert len(game_proc.G.c.player.abilities) == 0, 'wrong abilities'

        assert game_proc.G.c.bot, 'bot not inited'
        assert game_proc.G.c.bot.is_bot == True, 'wrong bot status'
        assert game_proc.G.c.bot.has_priority is None, 'wrong turn priority'
        assert game_proc.G.c.bot.faction is None, 'wrong faction'
        assert game_proc.G.c.bot.score == 0, 'wrong score'
        assert game_proc.G.c.bot.login is None, 'wrong login'
        assert len(game_proc.G.c.bot.c.agent_cards.c) == 6, 'wrong agent_cards'
        assert len(game_proc.G.c.bot.c.group_cards.c) == 0, 'wrong groups'
        assert len(game_proc.G.c.bot.c.objective_cards.c) == 0, 'wrong objectives'
        assert len(game_proc.G.c.bot.c.agent_cards.current) == 6, 'wrong agents'
        assert len(game_proc.G.c.bot.c.group_cards.current) == 0, 'wrong groups'
        assert len(game_proc.G.c.bot.c.objective_cards.current) == 0, 'wrong objectives'
        assert len(game_proc.G.c.bot.abilities) == 0, 'wrong abilities'

        # objectives
        assert len(game_proc.G.c.objective_deck.c) == 21, 'wrong objective len'
        assert game_proc.G.c.objective_deck.last is None, 'wrong mission card'
        assert len(game_proc.G.c.objective_deck.current) == 21, 'empty objective current'
        assert len(game_proc.G.c.objective_deck.pile) == 0, 'wrong pile'
        assert game_proc.G.c.objective_deck.c.egypt.id == 'Egypt', 'wrong card field'
        assert game_proc.G.c.objective_deck.c.egypt.name == 'Egypt', 'wrong card field'
        assert len(game_proc.G.c.objective_deck.c.egypt.bias_icons) == 4, 'wrong card field'
        assert game_proc.G.c.objective_deck.c.egypt.stability == 11, 'wrong card field'
        assert game_proc.G.c.objective_deck.c.egypt.victory_points == 20, 'wrong card field'

        # groups
        assert len(game_proc.G.c.group_deck.c) == 24, 'wrong group len'
        assert len(game_proc.G.c.group_deck.current) == 24, 'empty group current'
        assert len(game_proc.G.c.group_deck.pile) == 0, 'wrong pile'
        assert game_proc.G.c.group_deck.c.guerilla.id == 'Guerilla', 'wrong card field'
        assert game_proc.G.c.group_deck.c.guerilla.name == 'Guerilla', 'wrong card field'
        assert game_proc.G.c.group_deck.c.guerilla.faction == 'Military', 'wrong card field'
        assert game_proc.G.c.group_deck.c.guerilla.influence == 1, 'wrong card field'
        assert isinstance(game_proc.G.c.group_deck.c.guerilla.power, str), 'wrong card field'

        # steps
        assert game_proc.G.c.steps.game_turn == 0, 'wrong turn'
        assert game_proc.G.c.steps.turn_phase is None, 'wrong phase'
        assert game_proc.G.c.steps.is_game_end == False, 'game is end'
        assert len(game_proc.G.c.steps.turn_phases_left) == 6, 'wrong turn phases left'
        assert len(game_proc.G.c.steps.c) == 6, 'wrong len'
        assert len(game_proc.G.c.steps.current) == 6, 'wrong current'
        assert not game_proc.G.c.steps.last, 'wrong last'

        # coin
        assert isinstance(game_proc.G.c.coin, bgameb.Dice), 'wrong coin'
        assert game_proc.G.c.coin.sides == 2, 'wrong sides'

    def test_flush_change_player(
        self,
        inited_game_proc: processor_game.GameProcessor
            ) -> None:
        inited_game_proc.G.c.player.is_bot = True
        inited_game_proc.G.c.bot.is_bot = False
        current = inited_game_proc.flush()
        assert current.players[0].is_bot == True, 'player isnt changed'
        assert current.players[1].is_bot == False, 'bot isnt changed'

    def test_flush_steps(
        self,
        inited_game_proc: processor_game.GameProcessor
            ) -> None:
        """Test flush() can change steps
        """
        inited_game_proc.G.c.steps.pop()
        inited_game_proc.G.c.steps.game_turn += 1
        inited_game_proc.G.c.steps.is_game_end = True
        current = inited_game_proc.flush()
        assert current.game_steps.game_turn == 1, 'wrong turn'
        assert current.game_steps.turn_phase == Phases.BRIEFING.value, 'wrong phase'
        assert current.game_steps.is_game_end == True, 'game not end'
        assert len(current.game_steps.turn_phases_left) == 5, \
            'wrong phases left'

    def test_flush_agents(
        self,
        inited_game_proc: processor_game.GameProcessor,
            ) -> None:
        """Test flush() can chamge agents
        """
        card = inited_game_proc.G.c.player.c.agent_cards.current[0]
        card.is_dead = True
        card.is_in_vacation = True
        card.is_in_play = True
        card.is_revealed = True
        current = inited_game_proc.flush()
        cards = current.players[0].player_cards.agent_cards
        assert cards.dead == [card.id,], 'wrong dead'
        assert cards.in_vacation == [card.id,], 'wrong vacation'
        assert cards.in_play == card.id, 'wrong play'
        assert cards.in_headquarter == [
            card.id, '_hidden', '_hidden', '_hidden', '_hidden', '_hidden'
                ], 'wrong in_headquarter'

class TestGameProcessorLogic:
    """Test GameProcessor class
    """

    def test_deal_and_shuffle_decks(
        self,
        inited_game_proc: processor_game.GameProcessor,
            ) -> None:
        """Test deal_and_shuffle_decks()
        """
        game_proc = inited_game_proc.deal_and_shuffle_decks()
        assert isinstance(game_proc, processor_game.GameProcessor), 'wrong return'
        assert len(game_proc.G.c.objective_deck.current) == 21, 'wrong proc objective len'
        assert len(game_proc.G.c.group_deck.current) == 24, 'wrong proc group len'

    @pytest.mark.parametrize("test_input,expected", [
        (Factions.KGB, ('kgb', 'cia')), (Factions.CIA, ('cia', 'kgb')),
            ])
    def test_set_faction(
        self,
        test_input: Factions,
        expected: Tuple[str],
        inited_game_proc: processor_game.GameProcessor,
            ) -> None:
        """Test set faction
        """
        game_proc = inited_game_proc.set_faction(test_input)

        assert game_proc.G.c.player.faction == expected[0], 'wrong player proc faction'
        assert game_proc.G.c.bot.faction == expected[1], 'wrong bot proc faction'

        with pytest.raises(HTTPException):
            game_proc.set_faction(test_input)

    @pytest.mark.parametrize("test_input,expected", [
        (Balance.TRUE.value, (True, False)),
        (Balance.FALSE.value, (False, True)),
            ])
    def test_set_priority(
        self,
        test_input: Balance,
        expected: Tuple[bool],
        inited_game_proc: processor_game.GameProcessor,
            ) -> None:
        """Test set priority
        """
        game_proc = inited_game_proc.set_priority(test_input)

        assert game_proc.G.c.player.has_priority == expected[0], 'wrong player proc priority'
        assert game_proc.G.c.bot.has_priority == expected[1], 'wrong bot proc priority'

        with pytest.raises(HTTPException):
            game_proc.set_priority(test_input)

    def test_set_priority_random(
        self,
        inited_game_proc: processor_game.GameProcessor,
            ) -> None:
        """Test set priority at random
        """
        game_proc = inited_game_proc.set_priority(Balance.RANDOM.value)
        assert isinstance(game_proc.G.c.player.has_priority, bool), 'wrong player proc priority'
        assert isinstance(game_proc.G.c.bot.has_priority, bool), 'wrong bot proc priority'

    def test_set_next_turn_change_the_turn_number(
        self,
        inited_game_proc: processor_game.GameProcessor,
            ) -> None:
        """Test set_next_turn() push turn
        """
        game_proc = inited_game_proc.set_next_turn()

        assert game_proc.G.c.steps.game_turn == 1, 'wrong proc turn'
        assert game_proc.G.c.steps.last is None, 'wrong last'
        assert len(game_proc.G.c.steps.current) == 6, 'wrong current'

    def test_set_next_turn_cant_change_if_game_ends(
        self,
        inited_game_proc: processor_game.GameProcessor,
            ) -> None:
        """Test set_next_turn() cant change turn if game end
        """
        inited_game_proc.G.c.steps.is_game_end = True

        with pytest.raises(HTTPException):
            inited_game_proc.set_next_turn()

    def test_set_next_phase_change_phase(
        self,
        inited_game_proc: processor_game.GameProcessor,
            ) -> None:
        """Test set_next_phase() push phase
        """
        game_proc = inited_game_proc.set_next_phase()
        assert isinstance(game_proc, processor_game.GameProcessor), 'wrong game_proce'
        assert game_proc.G.c.steps.last.id == Phases.BRIEFING.value, \
            'wrong proc phase'
        assert len(game_proc.G.c.steps.current) == 5, 'wrong tep len'

        game_proc = inited_game_proc.set_next_phase()
        assert game_proc.G.c.steps.last.id == Phases.PLANNING.value, \
            'wrong proc phase'
        assert len(game_proc.G.c.steps.current) == 4, 'wrong tep len'

    def test_set_next_phase_cant_change_detente(
        self,
        inited_game_proc: processor_game.GameProcessor,
            ) -> None:
        """Test set_next_phase() cant change detente
        """
        inited_game_proc.G.c.steps.last = inited_game_proc.G.c.steps.c.by_id(Phases.DETENTE.value)

        game_proc = inited_game_proc.set_next_phase()
        assert game_proc.G.c.steps.last.id == 'detente', \
            'phase changed if game end'
        assert len(game_proc.G.c.steps.current) == 6, 'wrong tep len'

    def test_check_analyct_condition_raise_wrong_phase(
        self,
        inited_game_proc: processor_game.GameProcessor,
            ) -> None:
        """Test play analyst look raise 400 when wrong phase
        """
        inited_game_proc.G.c.steps.last = inited_game_proc.G.c.steps.c.by_id(Phases.DETENTE.value)

        with pytest.raises(HTTPException):
            inited_game_proc._check_analyct_condition()

    def test_check_analyct_condition_raise_wrong_access(
        self,
        inited_game_proc: processor_game.GameProcessor,
            ) -> None:
        """Test play analyst look raise 400 when player havent access
        to ability
        """
        inited_game_proc.G.c.steps.last = inited_game_proc.G.c.steps.c.by_id(Phases.BRIEFING.value)

        with pytest.raises(HTTPException):
            inited_game_proc._check_analyct_condition()

    def test_play_analyst_for_look_the_top(
        self,
        started_game_proc: processor_game.GameProcessor,
            ) -> None:
        """Test play analyst look 3 cards
        """
        started_game_proc.G.c.steps.last = started_game_proc.G.c.steps.c.by_id(Phases.BRIEFING.value)
        started_game_proc.G.c.player.abilities.append(Agents.ANALYST.value)
        game_proc = started_game_proc.play_analyst_for_look_the_top()
        assert len(game_proc.G.c.player.c.group_cards.current) == 3, 'wrong current'
        assert game_proc.G.c.player.c.group_cards.current[0].pos_in_deck == -3, \
            'wrong position'
        old = game_proc.G.c.player.c.group_cards.current[-1].id
        assert game_proc.G.c.group_deck.current[-1].id == old, 'wrong order'

        with pytest.raises(HTTPException):
            game_proc.play_analyst_for_look_the_top()

    def test_play_analyst_for_look_the_top_removes_old_revealed(
        self,
        started_game_proc: processor_game.GameProcessor,
            ) -> None:
        """Test play analyst look 3 cards and removes old revealed
        """
        started_game_proc.G.c.steps.last = started_game_proc.G.c.steps.c.by_id(Phases.BRIEFING.value)
        started_game_proc.G.c.player.abilities.append(Agents.ANALYST.value)
        started_game_proc.G.c.player.c.group_cards.current.append(
            started_game_proc.G.c.group_deck.current[-1]
                )
        started_game_proc.G.c.player.c.group_cards.current[-1].pos_in_deck = -10

        game_proc = started_game_proc.play_analyst_for_look_the_top()
        assert len(game_proc.G.c.player.c.group_cards.current) == 3, 'wrong current'
        assert game_proc.G.c.player.c.group_cards.current[0].pos_in_deck == -3, \
            'wrong position'

    def test_play_analyst_for_arrange_the_top(
        self,
        started_game_proc: processor_game.GameProcessor,
            ) -> None:
        """Test play analyst for arrange the top
        """
        started_game_proc.G.c.steps.last = started_game_proc.G.c.steps.c.by_id(Phases.BRIEFING.value)
        started_game_proc.G.c.player.abilities.append(Agents.ANALYST.value)
        top = [
            started_game_proc.G.c.group_deck.current[-3].id,
            started_game_proc.G.c.group_deck.current[-2].id,
            started_game_proc.G.c.group_deck.current[-1].id,
                ]
        rev = top[::-1]
        assert len(started_game_proc.G.c.group_deck.current) == 24, 'wrong current'

        game_proc = started_game_proc.play_analyst_for_arrange_the_top(rev)
        assert game_proc.G.c.player.abilities == [], 'wrong abilities'
        assert len(game_proc.G.c.group_deck.current) == 24, 'wrong current'
        top = [
            game_proc.G.c.group_deck.current[-3].id,
            game_proc.G.c.group_deck.current[-2].id,
            game_proc.G.c.group_deck.current[-1].id,
                ]
        assert top == rev, 'not reordered'

    def test_play_analyst_for_arrange_the_top_not_match(
        self,
        started_game_proc: processor_game.GameProcessor,
            ) -> None:
        """Test play analyst for arrange the top not match the top
        """
        started_game_proc.G.c.steps.last = started_game_proc.G.c.steps.c.by_id(Phases.BRIEFING.value)
        started_game_proc.G.c.player.abilities.append(Agents.ANALYST.value)
        old = [
            started_game_proc.G.c.group_deck.current[-3].id,
            started_game_proc.G.c.group_deck.current[-2].id,
            started_game_proc.G.c.group_deck.current[-1].id,
                ]
        wrong = [
            started_game_proc.G.c.group_deck.current[-10].id,
            started_game_proc.G.c.group_deck.current[-2].id,
            started_game_proc.G.c.group_deck.current[-1].id,
                ]
        wrong.reverse()

        with pytest.raises(HTTPException):
            started_game_proc.play_analyst_for_arrange_the_top(wrong)

        assert started_game_proc.G.c.player.abilities == [Agents.ANALYST.value], 'wrong abilities'
        assert len(started_game_proc.G.c.group_deck.current) == 24, 'wrong current'
        new = [
            started_game_proc.G.c.group_deck.current[-3].id,
            started_game_proc.G.c.group_deck.current[-2].id,
            started_game_proc.G.c.group_deck.current[-1].id,
                ]
        assert old == new, 'reordered'

    @pytest.mark.parametrize("test_input", ['player', 'bot', ])
    def test_set_agent(
        self,
        started_game_proc: processor_game.GameProcessor,
        test_input: str,
            ) -> None:
        """Test set agent
        """
        game_proc = started_game_proc.set_agent(
            player=test_input, agent_id=Agents.DEPUTY.value
                )
        assert game_proc.G.c[test_input].c.agent_cards.by_id(Agents.DEPUTY.value).is_in_play == True, \
            'agent not set'
        assert game_proc.G.c[test_input].c.agent_cards.by_id(Agents.DEPUTY.value).is_in_headquarter== False, \
            'agent is in hand'
        assert game_proc.G.c[test_input].c.agent_cards.by_id(Agents.DEPUTY.value).is_revealed == False, \
            'wrong revealed'
        with pytest.raises(HTTPException):
            game_proc = started_game_proc.set_agent(
                player=test_input, agent_id='Someher wrong'
                    )

    @pytest.mark.parametrize("test_input", ['player', 'bot', ])
    def test_set_agent_and_reveal(
        self,
        started_game_proc: processor_game.GameProcessor,
        test_input: str,
            ) -> None:
        started_game_proc.G.c[test_input].abilities.append(Agents.DOUBLE.value)
        game_proc = started_game_proc.set_agent(
            player=test_input, agent_id=Agents.DEPUTY.value
                )
        assert game_proc.G.c[test_input].c.agent_cards.by_id(Agents.DEPUTY.value).is_in_play == True, \
            'agent not set'
        assert game_proc.G.c[test_input].c.agent_cards.by_id(Agents.DEPUTY.value).is_revealed == True, \
            'wrong revealed'
        assert game_proc.G.c[test_input].c.agent_cards.by_id(Agents.DEPUTY.value).is_in_headquarter== False, \
            'agent is in hand'
        assert game_proc.G.c.player.abilities == [], 'abilities not clear'


class TestCheckPhaseConditions:
    """Test chek_phase_conditions_before_next()
    """

    def test_chek_phase_conditions_before_next_if_game_end(
        self,
        inited_game_proc: processor_game.GameProcessor,
            ) -> None:
        """Test chek_phase_conditions_before_next() if game end
        """
        inited_game_proc.G.c.steps.is_game_end = True

        with pytest.raises(
            HTTPException,
            ):
            inited_game_proc.chek_phase_conditions_before_next()

    def test_chek_phase_conditions_before_next_raise_if_no_priority(
        self,
        inited_game_proc: processor_game.GameProcessor,
            ) -> None:
        """Test chek_phase_conditions_before_next() if no player has
        priority in briefing
        """
        inited_game_proc.G.c.steps.last = inited_game_proc.G.c.steps.c.by_id(Phases.BRIEFING.value)

        with pytest.raises(
            HTTPException,
            ):
            inited_game_proc.chek_phase_conditions_before_next()

    def test_chek_phase_conditions_before_next_if_no_mission(
        self,
        inited_game_proc: processor_game.GameProcessor,
            ) -> None:
        """Test chek_phase_conditions_before_next() if no mission card set
        """
        inited_game_proc.G.c.steps.last = inited_game_proc.G.c.steps.c.by_id(Phases.BRIEFING.value)
        inited_game_proc.G.c.objective_deck.last = 'some mission card'

        with pytest.raises(
            HTTPException,
                ):
            inited_game_proc.chek_phase_conditions_before_next()

    def test_chek_phase_conditions_before_next_if_analyst_not_used(
        self,
        inited_game_proc: processor_game.GameProcessor,
            ) -> None:
        """Test chek_phase_conditions_before_next() if analyst
        bility not used
        """
        inited_game_proc.G.c.steps.last = inited_game_proc.G.c.steps.c.by_id(Phases.BRIEFING.value)
        inited_game_proc.G.c.player.abilities.append(Agents.ANALYST.value)
        inited_game_proc.G.c.player.has_priority = True
        inited_game_proc.G.c.bot.has_priority = False
        inited_game_proc.G.c.objective_deck.last = 'some mission card'

        with pytest.raises(
            HTTPException,
                ):
            inited_game_proc.chek_phase_conditions_before_next()

    @pytest.mark.parametrize("test_input", ['player', 'bot', ])
    def test_chek_phase_conditions_before_next_if_players_agent_not_set(
        self,
        inited_game_proc: processor_game.GameProcessor,
        test_input: str,
            ) -> None:
        """Test chek_phase_conditions_before_next() if players
        agent not set
        """
        inited_game_proc.G.c.steps.last = inited_game_proc.G.c.steps.c.by_id(Phases.BRIEFING.value)
        with pytest.raises(
            HTTPException,
                ):
            inited_game_proc.chek_phase_conditions_before_next()
        inited_game_proc.G.c[test_input].c.agent_cards.by_id(Agents.DEPUTY.value).is_in_play = True
        with pytest.raises(
            HTTPException,
                ):
            inited_game_proc.chek_phase_conditions_before_next()

    def test_chek_phase_conditions_before_next_if_last_phase(
        self,
        inited_game_proc: processor_game.GameProcessor,
            ) -> None:
        """Test chek_phase_conditions_before_next() if last phase
        and needed push to next tun
        """
        inited_game_proc.G.c.steps.last = inited_game_proc.G.c.steps.c.by_id(Phases.DETENTE.value)

        with pytest.raises(
            HTTPException,
                ):
            inited_game_proc.chek_phase_conditions_before_next()


class TestGamePhaseConditions:
    """Test change conditions
    """

    def test_set_mission_card(
        self,
        started_game_proc: processor_game.GameProcessor,
            ) -> None:
        """Test set mission card and change objective deck
        """
        game_proc = started_game_proc.set_mission_card()

        assert isinstance(game_proc, processor_game.GameProcessor), 'wrong game_proce'
        assert isinstance(game_proc.G.c.objective_deck.last.id, str), 'mission not set'
        assert len(game_proc.G.c.objective_deck.current) == 20, 'wrong proc current'

    def test_set_turn_priority_at_the_turn_0(
        self,
        started_game_proc: processor_game.GameProcessor,
            ) -> None:
        """Test set turn priority at the turn 0
        """
        started_game_proc.G.c.player.score = 30
        started_game_proc.G.c.bot.score = 0

        game_proc = started_game_proc.set_turn_priority()

        assert isinstance(game_proc, processor_game.GameProcessor), 'wrong game_proce'
        assert isinstance(game_proc.G.c.player.has_priority, bool), 'wrong priority'
        assert isinstance(game_proc.G.c.bot.has_priority, bool), 'wrong priority'

    @pytest.mark.parametrize("test_input,expected", [
        ((30, 0), (False, True)),
        ((0, 30), (True, False)),
        ((0, 0), (None, None)),
            ])
    def test_set_turn_priority(
        self,
        test_input: Tuple[int],
        expected: Tuple[bool],
        started_game_proc: processor_game.GameProcessor,
            ) -> None:
        """Test set turn priority
        """
        started_game_proc.G.c.player.score = test_input[0]
        started_game_proc.G.c.bot.score = test_input[1]
        started_game_proc.G.c.steps.game_turn = 1

        game_proc = started_game_proc.set_turn_priority()

        assert game_proc.G.c.player.has_priority == expected[0], 'wrong priority'
        assert game_proc.G.c.bot.has_priority == expected[1], 'wrong priority'

    def test_set_phase_conditions_after_next_briefing(
        self,
        started_game_proc: processor_game.GameProcessor,
            ) -> None:
        """Test set_phase_conditions_after_next() set mission card
        in briefing
        """
        started_game_proc.G.c.steps.last = started_game_proc.G.c.steps.c.by_id(Phases.BRIEFING.value)
        card = started_game_proc.G.c.group_deck.pop()
        started_game_proc.G.c.group_deck.pile.append(card.id)
        started_game_proc.G.c.player.c.group_cards.append(card)
        started_game_proc.G.c.bot.c.group_cards.append(card)
        assert len(started_game_proc.G.c.group_deck.current) == 23, 'wrong groups'
        assert len(started_game_proc.G.c.player.c.group_cards.current) == 1, \
            'wrong revealed for player'
        assert len(started_game_proc.G.c.bot.c.group_cards.current) == 1, \
            'wrong revealed for bot'
        assert len(started_game_proc.G.c.group_deck.pile) == 1, \
            'wrong pile'

        game_proc = started_game_proc.set_phase_conditions_after_next()

        assert isinstance(game_proc.G.c.objective_deck.last.id, str), 'mission not set'
        assert isinstance(game_proc.G.c.player.has_priority, bool), 'wrong priority'
        assert isinstance(game_proc.G.c.bot.has_priority, bool), 'wrong priority'
        assert len(started_game_proc.G.c.group_deck.current) == 24, 'wrong groups'
        assert len(started_game_proc.G.c.player.c.group_cards.current) == 0, \
            'wrong revealed for player'
        assert len(started_game_proc.G.c.bot.c.group_cards.current) == 0, \
            'wrong revealed for bot'
        assert len(started_game_proc.G.c.group_deck.pile) == 0, \
            'wrong pile'

    @pytest.mark.parametrize("test_input", ['player', 'bot', ])
    def test_set_phase_conditions_after_next_influence(
        self,
        started_game_proc: processor_game.GameProcessor,
        test_input: str,
            ) -> None:
        """Test set phase condition after next in influence struggle change
        returns vacated agents to hand
        """
        started_game_proc.G.c.steps.last = started_game_proc.G.c.steps.c.by_id(Phases.INFLUENCE.value)
        cards = started_game_proc.G.c[test_input].c.agent_cards
        cards.by_id(Agents.SPY.value).is_in_vacation = True
        cards.by_id(Agents.SPY.value).is_revealed = True
        cards.by_id(Agents.DIRECTOR.value).is_in_vacation = True
        cards.by_id(Agents.DIRECTOR.value).is_revealed = False

        game_proc = started_game_proc.set_phase_conditions_after_next()
        cards = game_proc.G.c[test_input].c.agent_cards

        assert cards.by_id(Agents.SPY.value).is_in_vacation is False, 'not changed'
        assert cards.by_id(Agents.SPY.value).is_revealed is False, 'not changed'
        assert cards.by_id(Agents.DIRECTOR.value).is_in_vacation is False, 'not changed'
        assert cards.by_id(Agents.DIRECTOR.value).is_revealed is False, 'changed'

    @pytest.mark.parametrize("test_input", ['player', 'bot', ])
    def test_set_phase_conditions_after_next_debriefing(
        self,
        started_game_proc: processor_game.GameProcessor,
        test_input: str,
            ) -> None:
        """Test set phase condition after next in debriefing
        reveal agents in play
        """
        started_game_proc.G.c.steps.last = started_game_proc.G.c.steps.c.by_id(Phases.DEBRIFIENG.value)
        cards = started_game_proc.G.c[test_input].c.agent_cards
        cards.by_id(Agents.SPY.value).is_in_play = True
        cards.by_id(Agents.SPY.value).is_revealed = True
        cards.by_id(Agents.DIRECTOR.value).is_in_play = True
        cards.by_id(Agents.DIRECTOR.value).is_revealed = False

        game_proc = started_game_proc.set_phase_conditions_after_next()
        cards = game_proc.G.c[test_input].c.agent_cards

        assert cards.by_id(Agents.SPY.value).is_in_play is True, 'changed'
        assert cards.by_id(Agents.SPY.value).is_revealed is True, 'changed'
        assert cards.by_id(Agents.DIRECTOR.value).is_in_play is True, 'changed'
        assert cards.by_id(Agents.DIRECTOR.value).is_revealed is True, 'not changed'

    @pytest.mark.parametrize("test_input", ['player', 'bot', ])
    def test_set_phase_conditions_after_next_detente(
        self,
        started_game_proc: processor_game.GameProcessor,
        test_input: str,
            ) -> None:
        """Test set phase condition after next in detente
        agents go to vacation and to hand
        """
        started_game_proc.G.c.steps.last = started_game_proc.G.c.steps.c.by_id(Phases.DETENTE.value)
        cards = started_game_proc.G.c[test_input].c.agent_cards
        cards.by_id(Agents.SPY.value).is_in_play = True
        cards.by_id(Agents.SPY.value).is_revealed = True
        cards.by_id(Agents.DEPUTY.value).is_in_play = True
        cards.by_id(Agents.DEPUTY.value).is_revealed = True

        game_proc = started_game_proc.set_phase_conditions_after_next()
        cards = game_proc.G.c[test_input].c.agent_cards

        assert cards.by_id(Agents.SPY.value).is_in_play is False, 'not changed'
        assert cards.by_id(Agents.SPY.value).is_revealed is True, 'changed'
        assert cards.by_id(Agents.SPY.value).is_in_vacation is True, 'not changed'
        assert cards.by_id(Agents.DEPUTY.value).is_in_play is False, 'not changed'
        assert cards.by_id(Agents.DEPUTY.value).is_revealed is False, 'not changed'
        assert cards.by_id(Agents.DEPUTY.value).is_in_vacation is False, 'changed'

