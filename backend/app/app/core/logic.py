from typing import Union, Optional
from fastapi import HTTPException
from app.crud.crud_game_current import CurrentGameData
from app.schemas.scheme_game_current_api import CurrentGameDataApi
from app.schemas.scheme_game_current import (
    CurrentGameDataProcessor, AgentInPlayProcessor, GroupInPlayProcessor,
    ObjectiveInPlayProcessor, PlayerProcessor, OpponentProcessor
        )
from app.constructs import (
    Factions, Agents, Groups, Objectives, Phases, Sides, MilitaryGroups
        )
from bgameb import Step, errors


class GameLogic:
    """Create the game object to manipulation of game tools
    """

    def __init__(
        self,
        game: CurrentGameData,
            ) -> None:
        self.game = game
        self.proc = self._fill_process()

    def _fill_process(self) -> CurrentGameDataProcessor:
        """Get game processor with db game data
        """
        game = self.game.to_mongo().to_dict()
        proc = CurrentGameDataProcessor(**game)

        # fill steps
        for num, step in enumerate(Phases):
            proc.steps.add(Step(id=step.value, priority=num))

        # fill players

        for card in Agents:
            proc.players.player.agents.add(
                AgentInPlayProcessor(id=card.value)
                    )
            proc.players.opponent.agents.add(
                AgentInPlayProcessor(id=card.value)
                    )

        # fill decks
        for card in Groups:
            proc.decks.groups.add(
                GroupInPlayProcessor(id=card.value)
                    )
        for card in Objectives:
            proc.decks.objectives.add(
                ObjectiveInPlayProcessor(id=card.value)
                    )

        proc.fill()

        return proc

    def get_api_scheme(self) -> CurrentGameDataApi:
        """Get ready to use api scheme

        Returns:
            CurrentGameDataApi: api scheme
        """
        data = self.proc.dict(by_alias=True)
        return CurrentGameDataApi(**data)

    def deal_and_shuffle_decks(self) -> 'GameLogic':
        """Deal and shuffle objective and group decks

        Returns:
            GameLogic
        """
        self.proc.decks.groups.deal().shuffle()
        self.proc.decks.objectives.deal().shuffle()

        return self

    def set_faction(self, faction: Factions) -> 'GameLogic':
        """Set player and opponent faction

        Args:
            faction (Factions): player faction

        Returns:
            GameLogic
        """
        if isinstance(self.proc.players.player.faction, str):
            raise HTTPException(
                status_code=409,
                detail="You cant change faction because is chosen yet"
                    )

        self.proc.players.player.faction = faction.value
        self.proc.players.opponent.faction = Factions.KGB \
            if faction == Factions.CIA else Factions.CIA

        return self

    def set_next_turn(self) -> 'GameLogic':
        """Set next turn

        Returns:
            GameLogic
        """
        if self.proc.steps.is_game_ends is True:
            raise HTTPException(
                status_code=409,
                detail="Something can't be changed, because game is end"
                    )

        if self.proc.steps.last_id == Phases.DETENTE.value:

            self.proc.steps.game_turn += 1
            self.proc.steps.deal().pop()

        else:
            raise HTTPException(
                status_code=409,
                detail="You can set next turn only from detente phase"
                    )

        return self

    def set_next_phase(self) -> 'GameLogic':
        """Set next phase

        Returns:
            GameLogic
        """
        if self.proc.steps.last_id != Phases.DETENTE.value:
            self.proc.steps.pop()

        return self

    def set_mission_card(self) -> 'GameLogic':
        """Set mission card on a turn

        Returns:
            GameLogic
        """
        try:
            self.proc.decks.objectives.pop()
        except IndexError:
            raise HTTPException(
                status_code=409,
                detail="Objective deck is empty."
                    )

        return self

    def set_balance(self) -> 'GameLogic':
        """Set balance to the turn. Balance is used in influence struggle.

        Returns:
            GameLogic
        """
        if self.proc.steps.game_turn == 1:
            val = True if self.proc.coin.roll()[0] == 1 else False
        elif self.proc.players.player.score < self.proc.players.opponent.score:
            val = True
        elif self.proc.players.player.score > self.proc.players.opponent.score:
            val = False
        else:
            # TODO: change condition:
            # if loose previous seas fire phase -> True
            # if both loose -> return self
            return self

        self.proc.players.player.has_balance = val
        self.proc.players.opponent.has_balance = not val

        return self

    def _get_side_proc(self, side: Sides) -> Union[PlayerProcessor, OpponentProcessor]:
        if side == Sides.PLAYER:
            return self.proc.players.player
        else:
            return self.proc.players.opponent

    def _check_analyct_condition(self, side: Sides = Sides.PLAYER) -> None:
        """Check conditions for play analyst ability

        Args:
            side (Sides): player or opponent, default to 'player'
        """
        if self.proc.steps.last_id != Phases.BRIEFING:
            raise HTTPException(
                status_code=409,
                detail="Analyst ability can be played only in 'briefing' phase."
                    )
        if Agents.ANALYST not in self._get_side_proc(side).awaiting_abilities:
            raise HTTPException(
                status_code=409,
                detail="No access to play ability of Analyst agent card."
                    )

    def play_analyst_for_look_the_top(self, side: Sides = Sides.PLAYER) -> 'GameLogic':
        """Play analyst abylity for look the top cards

        Args:
            side (Sides): player or opponent, default to 'player'

        Returns:
            GameLogic
        """
        self._check_analyct_condition(side)

        if side == Sides.PLAYER:
            rev =  all([
                card.is_revealed_to_player for card
                in self.proc.decks.groups.current
                    ][-3:])
        else:
            rev =  all([
                card.is_revealed_to_opponent for card
                in self.proc.decks.groups.current
                    ][-3:])
        if rev:
            raise HTTPException(
                status_code=409,
                detail="Top 3 group cards is yet revealed."
                    )

        if side == Sides.PLAYER:
            for pos in range(-3, 0):
                self.proc.decks.groups.current[pos].is_revealed_to_player = True
        else:
            for pos in range(-3, 0):
                self.proc.decks.groups.current[pos].is_revealed_to_opponent = True

        return self

    def play_analyst_for_arrange_the_top(
        self,
        top: list[Groups],
        side: Sides = Sides.PLAYER
            ) -> 'GameLogic':
        """Play analyst abylity for rearrange the top cards

        Args:
            top (list[Groups]): arranged cards
            side (Sides): player or opponent, default to 'player'

        Returns:
            GameLogic
        """
        self._check_analyct_condition(side)

        try:
            self.proc.decks.groups.reorderfrom(top, len(self.proc.decks.groups.current)-3)
            self._get_side_proc(side).awaiting_abilities.remove(Agents.ANALYST.value)

        except errors.ArrangeIndexError:
            raise HTTPException(
                status_code=409,
                detail="Your list of cards and top cards not match."
                    )

        return self

    def set_agent_x(
        self,
        agent: Agents,
        side: Sides = Sides.PLAYER
            ) -> 'GameLogic':
        """Set agent card

        Args:
            agent (Agents): agent for current turn
            side (Sides): player or opponent, default to 'player'

        Returns:
            GameLogic
        """
        if self.proc.steps.last_id != Phases.PLANNING:
            raise HTTPException(
                status_code=409,
                detail="Agent can be set only in 'planning' phase."
                    )

        user = self._get_side_proc(side)
        choice = user.agents.by_id(agent)

        if choice and choice[0].is_in_headquarter is True:
            choice[0].is_agent_x = True
            choice[0].is_in_headquarter = False
            if Agents.DOUBLE in user.awaiting_abilities:
                choice[0].is_revealed = True
                user.awaiting_abilities.remove(Agents.DOUBLE)
        else:
            raise HTTPException(
                status_code=409,
                detail=f"Agent {agent} not available to choice."
                    )

        return self

    def _check_influence_condition(self) -> None:
        """Check influence struggle conditions
        """
        if self.proc.steps.last_id != Phases.INFLUENCE:
            raise HTTPException(
                status_code=409,
                detail="Group can be recruited only in 'influence struggle' phase."
                    )

        if self.proc.players.player.influence_pass is True and \
                self.proc.players.opponent.influence_pass is True:
            raise HTTPException(
                status_code=409,
                detail="Both sides are pass. You cant do anithing."
                    )

    def recruit_group(self, side: Sides = Sides.PLAYER) -> 'GameLogic':
        """Recruit group

        Args:
            side (Sides): player or opponent, default to 'player'

        Returns:
            GameLogic
        """
        self._check_influence_condition()

        if side == Sides.PLAYER:
            owned = self.proc.decks.groups.owned_by_player
        else:
            owned = self.proc.decks.groups.owned_by_opponent

        draw = self.proc.decks.groups.pop()
        draw.is_revealed_to_player = True
        draw.is_revealed_to_opponent = True
        owned.append(draw)

        return self

    def activate_group(
        self,
        source: Groups,
        target: Optional[Groups] = None,
        side: Sides = Sides.PLAYER,
            ) -> 'GameLogic':
        """Activate group

        Args:
            source (Groups): group, owned by player. Must be active
            source (Groups, optioanl): Targetgroup. Must be active. Default to None
            side (Sides): player or opponent, default to 'player'

        Returns:
            GameLogic
        """
        self._check_influence_condition()

        return self


    def pass_influence(self, side: Sides = Sides.PLAYER) -> 'GameLogic':
        """Pass in influence phase

        Args:
            side (Sides): player or opponent, default to 'player'

        Returns:
            GameLogic
        """
        self._check_influence_condition()

        if side == Sides.PLAYER:
            owned = self.proc.decks.groups.owned_by_player
        else:
            owned = self.proc.decks.groups.owned_by_opponent

        if len(owned) == 0:
            raise HTTPException(
                status_code=409,
                detail="You cant pass while you no control any group."
                    )

        user = self._get_side_proc(side)
        user.influence_pass = True

        return self

    def _discard_all_military_groups(
        self,
        play: list[GroupInPlayProcessor]
            ) -> list[GroupInPlayProcessor]:
        """Discard all military group from play of given side

        Args:
            play (list[Groups]): given side play before discard

        Returns:
            list[Groups]: given side play after discard
        """
        result = []
        for group in play:
            if group.id.value not in MilitaryGroups.get_values():
                result.append(group)
            else:
                self.proc.decks.groups.pile.append(group)

        return result

    def nuclear_escalation(self, side: Sides = Sides.PLAYER) -> 'GameLogic':
        """Pass in influence phase

        Args:
            side (Sides): player or opponent, default to 'player'

        Returns:
            GameLogic
        """
        self._check_influence_condition()

        if side == Sides.PLAYER:
            owned_ob = self.proc.decks.objectives.owned_by_player
        else:
            owned_ob = self.proc.decks.objectives.owned_by_opponent

        for ind, objective in enumerate(owned_ob):
            if objective is Objectives.NUCLEARESCALATION:

                self.proc.decks.groups.owned_by_player = self._discard_all_military_groups(
                    self.proc.decks.groups.owned_by_player
                        )
                self.proc.decks.groups.owned_by_opponent = self._discard_all_military_groups(
                    self.proc.decks.groups.owned_by_opponent
                        )

                self.proc.decks.objectives.pile.append(objective)
                del owned_ob[ind]

                return self

        raise HTTPException(
            status_code=409,
            detail="Nuclear escalation not available for this player."
                )

    def chek_phase_conditions_before_next(self) -> 'GameLogic':
        """Check game conition before push to next phase
        and raise exception if any check fails

        Returns:
            GameLogic
        """
        # game is over
        if self.proc.steps.is_game_ends:
            raise HTTPException(
                status_code=409,
                detail="Something can't be changed, because game is end"
                    )

        # phase = self.G.c.steps.turn_phase
        phase = self.proc.steps.last_id

        # briefing
        if phase == Phases.BRIEFING:

            # game is not started
            if self.proc.players.player.faction is None \
                    or self.proc.players.opponent.faction is None:
                raise HTTPException(
                    status_code=409,
                    detail="Faction not choosen. Use game/reset/faction to set faction."
                        )

            # objective card not defined
            if self.proc.decks.objectives.last is None:
                raise HTTPException(
                    status_code=409,
                    detail="Mission card undefined. Cant push to next phase."
                        )

            # players has't balance
            if self.proc.players.player.has_balance is self.proc.players.opponent.has_balance:
                raise HTTPException(
                    status_code=409,
                    detail="No one side has balance. Cant push to next phase."
                        )

            # analyst not used
            if Agents.ANALYST in self.proc.players.player.awaiting_abilities:
                raise HTTPException(
                    status_code=409,
                    detail="Analyst ability must be used by player."
                        )

            if Agents.ANALYST in self.proc.players.opponent.awaiting_abilities:
                raise HTTPException(
                    status_code=409,
                    detail="Analyst ability must be used by opponent."
                        )

        # planning
        elif phase == Phases.PLANNING:

            # agent not choosen
            if self.proc.players.player.agents.agent_x is None:
                raise HTTPException(
                    status_code=409,
                    detail=f"Agent for player not choosen."
                        )

            if self.proc.players.opponent.agents.agent_x is None:
                raise HTTPException(
                    status_code=409,
                    detail=f"Agent for opponent not choosen."
                        )

        # influence_struggle
        elif phase == Phases.INFLUENCE:

            # Both players must pass in group subgame
            if self.proc.players.player.influence_pass is not True or \
                self.proc.players.opponent.influence_pass is not True:
                raise HTTPException(
                    status_code=409,
                    detail="Both side must pass in group subgame before next phase."
                        )

        # ceasefire
        elif phase == Phases.CEASEFIRE:
            pass

        # debriefing
        elif phase == Phases.DEBRIFIENG:
            pass

        # detente
        elif phase == Phases.DETENTE:
            raise HTTPException(
                status_code=409,
                detail="This phase is last in a turn. Change turn number "
                        "before get next phase"
                    )

        return self

    def set_phase_conditions_after_next(self) -> 'GameLogic':
        """Set som phase conditions after push phase

        Returns:
            GameLogic
        """
        phase = self.proc.steps.last_id

        # set briefing states after next
        if phase == Phases.BRIEFING:

            self.set_mission_card()
            self.set_balance()
            self.proc.decks.groups.deal()
            self.proc.decks.groups.pile.clear()
            self.proc.decks.groups.owned_by_opponent.clear()
            self.proc.decks.groups.owned_by_player.clear()

        # planning
        elif phase == Phases.PLANNING:
            pass


        # influence_struggle
        elif phase == Phases.INFLUENCE:

            # return all agents from on_leave to headquarter
            for deck in [
                self.proc.players.player.agents.current,
                self.proc.players.opponent.agents.current
                    ]:
                for agent in deck:
                    if agent.is_on_leave == True:
                        agent.is_on_leave = False
                        agent.is_in_headquarter = False
                        agent.is_revealed = False

        # ceasefire
        elif phase == Phases.CEASEFIRE:

            # clear influence struggle pass
            self.proc.players.player.influence_pass = False
            self.proc.players.opponent.influence_pass = False

        # debriefing
        elif phase == Phases.DEBRIFIENG:

            # open all agents in play
            for deck in [
                self.proc.players.player.agents.current,
                self.proc.players.opponent.agents.current
                    ]:
                for agent in deck:
                    if agent.is_agent_x == True:
                        agent.is_revealed = True

        # detente
        elif phase == Phases.DETENTE:

            # put agents to on_leave from play
            for deck in [
                self.proc.players.player.agents.current,
                self.proc.players.opponent.agents.current
                    ]:
                for agent in deck:
                    if agent.is_agent_x == True:
                        agent.is_agent_x = False
                    if agent.id == Agents.DEPUTY:
                        agent.is_in_headquarter = True
                        agent.is_revealed = False
                    else:
                        agent.is_on_leave = True
                        agent.is_revealed = True

        return self
