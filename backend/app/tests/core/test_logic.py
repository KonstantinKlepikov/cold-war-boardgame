import pytest
from typing import Tuple
from collections import deque
from fastapi import HTTPException
from app.core.logic import GameLogic
from app.schemas.scheme_game_current import CurrentGameDataProcessor
from app.config import settings
from app.constructs import (
    Phases, Agents, Groups, Objectives, HiddenAgents,
    HiddenGroups, HiddenObjectives, Factions, Balance
        )


class TestGameLofic:
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
        assert data['steps']['is_game_starts'] is False, 'wrong start'

        assert data['players']['player']['login'] == settings.user0_login, \
            'wrong player login'
        assert data['players']['opponent']['login'] == settings.user2_login, \
            'wrong opponent login'
        for player in ['player', 'opponent']:
            assert data['players'][player]['score'] == 0, 'wrong score'
            assert data['players'][player]['faction'] is None, 'wrong faction'
            assert data['players'][player]['has_balance'] is False, 'wrong balance'
            assert data['players'][player]['has_domination'] is False, 'wrong domination'
            assert data['players'][player]['awaiting_abilities'] == [], \
               'wrong abilities'
            assert data['players'][player]['agents']['agent_x'] is None, \
                'wrong agent x'
            assert len(data['players'][player]['agents']['in_headquarter']) == 6, \
                'wrong headquarter'
            assert data['players'][player]['agents']['on_leave'] == [], \
                'wrong on_leave'
            assert data['players'][player]['agents']['terminated'] == [], \
                'wrong terminated'
        assert data['players']['player']['agents']['in_headquarter'][0] == Agents.SPY.value, \
                'wrong headquarter value'
        assert data['players']['opponent']['agents']['in_headquarter'][0] == HiddenAgents.HIDDEN.value, \
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

        with pytest.raises(HTTPException):
            game_logic.set_faction(test_input)

    @pytest.mark.parametrize("test_input,expected", [
        (Balance.TRUE.value, (True, False)),
        (Balance.FALSE.value, (False, True)),
            ])
    def test_set_balance(
        self,
        test_input: Balance,
        expected: Tuple[bool],
        game_logic: GameLogic,
            ) -> None:
        """Test set balance
        """
        proc = game_logic.set_balance(test_input).proc
        assert isinstance(proc, CurrentGameDataProcessor), \
            'wrong return'
        assert proc.players.player.has_balance == expected[0], 'wrong player proc priority'
        assert proc.players.opponent.has_balance == expected[1], 'wrong bot proc priority'

        with pytest.raises(HTTPException):
            game_logic.set_balance(test_input)

    def test_set_balance_random(
        self,
        game_logic: GameLogic,
            ) -> None:
        """Test set balaance at random
        """
        proc = game_logic.set_balance(Balance.RANDOM.value).proc
        assert proc.players.player.has_balance != proc.players.opponent.has_balance, \
            'wrong random balance'

    def test_set_next_turn_change_the_turn(
        self,
        game_logic: GameLogic,
            ) -> None:
        """Test set_next_turn() push turn
        """
        proc = game_logic.set_next_turn().proc

        assert proc.steps.game_turn == 2, 'wrong proc turn'
        assert proc.steps.last_id == Phases.BRIEFING.value, 'wrong last'
        assert len(proc.steps.current) == 5, 'wrong current'

    def test_set_next_turn_cant_change_if_game_ends(
        self,
        game_logic: GameLogic,
            ) -> None:
        """Test set_next_turn() cant change turn if game end
        """
        game_logic.proc.steps.is_game_ends = True

        with pytest.raises(HTTPException):
            game_logic.set_next_turn()

#     def test_set_next_phase_change_phase(
#         self,
#         inited_game_proc: processor_game.GameProcessor,
#             ) -> None:
#         """Test set_next_phase() push phase
#         """
#         game_proc = inited_game_proc.set_next_phase()
#         assert isinstance(game_proc, processor_game.GameProcessor), 'wrong game_proce'
#         assert game_proc.G.c.steps.last.id == Phases.BRIEFING.value, \
#             'wrong proc phase'
#         assert len(game_proc.G.c.steps.current) == 5, 'wrong tep len'

