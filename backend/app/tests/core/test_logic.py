import pytest
from typing import Tuple, Union
from collections import deque
from fastapi import HTTPException
from app.core.logic import GameLogic
from app.schemas.scheme_game_current import (
    CurrentGameDataProcessor, PlayerProcessor, OpponentProcessor
        )
from app.config import settings
from app.constructs import (
    Phases, Agents, Groups, Objectives, HiddenAgents,
    HiddenGroups, HiddenObjectives, Factions, Sides
        )


class TestGameLogic:
    """Test GameLogic class
    """

    def test_fill_game(
        self,
        game_logic: GameLogic,
            ) -> None:
        """Test game logic obkect ois inited by current data
        """
        proc = game_logic.proc

        assert isinstance(proc, CurrentGameDataProcessor), \
            'wrong return'

        assert proc.steps.turn_phase == Phases.BRIEFING.value, \
            'wrong phases'
        assert proc.steps.last_id == Phases.BRIEFING.value, \
            'wrong phases'
        assert proc.steps.turn_phases_left== Phases.get_values()[1:], \
            'wrong turn phases left'
        assert proc.steps.current_ids== Phases.get_values()[1:], \
            'wrong turn phases left'

        assert proc.players.player.login == settings.user0_login, \
            'wrong player login'

        assert len(proc.players.player.agents.c) == 6, \
            'player agents component not filled'
        assert isinstance(proc.players.player.agents.current, deque), \
            'wrong agents current'
        assert len(proc.players.player.agents.current) == 6, \
            'wrong player agents current len'
        assert proc.players.player.agents.current[0].id == Agents.SPY.value, \
            'wrong agent'

        assert proc.players.opponent.login == settings.user2_login, \
            'wrong player login'
        assert len(proc.players.opponent.agents.c) == 6, \
            'opponent agents component not filled'
        assert isinstance(proc.players.opponent.agents.current, deque), \
            'wrong agents current'
        assert len(proc.players.opponent.agents.current) == 6, \
            'wrong opponent agents current len'
        assert proc.players.opponent.agents.current[0].id == Agents.SPY.value, \
            'wrong agent'

        assert len(proc.decks.groups.c) == 24, 'groups component not filled'
        assert isinstance(proc.decks.groups.current, deque), \
            'wrong groups current'
        assert len(proc.decks.groups.current) == 24, 'wrong groups current'
        assert proc.decks.groups.current[0].id == Groups.GUERILLA.value, \
            'wrong group id'

        assert len(proc.decks.objectives.c) == 21, 'objectives component not filled'
        assert len(proc.decks.objectives.current) == 21, 'wrong objectives current'
        assert proc.decks.objectives.current[0].id == Objectives.NOBELPEACEPRIZE.value, \
            'wrong objective id'

    def test_get_api_scheme(
        self,
        game_logic: GameLogic,
            ) -> None:
        """Test game logic build api schemme
        """
        data = game_logic.get_api_scheme().dict()

        assert data['steps']['game_turn'] == 1, 'wrong game turn'
        assert data['steps']['turn_phase'] == Phases.BRIEFING.value, \
            'wrong phases'
        assert data['steps']['turn_phases_left'] == Phases.get_values()[1:], \
            'wrong turn phases left'
        assert data['steps']['is_game_ends'] is False, 'wrong end'

        assert data['players'][Sides.PLAYER.value]['login'] == settings.user0_login, \
            'wrong player login'
        assert data['players'][Sides.OPPONENT.value]['login'] == settings.user2_login, \
            'wrong opponent login'
        for side in Sides.get_values():
            assert data['players'][side]['score'] == 0, 'wrong score'
            assert data['players'][side]['faction'] is None, 'wrong faction'
            assert data['players'][side]['has_balance'] is False, 'wrong balance'
            assert data['players'][side]['has_domination'] is False, 'wrong domination'
            assert data['players'][side]['awaiting_abilities'] == [], \
               'wrong abilities'
            assert data['players'][side]['agents']['agent_x'] is None, \
                'wrong agent x'
            assert len(data['players'][side]['agents']['in_headquarter']) == 6, \
                'wrong headquarter'
            assert data['players'][side]['agents']['on_leave'] == [], \
                'wrong on_leave'
            assert data['players'][side]['agents']['terminated'] == [], \
                'wrong terminated'
        assert data['players'][Sides.PLAYER.value]['agents']['in_headquarter'][0] == Agents.SPY.value, \
                'wrong headquarter value'
        assert data['players'][Sides.OPPONENT.value]['agents']['in_headquarter'][0] == HiddenAgents.HIDDEN.value, \
                'wrong headquarter value'

        assert len(data['decks']['groups']['deck']) == 24, 'wrong groups'
        assert data['decks']['groups']['deck'][0] == HiddenGroups.HIDDEN.value, \
            'wrong groups value'
        assert data['decks']['groups']['pile'] == [], 'wrong groups pile'

        assert len(data['decks']['objectives']['deck']) == 21, 'wrong objectives'
        assert data['decks']['objectives']['deck'][0] == HiddenObjectives.HIDDEN.value, \
            'wrong objectives value'
        assert data['decks']['objectives']['pile'] == [], 'wrong objectives pile'

    def test_deal_and_shuffle_decks(
        self,
        game_logic: GameLogic,
            ) -> None:
        """Test deal_and_shuffle_decks()
        """
        proc = game_logic.deal_and_shuffle_decks().proc
        assert isinstance(proc, CurrentGameDataProcessor), \
            'wrong return'
        assert len(proc.decks.objectives.current) == 21, \
            'wrong proc objective len'
        assert len(proc.decks.groups.current) == 24, \
            'wrong proc group len'

    @pytest.mark.parametrize("test_input,expected", [
        (Factions.KGB, ('kgb', 'cia')), (Factions.CIA, ('cia', 'kgb')),
            ])
    def test_set_faction(
        self,
        test_input: Factions,
        expected: Tuple[str],
        game_logic: GameLogic,
            ) -> None:
        """Test set faction
        """
        proc = game_logic.set_faction(test_input).proc
        assert isinstance(proc, CurrentGameDataProcessor), \
            'wrong return'
        assert proc.players.player.faction == expected[0], 'wrong player proc faction'
        assert proc.players.opponent.faction == expected[1], 'wrong bot proc faction'

        with pytest.raises(HTTPException) as e:
            game_logic.set_faction(test_input)
        assert 'You cant change faction' in e.value.detail, 'wrong error'

    def test_set_next_turn_change_the_turn(
        self,
        game_logic: GameLogic,
            ) -> None:
        """Test set_next_turn() push turn
        """
        game_logic.proc.steps.last = game_logic.proc.steps.c.by_id(Phases.DETENTE)
        proc = game_logic.set_next_turn().proc
        assert proc.steps.game_turn == 2, 'wrong proc turn'
        assert proc.steps.last_id == Phases.BRIEFING.value, 'wrong last'
        assert len(proc.steps.current) == 5, 'wrong current'

    def test_set_next_turn_cant_change_if_wrong_phase(
        self,
        game_logic: GameLogic,
            ) -> None:
        """Test set_next_turn() cant change turn if wrong phase
        """
        with pytest.raises(HTTPException) as e:
            game_logic.set_next_turn()
        assert 'You can set next turn' in e.value.detail, 'wrong error'

    def test_set_next_turn_cant_change_if_game_ends(
        self,
        game_logic: GameLogic,
            ) -> None:
        """Test set_next_turn() cant change turn if game end
        """
        game_logic.proc.steps.is_game_ends = True
        game_logic.proc.steps.last = game_logic.proc.steps.c.by_id(Phases.DETENTE)

        with pytest.raises(HTTPException) as e:
            game_logic.set_next_turn()
        assert "Something can't be changed" in e.value.detail, 'wrong error'

    def test_set_next_phase_change_phase(
        self,
        game_logic: GameLogic,
            ) -> None:
        """Test set_next_phase() push phase
        """
        proc = game_logic.set_next_phase().proc
        assert isinstance(proc, CurrentGameDataProcessor), \
            'wrong return'
        assert proc.steps.last_id == Phases.PLANNING.value, \
            'wrong proc phase'
        assert len(proc.steps.current) == 4, 'wrong tep len'

        proc = game_logic.set_next_phase().proc
        assert proc.steps.last_id == Phases.INFLUENCE.value, \
            'wrong proc phase'
        assert len(proc.steps.current) == 3, 'wrong tep len'

    def test_set_next_phase_cant_change_detente(
        self,
        game_logic: GameLogic,
            ) -> None:
        """Test set_next_phase() cant change detente
        """
        game_logic.proc.steps.last = game_logic.proc.steps.c.by_id(Phases.DETENTE.value)
        proc = game_logic.set_next_phase().proc
        assert proc.steps.last_id == Phases.DETENTE.value, \
            'wrong proc phase'

    def test_set_mission_card(
        self,
        game_logic: GameLogic,
            ) -> None:
        """Test set mission card and change objective deck
        """
        proc = game_logic.set_mission_card().proc
        assert isinstance(proc, CurrentGameDataProcessor), \
            'wrong return'
        assert isinstance(proc.decks.objectives.last_id, str), 'mission not set'
        assert len(proc.decks.objectives.current) == 20, 'wrong proc current'

    def test_set_balance_at_the_turn_1(
        self,
        game_logic: GameLogic,
            ) -> None:
        """Test set turn priority at the turn 0
        """
        game_logic.proc.players.player.score = 30
        game_logic.proc.players.opponent.score = 0

        proc = game_logic.set_balance().proc
        assert isinstance(proc, CurrentGameDataProcessor), \
            'wrong return'
        assert proc.players.player.has_balance != proc.players.opponent.has_balance, \
            'wrong balance'

    @pytest.mark.parametrize("test_input,expected", [
        ((30, 0), (False, True)),
        ((0, 30), (True, False)),
        ((0, 0), (False, False)),
            ])
    def test_set_balance(
        self,
        test_input: Tuple[int],
        expected: Tuple[bool],
        game_logic: GameLogic,
            ) -> None:
        """Test set turn priority
        """
        game_logic.proc.players.player.score = test_input[0]
        game_logic.proc.players.opponent.score = test_input[1]
        game_logic.proc.steps.game_turn = 2

        proc = game_logic.set_balance().proc

        assert proc.players.player.has_balance == expected[0], \
            'wrong player priority'
        assert proc.players.opponent.has_balance == expected[1], \
            'wrong opponent priority'

    @pytest.mark.parametrize("test_input,expected", [
        (Sides.PLAYER, PlayerProcessor),
        (Sides.OPPONENT, OpponentProcessor)
            ])
    def test_get_side_proc(
        self,
        test_input: Sides,
        expected: Union[PlayerProcessor, OpponentProcessor],
        game_logic: GameLogic,
            ) -> None:
        """Test _get_side_proc() returns right process
        """
        proc = game_logic._get_side_proc(test_input)
        assert isinstance(proc, expected), 'wrong proc type'

    @pytest.mark.parametrize("test_input", [Sides.PLAYER, Sides.OPPONENT])
    def test_check_analyct_condition_raise_wrong_phase(
        self,
        test_input: Sides,
        game_logic: GameLogic,
            ) -> None:
        """Test play analyst look raise 400 when wrong phase
        """
        game_logic.proc.steps.last = game_logic.proc.steps.c.by_id(Phases.DETENTE)

        with pytest.raises(HTTPException) as e:
            game_logic._check_analyct_condition(test_input)
        assert "any phases except 'briefing'" in e.value.detail, 'wrong error'

    @pytest.mark.parametrize("test_input", [Sides.PLAYER, Sides.OPPONENT])
    def test_check_analyct_condition_raise_wrong_access(
        self,
        test_input: Sides,
        game_logic: GameLogic,
            ) -> None:
        """Test play analyst look raise 400 when player havent access
        to ability
        """
        game_logic.proc.steps.last = game_logic.proc.steps.c.by_id(Phases.BRIEFING)

        with pytest.raises(HTTPException) as e:
            game_logic._check_analyct_condition(test_input)
        assert "No access to play ability" in e.value.detail, 'wrong error'

    def test_play_analyst_for_look_the_top_of_player(
        self,
        game_logic: GameLogic,
            ) -> None:
        """Test play analyst look 3 cards of player
        """
        game_logic.proc.steps.last = game_logic.proc.steps.c.by_id(Phases.BRIEFING)
        game_logic.proc.players.player.awaiting_abilities.append(Agents.ANALYST)
        proc = game_logic.play_analyst_for_look_the_top(Sides.PLAYER).proc
        assert len([
            card for card
            in proc.decks.groups.current
            if card.is_revealed_to_player is True
                ]) == 3, 'wrong current'

        with pytest.raises(HTTPException) as e:
            game_logic.play_analyst_for_look_the_top(Sides.PLAYER)
        assert "Top 3 group cards is yet revealed" in e.value.detail, 'wrong error'

    def test_play_analyst_for_look_the_top_of_opponent(
        self,
        game_logic: GameLogic,
            ) -> None:
        """Test play analyst look 3 cards of opponent
        """
        game_logic.proc.steps.last = game_logic.proc.steps.c.by_id(Phases.BRIEFING)
        game_logic.proc.players.opponent.awaiting_abilities.append(Agents.ANALYST)
        proc = game_logic.play_analyst_for_look_the_top(Sides.OPPONENT).proc
        assert len([
            card for card
            in proc.decks.groups.current
            if card.is_revealed_to_opponent is True
                ]) == 3, 'wrong current'

        with pytest.raises(HTTPException) as e:
            game_logic.play_analyst_for_look_the_top(Sides.OPPONENT)
        assert "Top 3 group cards is yet revealed" in e.value.detail, 'wrong error'

    def test_play_analyst_for_arrange_the_top_for_player(
        self,
        game_logic: GameLogic,
            ) -> None:
        """Test play analyst for arrange the top for player
        """
        game_logic.proc.steps.last = game_logic.proc.steps.c.by_id(Phases.BRIEFING)
        game_logic.proc.players.player.awaiting_abilities.append(Agents.ANALYST)
        top = [
            game_logic.proc.decks.groups.current[-3].id,
            game_logic.proc.decks.groups.current[-2].id,
            game_logic.proc.decks.groups.current[-1].id,
                ]
        rev = top[::-1]
        assert len(game_logic.proc.decks.groups.current) == 24, 'wrong current'

        proc = game_logic.play_analyst_for_arrange_the_top(rev, Sides.PLAYER).proc
        assert proc.players.player.awaiting_abilities == [], 'wrong abilities'
        assert len(game_logic.proc.decks.groups.current) == 24, 'wrong current'
        top = [
            game_logic.proc.decks.groups.current[-3].id,
            game_logic.proc.decks.groups.current[-2].id,
            game_logic.proc.decks.groups.current[-1].id,
                ]
        assert top == rev, 'not reordered'

    def test_play_analyst_for_arrange_the_top_for_opponent(
        self,
        game_logic: GameLogic,
            ) -> None:
        """Test play analyst for arrange the top for opponent
        """
        game_logic.proc.steps.last = game_logic.proc.steps.c.by_id(Phases.BRIEFING)
        game_logic.proc.players.opponent.awaiting_abilities.append(Agents.ANALYST)
        top = [
            game_logic.proc.decks.groups.current[-3].id,
            game_logic.proc.decks.groups.current[-2].id,
            game_logic.proc.decks.groups.current[-1].id,
                ]
        rev = top[::-1]
        assert len(game_logic.proc.decks.groups.current) == 24, 'wrong current'

        proc = game_logic.play_analyst_for_arrange_the_top(rev, Sides.OPPONENT).proc
        assert proc.players.opponent.awaiting_abilities == [], 'wrong abilities'
        assert len(game_logic.proc.decks.groups.current) == 24, 'wrong current'
        top = [
            game_logic.proc.decks.groups.current[-3].id,
            game_logic.proc.decks.groups.current[-2].id,
            game_logic.proc.decks.groups.current[-1].id,
                ]
        assert top == rev, 'not reordered'

    def test_play_analyst_for_arrange_the_top_not_match(
        self,
        game_logic: GameLogic,
            ) -> None:
        """Test play analyst for arrange the top not match the top
        """
        game_logic.proc.steps.last = game_logic.proc.steps.c.by_id(Phases.BRIEFING)
        game_logic.proc.players.player.awaiting_abilities.append(Agents.ANALYST)
        old = [
            game_logic.proc.decks.groups.current[-3].id,
            game_logic.proc.decks.groups.current[-2].id,
            game_logic.proc.decks.groups.current[-1].id,
                ]
        wrong = [
            game_logic.proc.decks.groups.current[-10].id,
            game_logic.proc.decks.groups.current[-2].id,
            game_logic.proc.decks.groups.current[-1].id,
                ]
        wrong.reverse()

        with pytest.raises(HTTPException) as e:
            game_logic.play_analyst_for_arrange_the_top(wrong)
        assert "cards and top cards not match" in e.value.detail, 'wrong error'

        assert game_logic.proc.players.player.awaiting_abilities == [Agents.ANALYST], \
            'wrong abilities'
        assert len(game_logic.proc.decks.groups.current) == 24, 'wrong current'
        new = [
            game_logic.proc.decks.groups.current[-3].id,
            game_logic.proc.decks.groups.current[-2].id,
            game_logic.proc.decks.groups.current[-1].id,
                ]
        assert old == new, 'reordered'

    @pytest.mark.parametrize("test_input", [Sides.PLAYER, Sides.OPPONENT])
    def test_set_agent(
        self,
        test_input: Sides,
        game_logic: GameLogic,
            ) -> None:
        """Test set agent
        """
        game_logic.set_agent(Agents.DEPUTY, test_input)
        user = game_logic.proc.players.player if test_input == Sides.PLAYER \
            else game_logic.proc.players.opponent

        assert user.agents.by_id(Agents.DEPUTY)[0].is_agent_x == True, \
            'agent not set'
        assert user.agents.by_id(Agents.DEPUTY)[0].is_in_headquarter== False, \
            'agent is in hand'
        assert user.agents.by_id(Agents.DEPUTY)[0].is_revealed == False, \
            'wrong revealed'
        with pytest.raises(HTTPException) as e:
            game_logic.set_agent('Someher wrong', test_input)
        assert "not available to choice" in e.value.detail, 'wrong error'

    @pytest.mark.parametrize("test_input", [Sides.PLAYER, Sides.OPPONENT])
    def test_set_agent_and_reveal(
        self,
        test_input: Sides,
        game_logic: GameLogic,
            ) -> None:
        """Test get agent and reveal it
        """
        user = game_logic.proc.players.player if test_input == Sides.PLAYER else \
            game_logic.proc.players.opponent
        user.awaiting_abilities.append(Agents.DOUBLE)
        game_logic.set_agent(Agents.DEPUTY, test_input)

        assert user.agents.by_id(Agents.DEPUTY)[0].is_agent_x == True, \
            'agent not set'
        assert user.agents.by_id(Agents.DEPUTY)[0].is_in_headquarter== False, \
            'agent is in hand'
        assert user.agents.by_id(Agents.DEPUTY)[0].is_revealed == True, \
            'wrong revealed'
        assert user.awaiting_abilities == [], 'abilities not clear'


