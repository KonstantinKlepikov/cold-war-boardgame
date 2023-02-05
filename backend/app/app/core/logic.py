from fastapi import HTTPException
from app.crud.crud_game_static import StaticGameData
from app.crud.crud_game_current import CurrentGameData
from app.schemas.scheme_game_current_api import CurrentGameDataApi
from app.schemas.scheme_game_current import (
    CurrentGameDataProcessor, AgentInPlayProcessor, GroupInPlayProcessor,
    ObjectiveInPlayProcessor
        )
from app.constructs import Factions, Agents, Groups, Objectives, Phases
from bgameb import Step, errors


class GameLogic:
    """Create the game object to manipulation of game tools

    Args:
    """

    def __init__(
        self,
        static: StaticGameData,
        game: CurrentGameData,
            ) -> None:
        self.static = static
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
        """Get redy to use api scheme

        Returns:
            CurrentGameDataApi: api scheme
        """
        data = self.proc.dict(by_alias=True)
        return CurrentGameDataApi(**data)

    def deal_and_shuffle_decks(self) -> 'GameLogic':
        """Shuffle objective and group decks

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
                detail="You cant change faction because is choosen yet"
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

        self.proc.steps.game_turn += 1
        self.proc.steps.deal().pop()

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

    def _check_analyct_condition(self) -> None:
        """Check conditions for play analyst ability
        """
        if self.proc.steps.last_id != Phases.BRIEFING.value:
            raise HTTPException(
                status_code=409,
                detail="Ability can't be played in any phases except 'briefing'."
                    )
        if Agents.ANALYST not in self.proc.players.player.awaiting_abilities:
            raise HTTPException(
                status_code=409,
                detail="No access to play ability of Analyst agent card."
                    )

    def play_analyst_for_look_the_top(self) -> 'GameLogic':
        """Play analyst abylity for look the top cards

        Returns:
            GameLogic
        """
        self._check_analyct_condition()

        if all([
            card.is_revealed_to_player for card
            in self.proc.decks.groups.current
                ][-3:]):
            raise HTTPException(
                status_code=409,
                detail="Top 3 group cards is yet revealed for player."
                    )

        for pos in range(-3, 0):
            self.proc.decks.groups.current[pos].is_revealed_to_player = True

        return self

    def play_analyst_for_arrange_the_top(
        self, top: list[Groups]) -> 'GameLogic':
        """Play analyst abylity for rearrange the top cards

        Args:
            top (list[Groups]): arranged cards

        Returns:
            GameLogic
        """
        self._check_analyct_condition()

        try:
            self.proc.decks.groups.reorderfrom(top, len(self.proc.decks.groups.current)-3)
            self.proc.players.player.awaiting_abilities.remove(Agents.ANALYST.value)

        except errors.ArrangeIndexError:
            raise HTTPException(
                status_code=409,
                detail="Your list of cards and top cards not match."
                    )

        return self

    def set_agent(
        self,
        agent_id: Agents,
            ) -> 'GameLogic':
        """Set agent card

        Returns:
            GameLogic
        """
        choice = self.proc.players.player.agents.by_id(agent_id)
        if choice and choice[0].is_in_headquarter is True:
            choice[0].is_agent_x = True
            choice[0].is_in_headquarter = False
            if Agents.DOUBLE in self.proc.players.player.awaiting_abilities:
                choice[0].is_revealed = True
                self.proc.players.player.awaiting_abilities.remove(Agents.DOUBLE.value)
        else:
            raise HTTPException(
                status_code=409,
                detail=f"Agent {agent_id} not available to choice."
                    )
        return self

    def chek_phase_conditions_before_next(self) -> 'GameLogic':
        """Check game conition before push to next phase
        and raise exception if any check fails

        Returns:
            GameLogic
        """
        if self.proc.steps.is_game_ends:
            raise HTTPException(
                status_code=409,
                detail="Something can't be changed, because game is end"
                    )

        # phase = self.G.c.steps.turn_phase
        phase = self.proc.steps.last_id

        # briefing
        if phase == Phases.BRIEFING:

            # players has't priority
            if not self.proc.players.player.has_balance \
                    and not self.proc.players.opponent.has_balance:
                raise HTTPException(
                    status_code=409,
                    detail="No one player has priority. Cant push to next phase."
                        )

            # objective card not defined
            if self.proc.decks.objectives.last is None:
                raise HTTPException(
                    status_code=409,
                    detail="Mission card undefined. Cant push to next phase."
                        )

            # analyst not used
            if Agents.ANALYST in self.proc.players.player.awaiting_abilities:
                raise HTTPException(
                    status_code=409,
                    detail="Analyst ability must be used."
                        )

            # agent not choosen
            if self.proc.players.player.agents.agent_x is None:
                raise HTTPException(
                    status_code=409,
                    detail=f"Agent not choosen."
                        )

        # planning
        elif phase == Phases.PLANNING:
            pass

        # influence_struggle
        elif phase == Phases.INFLUENCE:
            pass

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
            pass

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