#         game_proc = inited_game_proc.set_next_phase()
#         assert game_proc.G.c.steps.last.id == Phases.PLANNING.value, \
#             'wrong proc phase'
#         assert len(game_proc.G.c.steps.current) == 4, 'wrong tep len'

#     def test_set_next_phase_cant_change_detente(
#         self,
#         inited_game_proc: processor_game.GameProcessor,
#             ) -> None:
#         """Test set_next_phase() cant change detente
#         """
#         inited_game_proc.G.c.steps.last = inited_game_proc.G.c.steps.c.by_id(Phases.DETENTE.value)

#         game_proc = inited_game_proc.set_next_phase()
#         assert game_proc.G.c.steps.last.id == 'detente', \
#             'phase changed if game end'
#         assert len(game_proc.G.c.steps.current) == 6, 'wrong tep len'

#     def test_check_analyct_condition_raise_wrong_phase(
#         self,
#         inited_game_proc: processor_game.GameProcessor,
#             ) -> None:
#         """Test play analyst look raise 400 when wrong phase
#         """
#         inited_game_proc.G.c.steps.last = inited_game_proc.G.c.steps.c.by_id(Phases.DETENTE.value)

#         with pytest.raises(HTTPException):
#             inited_game_proc._check_analyct_condition()

#     def test_check_analyct_condition_raise_wrong_access(
#         self,
#         inited_game_proc: processor_game.GameProcessor,
#             ) -> None:
#         """Test play analyst look raise 400 when player havent access
#         to ability
#         """
#         inited_game_proc.G.c.steps.last = inited_game_proc.G.c.steps.c.by_id(Phases.BRIEFING.value)

#         with pytest.raises(HTTPException):
#             inited_game_proc._check_analyct_condition()

#     def test_play_analyst_for_look_the_top(
#         self,
#         started_game_proc: processor_game.GameProcessor,
#             ) -> None:
#         """Test play analyst look 3 cards
#         """
#         started_game_proc.G.c.steps.last = started_game_proc.G.c.steps.c.by_id(Phases.BRIEFING.value)
#         started_game_proc.G.c.player.abilities.append(Agents.ANALYST.value)
#         game_proc = started_game_proc.play_analyst_for_look_the_top()
#         assert len(game_proc.G.c.player.c.group_cards.current) == 3, 'wrong current'
#         assert game_proc.G.c.player.c.group_cards.current[0].pos_in_deck == -3, \
#             'wrong position'
#         old = game_proc.G.c.player.c.group_cards.current[-1].id
#         assert game_proc.G.c.group_deck.current[-1].id == old, 'wrong order'

#         with pytest.raises(HTTPException):
#             game_proc.play_analyst_for_look_the_top()

#     def test_play_analyst_for_look_the_top_removes_old_revealed(
#         self,
#         started_game_proc: processor_game.GameProcessor,
#             ) -> None:
#         """Test play analyst look 3 cards and removes old revealed
#         """
#         started_game_proc.G.c.steps.last = started_game_proc.G.c.steps.c.by_id(Phases.BRIEFING.value)
#         started_game_proc.G.c.player.abilities.append(Agents.ANALYST.value)
#         started_game_proc.G.c.player.c.group_cards.current.append(
#             started_game_proc.G.c.group_deck.current[-1]
#                 )
#         started_game_proc.G.c.player.c.group_cards.current[-1].pos_in_deck = -10

#         game_proc = started_game_proc.play_analyst_for_look_the_top()
#         assert len(game_proc.G.c.player.c.group_cards.current) == 3, 'wrong current'
#         assert game_proc.G.c.player.c.group_cards.current[0].pos_in_deck == -3, \
#             'wrong position'

