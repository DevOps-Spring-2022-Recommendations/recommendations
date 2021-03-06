"""
TestYourResourceModel API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
import os
import logging
from unittest import TestCase
from service.utils import status  # HTTP Status Codes
from service.models import db
from service.routes import app, init_db
from .factories import RecommendationFactory

# DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///../db/test.db')
DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/testdb"
)
BASE_URL = "/recommendations"
CONTENT_TYPE_JSON = "application/json"
BASE_API="/api/recommendations"
######################################################################
#  T E S T   C A S E S
######################################################################
class TestRecommendationServer(TestCase):
    """ REST API Server Tests """

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        init_db()

    @classmethod
    def tearDownClass(cls):
        """Run once after all tests"""
        db.session.close()

    def setUp(self):
        """Runs before each test"""
        db.drop_all()  # clean up the last tests
        db.create_all()  # create new tables
        self.app = app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def _create_recommendations(self, count):
        """Factory method to create items in bulk"""
        recommendations = []
        for _ in range(count):
            test_recommendation = RecommendationFactory()
            resp = self.app.post(
                BASE_URL, json=test_recommendation.serialize(), content_type=CONTENT_TYPE_JSON
            )
            self.assertEqual(
                resp.status_code, status.HTTP_201_CREATED, "Could not create test recommendation"
            )
            new_recommendation = resp.get_json()
            test_recommendation.id = new_recommendation["id"]
            recommendations.append(test_recommendation)
        return recommendations
    def _create_recommendations_API(self, count):
        """Factory method to create items in bulk"""
        recommendations = []
        for _ in range(count):
            test_recommendation = RecommendationFactory()
            resp = self.app.post(
                BASE_API, json=test_recommendation.serialize(), content_type=CONTENT_TYPE_JSON
            )
            self.assertEqual(
                resp.status_code, status.HTTP_201_CREATED, "Could not create test recommendation"
            )
            new_recommendation = resp.get_json()
            test_recommendation.id = new_recommendation["id"]
            recommendations.append(test_recommendation)
        return recommendations

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """Test the Home Page"""
        resp = self.app.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_create_recommendation(self):
        """Create a new recommendation"""
        test_recommendation = RecommendationFactory()
        logging.debug(test_recommendation)
        resp = self.app.post(
            BASE_URL, json=test_recommendation.serialize(), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # Make sure location header is set
        location = resp.headers.get("Location", None)
        self.assertIsNotNone(location)
        # Check the data is correct
        new_recommendation = resp.get_json()
        logging.debug(new_recommendation)
        self.assertEqual(
            new_recommendation["src_product_id"], test_recommendation.src_product_id, "Source Product ID do not match"
        )
        self.assertEqual(
            new_recommendation["rec_product_id"], test_recommendation.rec_product_id, "Recommended Product ID do not match"
        )
        self.assertEqual(
            new_recommendation["type"], test_recommendation.type.name, "Type do not match"
        )
        # Check that the location header was correct
        resp = self.app.get(location, content_type=CONTENT_TYPE_JSON)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_recommendation = resp.get_json()
        self.assertEqual(
            new_recommendation["src_product_id"], test_recommendation.src_product_id, "Source Product ID do not match"
        )
        self.assertEqual(
            new_recommendation["rec_product_id"], test_recommendation.rec_product_id, "Recommended Product ID do not match"
        )
        self.assertEqual(
            new_recommendation["type"], test_recommendation.type.name, "Type do not match"
        )

    def test_create_recommendation_no_data(self):
        """Create a recommendation with missing data"""
        resp = self.app.post(BASE_URL, json={}, content_type=CONTENT_TYPE_JSON)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_recommendation_no_content_type(self):
        """Create a recommendation with no content type"""
        resp = self.app.post(BASE_URL)
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_update_recommendation(self):
        """Update an existing recommendation"""
        # create a recommendation to update
        test_recommendation = RecommendationFactory()
        resp = self.app.post(
            BASE_URL, json=test_recommendation.serialize(), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # update the recommendation
        new_recommendation = resp.get_json()
        logging.debug(new_recommendation)
        new_recommendation["src_product_id"] = 55
        resp = self.app.put(
            "/recommendations/{}".format(new_recommendation["id"]),
            json=new_recommendation,
            content_type=CONTENT_TYPE_JSON,
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_recommendation = resp.get_json()
        self.assertEqual(updated_recommendation["src_product_id"], 55)

    def test_delete_recommendation(self):
        """Delete a recommendation"""
        test_recommendation = self._create_recommendations(1)[0]
        resp = self.app.delete(
            "{0}/{1}".format(BASE_URL, test_recommendation.id), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(resp.data), 0)
        # make sure they are deleted
        resp = self.app.get(
            "{0}/{1}".format(BASE_URL, test_recommendation.id), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_recommendations_list(self):
        """Get a list of recommendations"""
        self._create_recommendations(5)
        resp = self.app.get(BASE_URL)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(len(resp.data) > 0)

    def test_enable_recommendations(self):
        """Enable a recommendation"""
        # test recommendation not found
        resp = self.app.put("/recommendations/1/enable",
            json=None,
            content_type=CONTENT_TYPE_JSON,
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

        # create a recommendation to test
        test_recommendation = RecommendationFactory()
        resp = self.app.post(
            BASE_URL, json=test_recommendation.serialize(), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        recommendation = resp.get_json()
        logging.debug(recommendation)
        resp = self.app.put("/recommendations/{}/enable".format(recommendation["id"]),
            json=recommendation,
            content_type=CONTENT_TYPE_JSON,
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        enabled = resp.get_json()
        self.assertEqual(enabled["status"], "ENABLED")

    def test_disable_recommendation(self):
        """Disable a recommendation"""
        # test recommendation not found
        resp = self.app.put("/recommendations/1/disable",
            json=None,
            content_type=CONTENT_TYPE_JSON,
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

        # create a recommendation to test
        test_recommendation = RecommendationFactory()
        resp = self.app.post(
            BASE_URL, json=test_recommendation.serialize(), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        recommendation = resp.get_json()
        logging.debug(recommendation)
        resp = self.app.put("/recommendations/{}/disable".format(recommendation["id"]),
            json=recommendation,
            content_type=CONTENT_TYPE_JSON,
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        disabled = resp.get_json()
        self.assertEqual(disabled["status"], "DISABLED")

    def test_query_by_src_product_id(self):
        """Query Recommendations by Source ID"""
        recommendations = self._create_recommendations(10)
        test_source_id = recommendations[0].src_product_id
        source_id_recommendations = [recommendation for recommendation in recommendations
            if recommendation.src_product_id == test_source_id]
        resp = self.app.get(
            BASE_URL, query_string="src_product_id={}".format(test_source_id)
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), len(source_id_recommendations))
        # check the data just to be sure
        for recommendation in data:
            self.assertEqual(recommendation["src_product_id"], test_source_id)

    def test_query_by_rec_product_id(self):
        """Query Recommendations by Recommendation Product ID"""
        recommendations = self._create_recommendations(10)
        test_rec_id = recommendations[0].rec_product_id
        rec_id_recommendations = [recommendation for recommendation in recommendations
            if recommendation.rec_product_id == test_rec_id]
        resp = self.app.get(
            BASE_URL, query_string="rec_product_id={}".format(test_rec_id)
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), len(rec_id_recommendations))
        # check the data just to be sure
        for recommendation in data:
            self.assertEqual(recommendation["rec_product_id"], test_rec_id)

    def test_query_by_type(self):
        """Query Recommendations by Type"""
        recommendations = self._create_recommendations(5)
        test_type = recommendations[0].type
        test_source_id = recommendations[0].src_product_id
        type_count = len([recommendation for recommendation in recommendations
            if recommendation.type == test_type])
        resp = self.app.get(
            BASE_URL, query_string="type={}".format(test_type.name)
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), type_count)

    def get_rec(self):
        """ retrieves a Recommendation for use in other actions """
        recommendations = self._create_recommendations(10)
        test_source_id = recommendations[0].id
        resp = self.app.get(BASE_URL,
                            query_string="id={}".format(test_source_id))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertGreater(len(resp.data), 0)
        data = resp.get_json()
        logging.debug('get_pet(data) = %s', data)
        return data

    def test_update_api(self):
        """ Update a recommandation """
        pet = self.get_rec()[0] # returns a list
        self.assertEqual(pet['id'], 1)
        pet['rec_product_id'] = 595
        id=pet['id']
        # make the call
        pet_id = pet['id']
        resp = self.app.put(f'{BASE_API}/{id}', json=pet,
                            
            content_type=CONTENT_TYPE_JSON)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_get_recommendations_list_API(self):
        """Get a list of recommendations"""
        self._create_recommendations(5)
        resp = self.app.get(BASE_API)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 5)

    def test_delete_recommendation_api(self):
        """Delete a recommendation"""
        test_recommendation = self._create_recommendations_API(1)[0]
        resp = self.app.delete(
            "{0}/{1}".format(BASE_API, test_recommendation.id), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(resp.data), 0)
        # make sure they are deleted
        resp = self.app.get(
            "{0}/{1}".format(BASE_API, test_recommendation.id), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_query_recommendations_by_source_API(self):
        """Query Recommendations by Source ID"""
        recommendations = self._create_recommendations(10)
        test_source_id = recommendations[0].src_product_id
        source_id_recos = [reco for reco in recommendations if reco.src_product_id == test_source_id]
        resp = self.app.get(
            BASE_API, query_string="src_product_id={}".format(test_source_id)
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), len(source_id_recos))
        # check the data just to be sure
        for reco in data:
            self.assertEqual(reco["src_product_id"], test_source_id)

    def test_enable_recommendations_API(self):
        """Enable a recommendation"""
        # test recommendation not found
        resp = self.app.put("/recommendations/1/enable",
            json=None,
            content_type=CONTENT_TYPE_JSON,
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

        # create a recommendation to test
        test_recommendation = RecommendationFactory()
        resp = self.app.post(
            BASE_API, json=test_recommendation.serialize(), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        recommendation = resp.get_json()
        logging.debug(recommendation)
        resp = self.app.put("/recommendations/{}/enable".format(recommendation["id"]),
            json=recommendation,
            content_type=CONTENT_TYPE_JSON,
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        enabled = resp.get_json()
        self.assertEqual(enabled["status"], "ENABLED")

