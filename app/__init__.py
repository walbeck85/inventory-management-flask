"""
App factory and in-memory storage for the Inventory Management System.

I am using a simple Python list to act as my data store instead of a full
database. This keeps the app easy to test and focused on the API logic itself.
"""

from flask import Flask

def create_app():
    """
    Create and configure a Flask application instance.

    I am defining this as a factory so I can easily reuse it in tests or
    extensions later. The app holds an in-memory list of inventory items.
    """
    app = Flask(__name__)

    # Seed the app with one default item so I always have data
    # to test read, update, and delete operations without setup.
    app.config["INVENTORY"] = [
        {
            "id": 1,
            "barcode": "0000000000000",
            "product_name": "Sample Product",
            "brands": "Acme",
            "ingredients_text": "water, salt",
            "price": 3.99,
            "stock": 10
        }
    ]

    # Return the ready-to-use Flask instance.
    return app