#     def test_play_analyst_for_arrange_the_top(
#         self,
#         started_game_proc: processor_game.GameProcessor,
#             ) -> None:
#         """Test play analyst for arrange the top
#         """
#         started_game_proc.G.c.steps.last = started_game_proc.G.c.steps.c.by_id(Phases.BRIEFING.value)
#         started_game_proc.G.c.player.abilities.append(Agents.ANALYST.value)
#         top = [
#             started_game_proc.G.c.group_deck.current[-3].id,
#             started_game_proc.G.c.group_deck.current[-2].id,
#             started_game_proc.G.c.group_deck.current[-1].id,
#                 ]
#         rev = top[::-1]
#         assert len(started_game_proc.G.c.group_deck.current) == 24, 'wrong current'

#         game_proc = started_game_proc.play_analyst_for_arrange_the_top(rev)
#         assert game_proc.G.c.player.abilities == [], 'wrong abilities'
#         assert len(game_proc.G.c.group_deck.current) == 24, 'wrong current'
#         top = [
#             game_proc.G.c.group_deck.current[-3].id,
#             game_proc.G.c.group_deck.current[-2].id,
#             game_proc.G.c.group_deck.current[-1].id,
#                 ]
#         assert top == rev, 'not reordered'

#     def test_play_analyst_for_arrange_the_top_not_match(
#         self,
#         started_game_proc: processor_game.GameProcessor,
#             ) -> None:
#         """Test play analyst for arrange the top not match the top
#         """
#         started_game_proc.G.c.steps.last = started_game_proc.G.c.steps.c.by_id(Phases.BRIEFING.value)
#         started_game_proc.G.c.player.abilities.append(Agents.ANALYST.value)
#         old = [
#             started_game_proc.G.c.group_deck.current[-3].id,
#             started_game_proc.G.c.group_deck.current[-2].id,
#             started_game_proc.G.c.group_deck.current[-1].id,
#                 ]
#         wrong = [
#             started_game_proc.G.c.group_deck.current[-10].id,
#             started_game_proc.G.c.group_deck.current[-2].id,
#             started_game_proc.G.c.group_deck.current[-1].id,
#                 ]
#         wrong.reverse()

#         with pytest.raises(HTTPException):
#             started_game_proc.play_analyst_for_arrange_the_top(wrong)

#         assert started_game_proc.G.c.player.abilities == [Agents.ANALYST.value], 'wrong abilities'
#         assert len(started_game_proc.G.c.group_deck.current) == 24, 'wrong current'
#         new = [
#             started_game_proc.G.c.group_deck.current[-3].id,
#             started_game_proc.G.c.group_deck.current[-2].id,
#             started_game_proc.G.c.group_deck.current[-1].id,
#                 ]
#         assert old == new, 'reordered'

#     @pytest.mark.parametrize("test_input", ['player', 'bot', ])
#     def test_set_agent(
#         self,
#         started_game_proc: processor_game.GameProcessor,
#         test_input: str,
#             ) -> None:
#         """Test set agent
#         """
#         game_proc = started_game_proc.set_agent(
#             player=test_input, agent_id=Agents.DEPUTY.value
#                 )
#         assert game_proc.G.c[test_input].c.agent_cards.by_id(Agents.DEPUTY.value).is_in_play == True, \
#             'agent not set'
#         assert game_proc.G.c[test_input].c.agent_cards.by_id(Agents.DEPUTY.value).is_in_headquarter== False, \
#             'agent is in hand'
#         assert game_proc.G.c[test_input].c.agent_cards.by_id(Agents.DEPUTY.value).is_revealed == False, \
#             'wrong revealed'
#         with pytest.raises(HTTPException):
#             game_proc = started_game_proc.set_agent(
#                 player=test_input, agent_id='Someher wrong'
#                     )

#     @pytest.mark.parametrize("test_input", ['player', 'bot', ])
#     def test_set_agent_and_reveal(
#         self,
#         started_game_proc: processor_game.GameProcessor,
#         test_input: str,
#             ) -> None:
#         started_game_proc.G.c[test_input].abilities.append(Agents.DOUBLE.value)
#         game_proc = started_game_proc.set_agent(
#             player=test_input, agent_id=Agents.DEPUTY.value
#                 )
#         assert game_proc.G.c[test_input].c.agent_cards.by_id(Agents.DEPUTY.value).is_in_play == True, \
#             'agent not set'
#         assert game_proc.G.c[test_input].c.agent_cards.by_id(Agents.DEPUTY.value).is_revealed == True, \
#             'wrong revealed'
#         assert game_proc.G.c[test_input].c.agent_cards.by_id(Agents.DEPUTY.value).is_in_headquarter== False, \
#             'agent is in hand'
#         assert game_proc.G.c.player.abilities == [], 'abilities not clear'


