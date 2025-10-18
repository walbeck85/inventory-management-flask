import pytest
from app.app import app as flask_app
from unittest.mock import patch

@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as client:
        yield client

@patch("app.app.requests.get")
def test_import_from_barcode_creates_item(mock_get, client):
    mock_get.return_value.json.return_value = {
        "status": 1,
        "product": {
            "product_name": "Organic Almond Milk",
            "brands": "Silk",
            "ingredients_text": "Filtered water, almonds..."
        }
    }
    resp = client.post("/inventory/import", json={"barcode": "0123456789012", "price": 5.49, "stock": 12})
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["product_name"] == "Organic Almond Milk"
    assert data["stock"] == 12

def test_import_from_barcode_missing_body(client):
    resp = client.post("/inventory/import", json={})
    assert resp.status_code == 400