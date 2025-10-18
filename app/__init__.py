from flask import Flask

def create_app():
    app = Flask(__name__)

    # In-memory “database” (Module 6 pattern: simple Python list/dicts)
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
    return app
