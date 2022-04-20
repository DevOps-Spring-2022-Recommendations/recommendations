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

Scenario: Change a statu
    When I visit the "Home Page"
    And I set the "Src Product ID" to "123"
    And I set the "Rec Product ID" to "321"
    And I select "Cross Sell" in the "Type" dropdown
    And I select "Enabled" in the "Status" dropdown
    And I press the "Create" button
    Then I should see the message "Success"
    When I copy the "ID" field
    And I press the "Clear" button
    When I paste the "ID" field
    And I press the "Search" button
    Then I should see "Enabled" in the "Status" dropdown
    When I select "Disabled" in the "Status" dropdown
    And I press the "Update" button
    Then I should see the message "Success"
    When I copy the "ID" field
    And I press the "Clear" button
    And I paste the "ID" field
    And I press the "Retrieve" button  
    Then I should see "Disabled" in the "Status" dropdown 
    When I copy the "ID" field
    And I press the "Clear" button
    And I paste the "ID" field
    And I press the "Search" button
    Then I should see "DISABLED" in the results
    Then I should not see "ENABLED" in the results
    
Scenario: Query recommendations by Type
    When I visit the "Home Page"
    When I visit the "Home Page"
    And I set the "Src Product ID" to "123"
    And I set the "Rec Product ID" to "321"
    And I select "Cross Sell" in the "Type" dropdown
    And I select "Enabled" in the "Status" dropdown
    And I press the "Create" button
    Then I should see the message "Success"
    When I press the "Clear" button
    And I select "Cross Sell" in the "Type" dropdown
    And I select "Enabled" in the "Status" dropdown
    And I press the "Search" button
    Then I should see "123" in the results
    And I should see "321" in the results
    And I should not see "886" in the results
