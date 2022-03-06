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
def get_recommendation():
    filter=None
    if(filter==None):
        products = Recommendation.all()
    results = [Recommendation.serialize() for product in products]
    app.logger.info("Returning %d products", len(results))
    return make_response("items returned", status.HTTP_200_OK)
######################################################################
# RETRIEVE A RECOMMENDATION BY ID
######################################################################



######################################################################
# ADD A NEW RECOMMENDATION
######################################################################

@app.route("/recommendations", methods=["POST"])
def create_Recommendation():
    """
    Creates a Recommendation
    This endpoint will create a Product based the data in the body that is posted
    """
    app.logger.info("Request to create a Product")
    check_content_type("application/json")
    recommendation = Recommendation()
    recommendation.deserialize(request.get_json())
    recommendation.create()
    message = recommendation.serialize()
    location_url = url_for("get_recommendation", item_id=recommendation.id, _external=True)

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
@app.route("/recommendations/<int:item_id>", methods=["DELETE"])
def delete_recommendations(item_id):
    """
    Delete a recommendation
    This endpoint will delete a recommendation based the id specified in the path
    """
    app.logger.info("Request to delete recommendation with id: %s", item_id)
    recommendation = Recommendation.find(item_id)
    if recommendation:
        recommendation.delete()

    app.logger.info("recommendation with ID [%s] delete complete.", item_id)
    return make_response("", status.HTTP_204_NO_CONTENT)

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