# class TestCheckPhaseConditions:
#     """Test chek_phase_conditions_before_next()
#     """

#     def test_chek_phase_conditions_before_next_if_game_end(
#         self,
#         inited_game_proc: processor_game.GameProcessor,
#             ) -> None:
#         """Test chek_phase_conditions_before_next() if game end
#         """
#         inited_game_proc.G.c.steps.is_game_end = True

#         with pytest.raises(
#             HTTPException,
#             ):
#             inited_game_proc.chek_phase_conditions_before_next()

#     def test_chek_phase_conditions_before_next_raise_if_no_priority(
#         self,
#         inited_game_proc: processor_game.GameProcessor,
#             ) -> None:
#         """Test chek_phase_conditions_before_next() if no player has
#         priority in briefing
#         """
#         inited_game_proc.G.c.steps.last = inited_game_proc.G.c.steps.c.by_id(Phases.BRIEFING.value)

#         with pytest.raises(
#             HTTPException,
#             ):
#             inited_game_proc.chek_phase_conditions_before_next()

#     def test_chek_phase_conditions_before_next_if_no_mission(
#         self,
#         inited_game_proc: processor_game.GameProcessor,
#             ) -> None:
#         """Test chek_phase_conditions_before_next() if no mission card set
#         """
#         inited_game_proc.G.c.steps.last = inited_game_proc.G.c.steps.c.by_id(Phases.BRIEFING.value)
#         inited_game_proc.G.c.objective_deck.last = 'some mission card'

#         with pytest.raises(
#             HTTPException,
#                 ):
#             inited_game_proc.chek_phase_conditions_before_next()

#     def test_chek_phase_conditions_before_next_if_analyst_not_used(
#         self,
#         inited_game_proc: processor_game.GameProcessor,
#             ) -> None:
#         """Test chek_phase_conditions_before_next() if analyst
#         bility not used
#         """
#         inited_game_proc.G.c.steps.last = inited_game_proc.G.c.steps.c.by_id(Phases.BRIEFING.value)
#         inited_game_proc.G.c.player.abilities.append(Agents.ANALYST.value)
#         inited_game_proc.G.c.player.has_priority = True
#         inited_game_proc.G.c.bot.has_priority = False
#         inited_game_proc.G.c.objective_deck.last = 'some mission card'

#         with pytest.raises(
#             HTTPException,
#                 ):
#             inited_game_proc.chek_phase_conditions_before_next()

#     @pytest.mark.parametrize("test_input", ['player', 'bot', ])
#     def test_chek_phase_conditions_before_next_if_players_agent_not_set(
#         self,
#         inited_game_proc: processor_game.GameProcessor,
#         test_input: str,
#             ) -> None:
#         """Test chek_phase_conditions_before_next() if players
#         agent not set
#         """
#         inited_game_proc.G.c.steps.last = inited_game_proc.G.c.steps.c.by_id(Phases.BRIEFING.value)
#         with pytest.raises(
#             HTTPException,
#                 ):
#             inited_game_proc.chek_phase_conditions_before_next()
#         inited_game_proc.G.c[test_input].c.agent_cards.by_id(Agents.DEPUTY.value).is_in_play = True
#         with pytest.raises(
#             HTTPException,
#                 ):
#             inited_game_proc.chek_phase_conditions_before_next()

#     def test_chek_phase_conditions_before_next_if_last_phase(
#         self,
#         inited_game_proc: processor_game.GameProcessor,
#             ) -> None:
#         """Test chek_phase_conditions_before_next() if last phase
#         and needed push to next tun
#         """
#         inited_game_proc.G.c.steps.last = inited_game_proc.G.c.steps.c.by_id(Phases.DETENTE.value)

#         with pytest.raises(
#             HTTPException,
#                 ):
#             inited_game_proc.chek_phase_conditions_before_next()


