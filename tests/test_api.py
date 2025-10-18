import pytest
from app.app import app as flask_app

@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as client:
        yield client

def test_get_inventory(client):
    response = client.get("/inventory")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert "product_name" in data[0]

def test_get_inventory_item_found(client):
    response = client.get("/inventory/1")
    assert response.status_code == 200
    data = response.get_json()
    assert data["id"] == 1

def test_get_inventory_item_not_found(client):
    response = client.get("/inventory/999")
    assert response.status_code == 404
    assert response.get_json()["error"] == "Item not found"

def test_create_inventory_item(client):
    new_item = {
        "product_name": "Test Product",
        "price": 9.99,
        "stock": 5
    }
    response = client.post("/inventory", json=new_item)
    assert response.status_code == 201
    data = response.get_json()
    assert data["product_name"] == "Test Product"

def test_create_inventory_item_validation(client):
    response = client.post("/inventory", json={})
    assert response.status_code == 400
    assert "error" in response.get_json()

def test_update_inventory_item(client):
    patch_data = {"stock": 99}
    response = client.patch("/inventory/1", json=patch_data)
    assert response.status_code == 200
    data = response.get_json()
    assert data["stock"] == 99

def test_delete_inventory_item(client):
    response = client.delete("/inventory/1")
    assert response.status_code == 204