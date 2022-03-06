"""
Recommendations Service

The recommendations resource is a representation a product recommendation based on another product
"""

from flask import jsonify, request, url_for, abort, make_response
from service.models import Recommendation
from . import app, status  # HTTP Status Codes
from werkzeug.exceptions import NotFound

######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    app.logger.info("Request for Root URL")
    return (
        jsonify(
            name="Recommendation REST API Service",
            version="1.0",
            paths=url_for("list_recommendations", _external=True),
        ),
        status.HTTP_200_OK,
    )

######################################################################
# LIST ALL RECOMMENDATIONS
######################################################################

@app.route("/recommendations", methods=["GET"])
def list_recommendations():
    products = Recommendation.all()
    results = [product.serialize() for product in products]
    app.logger.info("Returning %d products", len(results))
    return make_response(jsonify(results), status.HTTP_200_OK)
    """Returns all of the recommendation"""
    app.logger.info("Request for recommendation for category")
    # category = request.args.get("category")
    # name = request.args.get("name")
    # price = request.args.get("price")
    # if category:
    #     products = Recommendation.find_by_category(category)
    # elif name:
    #     products = Recommendation.find_products_of_same_category(name)
    # elif price:
    #     products = Recommendation.find_highest_price_product_by_category(category)
    # else:


######################################################################
# RETRIEVE A RECOMMENDATION BY ID
######################################################################

@app.route("/recommendations/<int:id>", methods=["GET"])
def get_recommendations(id):
    """
    Retrieve a single Recommendation

    This endpoint will return a Recommendation based on it's id
    """
    app.logger.info("Request for recommendation with id: %s", id)
    recommendation = Recommendation.find(id)
    if not recommendation:
        raise NotFound("Recommendation with id '{}' was not found.".format(id))

    app.logger.info("Returning recommendation: %s", recommendation.id)
    return make_response(jsonify(recommendation.serialize()), status.HTTP_200_OK)

######################################################################
# ADD A NEW RECOMMENDATION
######################################################################

@app.route("/recommendations", methods=["POST"])
def create_recommendations():
    """
    Creates a Recommendation
    This endpoint will create a Recommendation based the data in the body that is posted
    """
    app.logger.info("Request to create a Recommendation")
    check_content_type("application/json")
    recommendation = Recommendation()
    recommendation.deserialize(request.get_json())
    recommendation.create()
    message = recommendation.serialize()
    location_url = url_for("get_recommendations", id=recommendation.id, _external=True)

    app.logger.info("Recommendation with ID [%d] created.", recommendation.id)
    return make_response(
        jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}
    )

######################################################################
# UPDATE AN EXISTING RECOMMENDATION
######################################################################


######################################################################
# DELETE A RECOMMENDATION
######################################################################


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################

def check_content_type(media_type):
    """Checks that the media type is correct"""
    content_type = request.headers.get("Content-Type")
    if content_type and content_type == media_type:
        return
    app.logger.error("Invalid Content-Type: %s", content_type)
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        "Content-Type must be {}".format(media_type),
    )

def init_db():
    """ Initializes the SQLAlchemy app """
    Recommendation.init_db(app)