# class TestGamePhaseConditions:
#     """Test change conditions
#     """

#     def test_set_mission_card(
#         self,
#         started_game_proc: processor_game.GameProcessor,
#             ) -> None:
#         """Test set mission card and change objective deck
#         """
#         game_proc = started_game_proc.set_mission_card()

#         assert isinstance(game_proc, processor_game.GameProcessor), 'wrong game_proce'
#         assert isinstance(game_proc.G.c.objective_deck.last.id, str), 'mission not set'
#         assert len(game_proc.G.c.objective_deck.current) == 20, 'wrong proc current'

#     def test_set_turn_priority_at_the_turn_0(
#         self,
#         started_game_proc: processor_game.GameProcessor,
#             ) -> None:
#         """Test set turn priority at the turn 0
#         """
#         started_game_proc.G.c.player.score = 30
#         started_game_proc.G.c.bot.score = 0

#         game_proc = started_game_proc.set_turn_priority()

#         assert isinstance(game_proc, processor_game.GameProcessor), 'wrong game_proce'
#         assert isinstance(game_proc.G.c.player.has_priority, bool), 'wrong priority'
#         assert isinstance(game_proc.G.c.bot.has_priority, bool), 'wrong priority'

#     @pytest.mark.parametrize("test_input,expected", [
#         ((30, 0), (False, True)),
#         ((0, 30), (True, False)),
#         ((0, 0), (None, None)),
#             ])
#     def test_set_turn_priority(
#         self,
#         test_input: Tuple[int],
#         expected: Tuple[bool],
#         started_game_proc: processor_game.GameProcessor,
#             ) -> None:
#         """Test set turn priority
#         """
#         started_game_proc.G.c.player.score = test_input[0]
#         started_game_proc.G.c.bot.score = test_input[1]
#         started_game_proc.G.c.steps.game_turn = 1

#         game_proc = started_game_proc.set_turn_priority()

#         assert game_proc.G.c.player.has_priority == expected[0], 'wrong priority'
#         assert game_proc.G.c.bot.has_priority == expected[1], 'wrong priority'

#     def test_set_phase_conditions_after_next_briefing(
#         self,
#         started_game_proc: processor_game.GameProcessor,
#             ) -> None:
#         """Test set_phase_conditions_after_next() set mission card
#         in briefing
#         """
#         started_game_proc.G.c.steps.last = started_game_proc.G.c.steps.c.by_id(Phases.BRIEFING.value)
#         card = started_game_proc.G.c.group_deck.pop()
#         started_game_proc.G.c.group_deck.pile.append(card.id)
#         started_game_proc.G.c.player.c.group_cards.append(card)
#         started_game_proc.G.c.bot.c.group_cards.append(card)
#         assert len(started_game_proc.G.c.group_deck.current) == 23, 'wrong groups'
#         assert len(started_game_proc.G.c.player.c.group_cards.current) == 1, \
#             'wrong revealed for player'
#         assert len(started_game_proc.G.c.bot.c.group_cards.current) == 1, \
#             'wrong revealed for bot'
#         assert len(started_game_proc.G.c.group_deck.pile) == 1, \
#             'wrong pile'

#         game_proc = started_game_proc.set_phase_conditions_after_next()

#         assert isinstance(game_proc.G.c.objective_deck.last.id, str), 'mission not set'
#         assert isinstance(game_proc.G.c.player.has_priority, bool), 'wrong priority'
#         assert isinstance(game_proc.G.c.bot.has_priority, bool), 'wrong priority'
#         assert len(started_game_proc.G.c.group_deck.current) == 24, 'wrong groups'
#         assert len(started_game_proc.G.c.player.c.group_cards.current) == 0, \
#             'wrong revealed for player'
#         assert len(started_game_proc.G.c.bot.c.group_cards.current) == 0, \
#             'wrong revealed for bot'
#         assert len(started_game_proc.G.c.group_deck.pile) == 0, \
#             'wrong pile'

