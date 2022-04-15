# recommendations
[![Build Status](https://github.com/DevOps-Spring-2022-Recommendations/recommendations/actions/workflows/workflow.yml/badge.svg)](https://github.com/DevOps-Spring-2022-Recommendations/recommendations/actions)
[![Build Status](https://github.com/nyu-devops/lab-flask-bdd/actions/workflows/bdd-tests.yml/badge.svg)](https://github.com/nyu-devops/lab-flask-bdd/actions)
[![Codecov](https://codecov.io/gh/DevOps-Spring-2022-Recommendations/recommendations/branch/master/graph/badge.svg)](https://codecov.io/gh/DevOps-Spring-2022-Recommendations/recommendations)

The recommendations resource is a representation a product recommendation based on
another product. In essence it is just a relationship between two products that "go
together" (e.g., radio and batteries, printers and ink, shirts and pants, etc.). It could also
recommend based on what other customers have purchased like "customers who bought item A
usually buy item B". Recommendations should have a recommendation type like cross-sell, upsell, accessory, etc. This way a product page could request all of the up-sells for a product.
(Hint: an up-sell is a more full featured and expensive product that you recommend instead of
the one they initially want to buy, cross-sells are other items just like this one with similar
features and price.) You should use enumerations to represent the different recommendation
types.    


## Available Calls
/recommendations: GET \
/recommendations: POST \
/recommendations/\<int:id>: GET \
/recommendations/\<int:id>: PUT \
/recommendations/\<int:id>: DELETE
