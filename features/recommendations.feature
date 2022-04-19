Feature: The Recomendation store service back-end
    As a Recommendation Service Owner
    I need a RESTful catalog service
    So that I can keep track of all the Recommendations

Background:
    Given the following recommendations
        | src_product_id    | rec_product_id    | type          | status    |

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Recommendation Demo REST API Service"
    And I should not see "404 Not Found"
