"""
Models for Recommendations

All of the models are stored in this module
"""
import logging
from enum import Enum
from flask_sqlalchemy import SQLAlchemy
from flask import Flask

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """

    pass

class Type(Enum):
    """Enumeration of valid Recommendation Types"""

    CROSS_SELL = 0
    UP_SELL = 1
    ACCESSORY = 2


class Recommendation(db.Model):
    """
    Class that represents a Recommendation
    """

    app = None

    # Table Schema
    id = db.Column(db.Integer, primary_key=True) # recommendation id
    src_product_id = db.Column(db.Integer, nullable=False) # source product id
    rec_product_id = db.Column(db.Integer, nullable=False) # recommended product id
    type = db.Column( # recommendation type
        db.Enum(Type), nullable=False, server_default=(Type.CROSS_SELL.name)
    )

    def __repr__(self):
        return "<Recommendation id=[%s], src_product_id=[%s], rec_product_id=[%s], type=[%s]>" % \
            (self.id, self.src_product_id, self.rec_product_id, self.type.name)

    def create(self):
        """
        Creates a Recommendation to the database
        """
        # logger.info("Creating %d", self.id)
        self.id = None  # id must be none to generate next primary key
        db.session.add(self)
        db.session.commit()

    def serialize(self) -> dict:
        """Serializes a Recommendation into a dictionary"""
        return {
            "id": self.id,
            "src_product_id": self.src_product_id,
            "rec_product_id": self.rec_product_id,
            "type": self.type.name, # convert enum to string
        }

    def deserialize(self, data: dict):
        """
        Deserializes a Recommendation from a dictionary
        Args:
            data (dict): A dictionary containing the Recommendation data
        """
        try:
            if isinstance(data["src_product_id"], int):
                self.src_product_id = data["src_product_id"]
            else:
                raise DataValidationError(
                    "Invalid type for int [src_product_id]: "
                    + str(type(data["src_product_id"]))
                )
            if isinstance(data["rec_product_id"], int):
                self.rec_product_id = data["rec_product_id"]
            else:
                raise DataValidationError(
                    "Invalid type for int [rec_product_id]: "
                    + str(type(data["rec_product_id"]))
                )
            self.type = getattr(Type, data["type"])  # create enum from string
        except AttributeError as error:
            raise DataValidationError("Invalid attribute: " + error.args[0])
        except KeyError as error:
            raise DataValidationError("Invalid recommendation: missing " + error.args[0])
        except TypeError as error:
            raise DataValidationError(
                "Invalid recommendation: body of request contained bad or no data " + str(error)
            )
        return self

    @classmethod
    def find(cls, id: int):
        """Finds a Recommendation by it's ID

        :param id: the id of the Recommendation to find
        :type id: int

        :return: an instance with the id, or None if not found
        :rtype: Recommendation

        """
        logger.info("Processing lookup for id %s ...", id)
        return cls.query.get(id)

    @classmethod
    def find_or_404(cls, id: int):
        """Find a Recommendation by it's id

        :param id: the id of the Recommendation to find
        :type id: int

        :return: an instance with the id, or 404_NOT_FOUND if not found
        :rtype: Recommendation

        """
        logger.info("Processing lookup or 404 for id %s ...", id)
        return cls.query.get_or_404(id)

    @classmethod
    def init_db(cls, app: Flask):
        """Initializes the database session
        :param app: the Flask app
        :type data: Flask
        """
        logger.info("Initializing database")
        # This is where we initialize SQLAlchemy from the Flask app
        db.init_app(app)
        app.app_context().push()
        db.create_all()  # make our sqlalchemy tables
        
    def all(cls) -> list:
        """ Returns all of the Products in the database """
        logger.info("Processing all Products")
        return cls.query.all()