class TestCheckPhaseConditions:
    """Test chek_phase_conditions_before_next()
    """

    def test_chek_phase_conditions_before_next_if_game_end(
        self,
        game_logic: GameLogic,
            ) -> None:
        """Test chek_phase_conditions_before_next() if game end
        """
        game_logic.proc.steps.is_game_ends = True

        with pytest.raises(HTTPException)  as e:
            game_logic.chek_phase_conditions_before_next()
        assert "Something can't be changed" in e.value.detail, 'wrong error'

    def test_chek_phase_conditions_before_next_faction(
        self,
        game_logic: GameLogic,
            ) -> None:
        """Test cant next if faction not choosen
        """
        with pytest.raises(HTTPException)  as e:
            game_logic.chek_phase_conditions_before_next()
        assert "action not choosen" in e.value.detail, 'wrong error'

    def test_chek_phase_conditions_before_next_if_no_mission(
        self,
        game_logic: GameLogic,
            ) -> None:
        """Test chek_phase_conditions_before_next() if no mission card set
        """
        game_logic.proc.players.player.faction = Factions.CIA
        game_logic.proc.players.opponent.faction = Factions.KGB

        with pytest.raises(HTTPException)  as e:
            game_logic.chek_phase_conditions_before_next()
        assert "Mission card undefined" in e.value.detail, 'wrong error'

    def test_chek_phase_conditions_before_next_raise_if_no_balance(
        self,
        game_logic: GameLogic,
            ) -> None:
        """Test chek_phase_conditions_before_next() if no player has
        balance in briefing
        """
        game_logic.proc.players.player.faction = Factions.CIA
        game_logic.proc.players.opponent.faction = Factions.KGB
        game_logic.proc.decks.objectives.pop()
        with pytest.raises(HTTPException)  as e:
            game_logic.chek_phase_conditions_before_next()
        assert "No one side has balance" in e.value.detail, 'wrong error'

    @pytest.mark.parametrize("test_input", [Sides.PLAYER, Sides.OPPONENT])
    def test_chek_phase_conditions_before_next_if_analyst_not_used(
        self,
        test_input: Sides,
        game_logic: GameLogic,
            ) -> None:
        """Test chek_phase_conditions_before_next() if analyst
        ability not used
        """
        user = game_logic.proc.players.player if test_input == Sides.PLAYER else \
            game_logic.proc.players.opponent
        game_logic.proc.players.player.faction = Factions.CIA
        game_logic.proc.players.opponent.faction = Factions.KGB
        game_logic.proc.players.player.has_balance = True
        game_logic.proc.players.opponent.has_balance = False
        game_logic.proc.decks.objectives.pop()
        user.awaiting_abilities.append(Agents.ANALYST)

        with pytest.raises(HTTPException)  as e:
            game_logic.chek_phase_conditions_before_next()
        assert "Analyst ability must be used" in e.value.detail, 'wrong error'

    @pytest.mark.parametrize("test_input", [Sides.PLAYER, Sides.OPPONENT])
    def test_chek_phase_conditions_before_next_if_players_agent_not_set(
        self,
        test_input: Sides,
        game_logic: GameLogic,
            ) -> None:
        """Test chek_phase_conditions_before_next() if players
        agent not set
        """
        game_logic.proc.steps.last = game_logic.proc.steps.c.by_id(Phases.PLANNING)
        user = game_logic.proc.players.player if test_input == Sides.PLAYER else \
            game_logic.proc.players.opponent
        user.agents.current[0].is_agent_x = True

        with pytest.raises(HTTPException)  as e:
            game_logic.chek_phase_conditions_before_next()
        assert "not choosen" in e.value.detail, 'wrong error'

    def test_chek_phase_conditions_before_next_if_last_phase(
        self,
        game_logic: GameLogic,
            ) -> None:
        """Test chek_phase_conditions_before_next() if last phase
        and needed push to next tun
        """
        game_logic.proc.steps.last = game_logic.proc.steps.c.by_id(Phases.DETENTE)

        with pytest.raises(HTTPException)  as e:
            game_logic.chek_phase_conditions_before_next()
        assert "This phase is last in a turn" in e.value.detail, 'wrong error'


