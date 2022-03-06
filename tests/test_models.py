"""
Test cases for Recommendation Model

"""
import os
import logging
import unittest
from service.models import Recommendation, Type, DataValidationError, db
from service import app
from .factories import RecommendationFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/testdb"
)

######################################################################
#  R E C O M M E N D A T I O N   M O D E L   T E S T   C A S E S
######################################################################
class TestRecommendationModel(unittest.TestCase):
    """ Test Cases for Recomendation Model """

    @classmethod
    def setUpClass(cls):
        """ This runs once before the entire test suite """
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Recommendation.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.drop_all()  # clean up the last tests
        db.create_all()  # make our sqlalchemy tables

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()
        db.drop_all()


    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_serialize_a_recommendation(self):
        """Test serialization of a recommendation"""
        recommendation = RecommendationFactory()
        data = recommendation.serialize()
        self.assertNotEqual(data, None)
        self.assertIn("id", data)
        self.assertEqual(data["id"], recommendation.id)
        self.assertIn("src_product_id", data)
        self.assertEqual(data["src_product_id"], recommendation.src_product_id)
        self.assertIn("rec_product_id", data)
        self.assertEqual(data["rec_product_id"], recommendation.rec_product_id)
        self.assertIn("type", data)
        self.assertEqual(data["type"], recommendation.type.name)

    def test_deserialize_a_recommendation(self):
        """Test deserialization of a recommendation"""
        data = {
            "id": 1,
            "src_product_id": 21,
            "rec_product_id": 50,
            "type": "UP_SELL",
        }
        recommendation = Recommendation()
        recommendation.deserialize(data)
        self.assertNotEqual(recommendation, None)
        self.assertEqual(recommendation.id, None)
        self.assertEqual(recommendation.src_product_id, 21)
        self.assertEqual(recommendation.rec_product_id, 50)
        self.assertEqual(recommendation.type, Type.UP_SELL)

    def test_deserialize_missing_data(self):
        """Test deserialization of a recommendation with missing data"""
        data = {"id": 1, "src_product_id": 12, "rec_product_id": 99}
        recommendation = Recommendation()
        self.assertRaises(DataValidationError, recommendation.deserialize, data)

    def test_deserialize_bad_data(self):
        """Test deserialization of bad data"""
        recommendation = Recommendation()
        data = "this is not a dictionary"
        self.assertRaises(DataValidationError, recommendation.deserialize, data)
    
    def test_create_a_recommendation(self):
        """Create a Recommendation and assert that it exists"""
        recommendation = Recommendation(id=1, src_product_id=100, rec_product_id=200, type= "UP_SELL")
        self.assertIsNot(recommendation, None)
        self.assertEqual(recommendation.id, 1)
        self.assertEqual(recommendation.src_product_id, 100)
        self.assertEqual(recommendation.rec_product_id, 200)
        self.assertEqual(recommendation.type, "UP_SELL")

    def test_add_a_recommendation(self):
        """Create a Recommendation and add it to the database"""
        recommendations = Recommendation.all()
        self.assertEqual(recommendations, [])
        recommendation = Recommendation(id=1, src_product_id=100, rec_product_id=200, type= "UP_SELL")
        self.assertTrue(recommendation != None)
        self.assertEqual(recommendation.id, 1)
        recommendation.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertEqual(recommendation.id, 1)
        recommendations = Recommendation.all()
        self.assertEqual(len(recommendations), 1)
        
    def test_update_a_recommendation(self):
        """Update a item"""
        recommendation = Recommendation(id=1, name="iPhone", category="phone", price=100)
        self.assertIsNot(recommendation, None)
        self.assertEqual(recommendation.id, 1)
        recommendation.create()
        # Change it an save it
        recommendation.category = "laptop"
        original_id = recommendation.id
        recommendation.update()
        self.assertEqual(recommendation.id, original_id)
        self.assertEqual(recommendation.category, "laptop")
        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        recommendations = Recommendation.all()
        self.assertEqual(len(recommendations), 1)
        self.assertEqual(recommendations[0].id, 1)
        self.assertEqual(recommendations[0].category, "laptop")

    def test_update_a_recommendation_validation_error(self):
        """Update a item Validation Error"""
        recommendation = Recommendation(id=1, name="iPhone", category="Phone", price="100")
        self.assertRaises(DataValidationError, recommendation.update)
        recommendation = Recommendation(name="iPhone", category="Phone", price=100)
        self.assertRaises(DataValidationError, recommendation.update)
        recommendation = Recommendation(id="1", name="iPhone", category="Phone", price=100)
        self.assertRaises(DataValidationError, recommendation.update)
