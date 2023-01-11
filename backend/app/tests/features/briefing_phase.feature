@briefingphase
Feature: Briefing phase of the game
  
  Testing briefing phase for API: https://coldwar-api.onrender.com/docs

  Scenario: user goes into briefing phase with valid 'access_token' and without 'Analyst' card ability
    Given user using valid 'access_token'
    When user goes into 'Briefing' phase
    Then determine 'is_in_play' for random 'name' in 'objective_cards'
    And shuffle 'group_deck'
    And update 'current_data' of the game
    And user forced to use POST on '/api/v1/game/data/current'
    And user proceed to phase 'Planning'

  Scenario: user goes into briefing phase with valid 'access_token' and with 'Analyst' card ability
    Given user using valid 'access_token'
    And one of the users have 'Analyst' ability
    When user goes into 'Briefing' phase
    Then determine 'is_in_play' for random 'name' in 'objective_cards'
    And shuffle 'group_deck'
    And user with 'Analyst' ability must use PATCH method on endpoint '/api/v1/game/phase/briefing/analyst_look'
    And user with 'Analyst' ability must use PATCH method on endpoint '/api/v1/game/phase/briefing/analyst_arrange'
    And update 'current_data' of the game
    And user forced to use POST on '/api/v1/game/data/current'
    And user proceed to phase 'Planning'