class TestGamePhaseConditions:
    """Test change conditions
    """

    def test_set_phase_conditions_after_next_briefing(
        self,
        game_logic: GameLogic,
            ) -> None:
        """Test set_phase_conditions_after_next() set mission card
        in briefing
        """
        game_logic.proc.steps.last = game_logic.proc.steps.c.by_id(Phases.BRIEFING)
        card = game_logic.proc.decks.groups.pop()
        card = game_logic.proc.decks.groups.pile.append(card.id)
        card = game_logic.proc.decks.groups.owned_by_player.append(card)
        card = game_logic.proc.decks.groups.owned_by_opponent.append(card)
        assert len(game_logic.proc.decks.groups.current) == 23, 'wrong groups'

        proc = game_logic.set_phase_conditions_after_next().proc

        assert isinstance(proc.decks.objectives.last_id, Objectives), 'mission not set'
        assert isinstance(proc.players.player.has_balance, bool), 'wrong priority'
        assert isinstance(proc.players.opponent.has_balance, bool), 'wrong priority'
        assert len(proc.decks.objectives.current) == 20, 'wrong gobjectives'
        assert len(proc.decks.groups.current) == 24, 'wrong groups'
        assert len(proc.decks.groups.owned_by_player) == 0, \
            'wrong owned by player groups'
        assert len(proc.decks.groups.owned_by_opponent) == 0, \
            'wrong owned by opponent groups'
        assert len(proc.decks.groups.pile) == 0, \
            'wrong groups pile'

    def test_set_phase_conditions_after_next_influence(
        self,
        game_logic: GameLogic,
            ) -> None:
        """Test set phase condition after next in influence struggle change
        returns vacated agents to hand
        """
        game_logic.proc.steps.last = game_logic.proc.steps.c.by_id(Phases.INFLUENCE)

        for user in [
            game_logic.proc.players.player,
            game_logic.proc.players.opponent
                ]:
            user.agents.by_id(Agents.SPY)[0].is_on_leave = True
            user.agents.by_id(Agents.SPY)[0].is_revealed = True
            user.agents.by_id(Agents.DEPUTY)[0].is_on_leave = True
            user.agents.by_id(Agents.DEPUTY)[0].is_revealed = False

        proc = game_logic.set_phase_conditions_after_next().proc

        for user in [
            proc.players.player,
            proc.players.opponent
                ]:
            assert user.agents.by_id(Agents.SPY)[0].is_on_leave is False, 'not changed'
            assert user.agents.by_id(Agents.SPY)[0].is_revealed is False, 'not changed'
            assert user.agents.by_id(Agents.DEPUTY)[0].is_on_leave is False, 'not changed'
            assert user.agents.by_id(Agents.DEPUTY)[0].is_revealed is False, 'changed'

    def test_set_phase_conditions_after_next_debriefing(
        self,
        game_logic: GameLogic,
            ) -> None:
        """Test set phase condition after next in debriefing
        reveal agents in play
        """
        players = game_logic.proc.players

        game_logic.proc.steps.last = game_logic.proc.steps.c.by_id(Phases.DEBRIFIENG)

        players.player.agents.by_id(Agents.SPY)[0].is_agent_x = True
        players.player.agents.by_id(Agents.SPY)[0].is_revealed = True
        players.opponent.agents.by_id(Agents.DEPUTY)[0].is_agent_x = True
        players.opponent.agents.by_id(Agents.DEPUTY)[0].is_revealed = False

        game_logic.set_phase_conditions_after_next()

        assert players.player.agents.by_id(Agents.SPY)[0].is_agent_x is True, \
            'changed'
        assert players.player.agents.by_id(Agents.SPY)[0].is_revealed is True, \
            'changed'
        assert players.opponent.agents.by_id(Agents.DEPUTY)[0].is_agent_x is True, \
            'changed'
        assert players.opponent.agents.by_id(Agents.DEPUTY)[0].is_revealed is True, \
            'not changed'

    def test_set_phase_conditions_after_next_detente(
        self,
        game_logic: GameLogic,
            ) -> None:
        """Test set phase condition after next in detente
        agents go to vacation and to hand
        """
        players = game_logic.proc.players

        game_logic.proc.steps.last = game_logic.proc.steps.c.by_id(Phases.DETENTE)
        players.player.agents.by_id(Agents.SPY)[0].is_agent_x = True
        players.player.agents.by_id(Agents.SPY)[0].is_revealed = False
        players.opponent.agents.by_id(Agents.DEPUTY)[0].is_agent_x = True
        players.opponent.agents.by_id(Agents.DEPUTY)[0].is_revealed = True

        game_logic.set_phase_conditions_after_next()

        assert players.player.agents.by_id(Agents.SPY)[0].is_agent_x is False, \
            'not changed'
        assert players.player.agents.by_id(Agents.SPY)[0].is_revealed is True, \
            'changed'
        assert players.player.agents.by_id(Agents.SPY)[0].is_on_leave is True, \
            'not changed'
        assert players.opponent.agents.by_id(Agents.DEPUTY)[0].is_agent_x is False, \
            'not changed'
        assert players.opponent.agents.by_id(Agents.DEPUTY)[0].is_revealed is False, \
            'not changed'
        assert players.opponent.agents.by_id(Agents.DEPUTY)[0].is_on_leave is False, \
            'changed'
        assert players.opponent.agents.by_id(Agents.DEPUTY)[0].is_in_headquarter is True, \
            'changed'