#     @pytest.mark.parametrize("test_input", ['player', 'bot', ])
#     def test_set_phase_conditions_after_next_influence(
#         self,
#         started_game_proc: processor_game.GameProcessor,
#         test_input: str,
#             ) -> None:
#         """Test set phase condition after next in influence struggle change
#         returns vacated agents to hand
#         """
#         started_game_proc.G.c.steps.last = started_game_proc.G.c.steps.c.by_id(Phases.INFLUENCE.value)
#         cards = started_game_proc.G.c[test_input].c.agent_cards
#         cards.by_id(Agents.SPY.value).is_in_vacation = True
#         cards.by_id(Agents.SPY.value).is_revealed = True
#         cards.by_id(Agents.DIRECTOR.value).is_in_vacation = True
#         cards.by_id(Agents.DIRECTOR.value).is_revealed = False

#         game_proc = started_game_proc.set_phase_conditions_after_next()
#         cards = game_proc.G.c[test_input].c.agent_cards

#         assert cards.by_id(Agents.SPY.value).is_in_vacation is False, 'not changed'
#         assert cards.by_id(Agents.SPY.value).is_revealed is False, 'not changed'
#         assert cards.by_id(Agents.DIRECTOR.value).is_in_vacation is False, 'not changed'
#         assert cards.by_id(Agents.DIRECTOR.value).is_revealed is False, 'changed'

#     @pytest.mark.parametrize("test_input", ['player', 'bot', ])
#     def test_set_phase_conditions_after_next_debriefing(
#         self,
#         started_game_proc: processor_game.GameProcessor,
#         test_input: str,
#             ) -> None:
#         """Test set phase condition after next in debriefing
#         reveal agents in play
#         """
#         started_game_proc.G.c.steps.last = started_game_proc.G.c.steps.c.by_id(Phases.DEBRIFIENG.value)
#         cards = started_game_proc.G.c[test_input].c.agent_cards
#         cards.by_id(Agents.SPY.value).is_in_play = True
#         cards.by_id(Agents.SPY.value).is_revealed = True
#         cards.by_id(Agents.DIRECTOR.value).is_in_play = True
#         cards.by_id(Agents.DIRECTOR.value).is_revealed = False

#         game_proc = started_game_proc.set_phase_conditions_after_next()
#         cards = game_proc.G.c[test_input].c.agent_cards

#         assert cards.by_id(Agents.SPY.value).is_in_play is True, 'changed'
#         assert cards.by_id(Agents.SPY.value).is_revealed is True, 'changed'
#         assert cards.by_id(Agents.DIRECTOR.value).is_in_play is True, 'changed'
#         assert cards.by_id(Agents.DIRECTOR.value).is_revealed is True, 'not changed'

#     @pytest.mark.parametrize("test_input", ['player', 'bot', ])
#     def test_set_phase_conditions_after_next_detente(
#         self,
#         started_game_proc: processor_game.GameProcessor,
#         test_input: str,
#             ) -> None:
#         """Test set phase condition after next in detente
#         agents go to vacation and to hand
#         """
#         started_game_proc.G.c.steps.last = started_game_proc.G.c.steps.c.by_id(Phases.DETENTE.value)
#         cards = started_game_proc.G.c[test_input].c.agent_cards
#         cards.by_id(Agents.SPY.value).is_in_play = True
#         cards.by_id(Agents.SPY.value).is_revealed = True
#         cards.by_id(Agents.DEPUTY.value).is_in_play = True
#         cards.by_id(Agents.DEPUTY.value).is_revealed = True

#         game_proc = started_game_proc.set_phase_conditions_after_next()
#         cards = game_proc.G.c[test_input].c.agent_cards

#         assert cards.by_id(Agents.SPY.value).is_in_play is False, 'not changed'
#         assert cards.by_id(Agents.SPY.value).is_revealed is True, 'changed'
#         assert cards.by_id(Agents.SPY.value).is_in_vacation is True, 'not changed'
#         assert cards.by_id(Agents.DEPUTY.value).is_in_play is False, 'not changed'
#         assert cards.by_id(Agents.DEPUTY.value).is_revealed is False, 'not changed'
#         assert cards.by_id(Agents.DEPUTY.value).is_in_vacation is False, 'changed'
