"""
Recommendations Service

The recommendations resource is a representation a product recommendation based on another product
"""

from flask import jsonify, request, url_for, abort, make_response
from service.models import Recommendation, Status, Type, DataValidationError, DatabaseConnectionError
from . import app
from .utils import status
from werkzeug.exceptions import NotFound
from flask_restx import Api, Resource, fields, reqparse, inputs

# Document the type of autorization required
authorizations = {
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'X-Api-Key'
    }
}

######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Base URL for our service"""
    return app.send_static_file("index.html")

######################################################################
# Configure Swagger before initializing it
######################################################################
api = Api(app,
          version='1.0.0',
          title='Recommendation Demo REST API Service',
          description='This is a sample server Recommendation store server.',
          default='recommendations',
          default_label='Recommendation shop operations',
          doc='/apidocs', # default also could use doc='/apidocs/'
          authorizations=authorizations,
          prefix='/api'
         )

# Define the model so that the docs reflect what can be sent
create_model = api.model('Recommendation', {
    'id': fields.Integer(required=True,
                          description='The id of the recommendation'),
    'src_product_id': fields.Integer(required=True,
                              description='The source ID of recommendation'),
    'rec_product_id': fields.Integer(required=True,
                              description='The target ID of recommendation'),
    'type': fields.String(enum=Type._member_names_, description='The type of the recommendation'),
    'status': fields.String(enum=Status._member_names_, description='The status of the recommendation')
})

recommendation_model = api.inherit(
    'RecommendationModel', 
    create_model,
    {
        '_id': fields.String(readOnly=True,
                            description='The unique id assigned internally by service'),
    }
)


# query string arguments
recommendation_args = reqparse.RequestParser()
recommendation_args.add_argument('src_product_id', type=int, required=False, help='List Recommendations by source ID')


######################################################################
# LIST ALL RECOMMENDATIONS
######################################################################

@app.route("/recommendations", methods=["GET"])
def list_recommendations():
    """Returns all of the recommendation"""
    app.logger.info("Request to list Recommendations...")

    recommendations = []
    src_product_id = request.args.get("src_product_id")
    rec_product_id = request.args.get("rec_product_id")
    type = request.args.get("type")

    if src_product_id:
        app.logger.info("Find by source product id: %s", src_product_id)
        recommendations = Recommendation.find_by_src_id(int(src_product_id))
    elif rec_product_id:
        app.logger.info("Find by recommendation product id: %s", rec_product_id)
        recommendations = Recommendation.find_by_rec_id(int(rec_product_id))
    elif type:
        app.logger.info("Find by type: %s", type)
        recommendations = Recommendation.find_by_type(type)
    else:
        app.logger.info("Find all")
        recommendations = Recommendation.all()

    results = [recommendation.serialize() for recommendation in recommendations]
    app.logger.info("Returning %d recommendations", len(results))
    return make_response(jsonify(results), status.HTTP_200_OK)


######################################################################
# Special Error Handlers
######################################################################
@api.errorhandler(DataValidationError)
def request_validation_error(error):
    """ Handles Value Errors from bad data """
    message = str(error)
    app.logger.error(message)
    return {
        'status_code': status.HTTP_400_BAD_REQUEST,
        'error': 'Bad Request',
        'message': message
    }, status.HTTP_400_BAD_REQUEST

@api.errorhandler(DatabaseConnectionError)
def database_connection_error(error):
    """ Handles Database Errors from connection attempts """
    message = str(error)
    app.logger.critical(message)
    return {
        'status_code': status.HTTP_503_SERVICE_UNAVAILABLE,
        'error': 'Service Unavailable',
        'message': message
    }, status.HTTP_503_SERVICE_UNAVAILABLE


