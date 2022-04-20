Feature: The Recomendation store service back-end
    As a Recommendation Service Owner
    I need a RESTful catalog service
    So that I can keep track of all the Recommendations

Background:
    Given the following recommendations
        | src_product_id    | rec_product_id    | type          | status    |
        | 100    | 200    | CROSS_SELL          | ENABLED    |
        | 101    | 201    | CROSS_SELL          | DISABLED    |

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Recommendation Demo RESTful Service" in the title
    And I should not see "404 Not Found"

Scenario: Create a Recommendation
    When I visit the "Home Page"
    And I set the "Src Product ID" to "12"
    And I set the "Rec Product ID" to "23"
    And I select "Cross Sell" in the "Type" dropdown
    And I select "Enabled" in the "Status" dropdown
    And I press the "Create" button
    Then I should see the message "Success"
    When I copy the "ID" field
    And I press the "Clear" button
    Then the "ID" field should be empty
    And the "Src Product ID" field should be empty
    And the "Rec Product ID" field should be empty
    When I paste the "ID" field
    And I press the "Retrieve" button
    Then I should see "12" in the "Src Product ID" field
    And I should see "23" in the "Rec Product ID" field
    And I should see "Cross Sell" in the "Type" dropdown
    And I should see "Enabled" in the "Status" dropdown

Scenario: List all recommendations
    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see "100" in the results
    And I should see "200" in the results
    And I should see "201" in the results
    And I should see "101" in the results
    And I should not see "300" in the results
