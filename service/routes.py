"""
Recommendations Service

The recommendations resource is a representation a product recommendation based on another product
"""

from flask import jsonify, request, url_for, abort, make_response
from service.models import Recommendation, Status
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
    """Returns all of the recommendation"""
    recommendations = Recommendation.all()
    results = [recommendation.serialize() for recommendation in recommendations]
    app.logger.info("Returning %d recommendations", len(results))
    return make_response(jsonify(results), status.HTTP_200_OK)

@app.route("/recommendations", methods=["GET"])
def list_recommendations_by_rec_id():
    """Returns all of the recommendation"""
    app.logger.info("Request for recommendations list")
    recommendations = []
    rec_product_id = request.args.get("rec_product_id")
    if rec_product_id:
        recommendations = Recommendation.find_by_rec_product_id(int(rec_product_id))
    else:
        recommendations = Recommendation.all()
    results = [recommendation.serialize() for recommendation in recommendations]
    app.logger.info("Returning %d recommendations", len(results))
    return make_response(jsonify(results), status.HTTP_200_OK)


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
@app.route("/recommendations/<int:item_id>", methods=["PUT"])
def update_recommendations(item_id):
    """
    Update a Recommendation
    This endpoint will update a Recommendation based the body that is posted
    """
    app.logger.info("Request to update a recommendation with id: %s", item_id)
    check_content_type("application/json")
    recommendation = Recommendation.find(item_id)
    if not recommendation:
        raise NotFound("recommendation with id '{}' was not found.".format(item_id))
    recommendation.deserialize(request.get_json())
    recommendation.id = item_id
    recommendation.update()

    app.logger.info("recommendation with ID [%s] updated.", recommendation.id)
    return make_response(jsonify(recommendation.serialize()), status.HTTP_200_OK)

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
# ACTION: ENABLE AND DISABLE A RECOMMENDATION
######################################################################
@app.route("/recommendations/<int:id>/enable", methods=["PUT"])
def enable_recommendations(id):
    """
    Enable a recommendation
    This endpoint will enable a recommendation based on the id specified in the path
    """
    app.logger.info("Request to enable recommendation with id: %s", id)
    recommendation = Recommendation.find(id)
    if not recommendation:
        raise NotFound("recommendation with id '{}' was not found.".format(id))
    recommendation.deserialize(request.get_json())
    recommendation.status = Status.ENABLED
    recommendation.update()

    app.logger.info("recommendation with ID [%s] enabled.", recommendation.id)
    return make_response(jsonify(recommendation.serialize()), status.HTTP_200_OK)

@app.route("/recommendations/<int:id>/disable", methods=["PUT"])
def disable_recommendations(id):
    """
    Disable a recommendation
    This endpoint will disable a recommendation based on the id specified in the path
    """
    app.logger.info("Request to disable recommendation with id: %s", id)
    recommendation = Recommendation.find(id)
    if not recommendation:
        raise NotFound("recommendation with id '{}' was not found.".format(id))
    recommendation.deserialize(request.get_json())
    recommendation.status = Status.DISABLED
    recommendation.update()

    app.logger.info("recommendation with ID [%s] disabled.", recommendation.id)
    return make_response(jsonify(recommendation.serialize()), status.HTTP_200_OK)

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
