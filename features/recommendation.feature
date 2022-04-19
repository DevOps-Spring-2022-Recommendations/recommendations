
Feature: The Recomendation store service back-end
    As a Recommendation Store Owner
    I need a RESTful catalog service
    So that I can keep track of all my Recommendations

Background:
    Given the server is started

Scenario: The server is running
    When I visit the "home page"
    Then I should see "Recommendation Demo REST API Service"
    And  I should not see "404 Not Found"