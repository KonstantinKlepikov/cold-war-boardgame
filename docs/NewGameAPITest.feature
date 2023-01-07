@newgame
Feature: Creating new game
  
  Creating new game using API: https://coldwar-api.onrender.com/docs

  Scenario: user creating new game with valid 'access_token'
    Given user using valid 'access_token'
    And using POST method on endpoint '/api/v1/game/create'
    And using PATCH method on edpoint '/api/v1/game/preset/faction' with <faction> name
    When user sending requests
    Then new object in database created
    And setup player <faction>
    And setup random priority for a player
    And setup 'game_turn' as '1' and 'game_phase' as 'briefing'
    And user get responses with status code '201' and '200'
    And user get 'data/static' of the game
    And user get 'data/current' of the game
    And user proceed next

    Examples:
    | faction |
    | CIA |
    | KGB |



  Scenario: user creating new game with valid 'access_token'
    Given user using POST method on endpoint '/api/v1/game/create' to start 'new_game'
    And user has valid 'access_token' and user doesn't have a 'unfinished_game' object in database
    When user sending request
    Then user get response with status code '201' and 'static_data' of the game
    And in database 'new_game' object created

  Scenario: user creating new game without valid 'access_token'
    Given user using POST method on endpoint '/api/v1/game/create' to start 'new_game'
    And user does not have valid 'access_token' and user doesn't have a 'unfinished_game' object in database
    When user sending request
    Then user get response with status code '401'

  Scenario: user creating new game while he have unfinished game with valid 'access_token'
    Given user using POST method on endpoint '/api/v1/game/create' to start 'new_game'
    And user has valid 'access_token' and user have a 'unfinished_game' object in database
    When user sending request
    Then user get response with status code '201' and 'static_data' of the game
    And in database 'new_game' object created