######################################################################
#  PATH: /recommendations/{id}
######################################################################
@api.route('/recommendations/<recommendation_id>')
@api.param('recommendation_id', 'The recommendation identifier')
class RecommendationResource(Resource):
    """
    RecommendationResource class

    Allows the manipulation of a single recommendation
    GET /recommendation{id} - Returns a recommendation with the id
    PUT /recommendation{id} - Update a recommendation with the id
    DELETE /recommendation{id} -  Deletes a recommendation with the id
    """

    #------------------------------------------------------------------
    # RETRIEVE A RECOMMENDATION
    #------------------------------------------------------------------
    @api.doc('get_recommendations')
    @api.response(404, 'recommendation not found')
    @api.marshal_with(recommendation_model)
    def get(self, recommendation_id):
        """
        Retrieve a single recommendation

        This endpoint will return a Recommendation based on it's id
        """
        app.logger.info("Request to Retrieve a recommendation with id [%s]", recommendation_id)
        recommendation = Recommendation.find(recommendation_id)
        if not recommendation:
            abort(status.HTTP_404_NOT_FOUND, "Recommendation with id '{}' was not found.".format(recommendation_id))
        return recommendation.serialize(), status.HTTP_200_OK

    #------------------------------------------------------------------
    # UPDATE AN EXISTING RECOMMENDATION
    #------------------------------------------------------------------
    @api.doc('update_Recommendations')
    @api.response(404, 'Recommendation not found')
    @api.response(400, 'The posted Recommendation data was not valid')
    @api.expect(recommendation_model)
    @api.marshal_with(recommendation_model)
    def put(self, recommendation_id):
        """
        Update a Recommendation

        This endpoint will update a Recommendation based the body that is posted
        """
        app.logger.info('Request to Update a recommendation with id [%s]', recommendation_id)
        recommendation = Recommendation.find(recommendation_id)
        if not recommendation:
            abort(status.HTTP_404_NOT_FOUND, "Recommendation with id '{}' was not found.".format(recommendation_id))
        app.logger.debug('Payload = %s', api.payload)
        data = api.payload
        recommendation.deserialize(data)
        recommendation.id = recommendation_id
        recommendation.update()
        return recommendation.serialize(), status.HTTP_200_OK

    #------------------------------------------------------------------
    # DELETE A RECOMMENDATION
    #------------------------------------------------------------------
    @api.doc('delete_recommendations', security='apikey')
    @api.response(204, 'Recommendation deleted')
    def delete(self, recommendation_id):
        """
        Delete a Recommendation

        This endpoint will delete a recommendation based the id specified in the path
        """
        app.logger.info('Request to Delete a Recommendation with id [%s]', recommendation_id)
        recommendation = Recommendation.find(recommendation_id)
        if recommendation:
            recommendation.delete()
            app.logger.info('Recommendation with id [%s] was deleted', recommendation_id)

        return '', status.HTTP_204_NO_CONTENT

######################################################################
#  PATH: /recommendations
######################################################################
@api.route('/recommendations', strict_slashes=False)
class RecommendationCollection(Resource):
    """ Handles all interactions with collections of Recommendations """
    #------------------------------------------------------------------
    # LIST ALL RECOMMENDATIONS
    #------------------------------------------------------------------
    @api.doc('list_recommendations')
    @api.expect(recommendation_args, validate=True)
    @api.marshal_list_with(recommendation_model)
    def get(self):
        """ Returns all of the Recommendations """
        app.logger.info('Request to list Recommendations...')
        recommendations = []
        args = recommendation_args.parse_args()
        if args['src_product_id']:
            app.logger.info('Filtering by Source ID: %s', args['src_product_id'])
            recommendations = Recommendation.find_by_src_id(int(args['src_product_id']))
        else:
            app.logger.info('Returning unfiltered list.')
            recommendations = Recommendation.all()

        app.logger.info('[%s] Recommendations returned', len(recommendations))
        results = [recommendation.serialize() for recommendation in recommendations]
        return results, status.HTTP_200_OK


    #------------------------------------------------------------------
    # ADD A NEW RECOMMENDATION
    #------------------------------------------------------------------
    @api.doc('create_recommendations')
    @api.response(400, 'The posted data was not valid')
    @api.expect(create_model)
    @api.marshal_with(recommendation_model, code=201)
    def post(self):
        """
        Creates a Recommendation
        This endpoint will create a Recommendation based the data in the body that is posted
        """
        app.logger.info('Request to Create a Recommendation')
        recommendation = Recommendation()
        app.logger.debug('Payload = %s', api.payload)
        recommendation.deserialize(api.payload)
        recommendation.create()
        app.logger.info('Pet with new id [%s] created!', recommendation.id)
        location_url = api.url_for(RecommendationResource, recommendation_id=recommendation.id, _external=True)
        return recommendation.serialize(), status.HTTP_201_CREATED, {'Location': location_url}




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
