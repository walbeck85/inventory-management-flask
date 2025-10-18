"""Flask routes for the Inventory Management System.

Design notes:
- I keep state in memory (a simple list of dicts) so I can focus on the API
  surface and responses without introducing a real database yet.
- Endpoints return explicit JSON and status codes.
- PATCH supports partial updates so I can tweak one field at a time.
- Two helper endpoints use OpenFoodFacts: `/inventory/search` just looks up data,
  while `/inventory/import` persists a looked‑up item into the in‑memory list.
"""

from flask import jsonify, request
import requests  # external product lookups
from . import create_app

# Create a single app instance for this module so tests and the dev server
# import the same object.
app = create_app()


def _next_id(items):
    """Return the next integer id based on the current max in the list."""
    return max((i["id"] for i in items), default=0) + 1


def _find_by_id(items, item_id):
    """Return the first item matching the id, or None if not found."""
    return next((i for i in items if i["id"] == item_id), None)


@app.route("/", methods=["GET"])
def root():
    """Lightweight healthcheck so I can confirm the server is up."""
    return jsonify({"message": "Inventory API ready"}), 200


# GET /inventory -> list all items
@app.route("/inventory", methods=["GET"])
def list_inventory():
    """Return every item currently stored in the in‑memory inventory."""
    items = app.config["INVENTORY"]
    return jsonify(items), 200


# GET /inventory/<int:item_id> -> get one item
@app.route("/inventory/<int:item_id>", methods=["GET"])
def get_inventory_item(item_id):
    """Return a single item by id, or a 404 JSON error when it isn’t present."""
    items = app.config["INVENTORY"]
    item = _find_by_id(items, item_id)
    if not item:
        return jsonify({"error": "Item not found"}), 404
    return jsonify(item), 200


# POST /inventory -> create a new item
@app.route("/inventory", methods=["POST"])
def create_inventory_item():
    """
    Create a new item.

    I require `product_name` and default optional numeric fields to 0 so the
    payload stays simple for quick testing. Additional fields are accepted and
    stored as strings to keep types predictable.
    """
    items = app.config["INVENTORY"]
    data = request.get_json() or {}

    # Minimal validation: I need at least a name to add something meaningful.
    name = str(data.get("product_name", "")).strip()
    if not name:
        return jsonify({"error": "Missing 'product_name'"}), 400

    new_item = {
        "id": _next_id(items),
        "barcode": str(data.get("barcode", "")),
        "product_name": name,
        "brands": str(data.get("brands", "")),
        "ingredients_text": str(data.get("ingredients_text", "")),
        "price": float(data.get("price", 0)),
        "stock": int(data.get("stock", 0)),
    }
    items.append(new_item)
    return jsonify(new_item), 201


# PATCH /inventory/<int:item_id> -> update fields on an item
@app.route("/inventory/<int:item_id>", methods=["PATCH"])
def update_inventory_item(item_id):
    """
    Partially update an existing item.

    Only fields provided in the request are changed; everything else stays the
    same. This makes quick edits easy without resending the whole object.
    """
    items = app.config["INVENTORY"]
    item = _find_by_id(items, item_id)
    if not item:
        return jsonify({"error": "Item not found"}), 404

    data = request.get_json() or {}

    # Update string fields first; treat None as empty string.
    for field in ["barcode", "product_name", "brands", "ingredients_text"]:
        if field in data:
            item[field] = str(data[field]) if data[field] is not None else ""

    # Normalize numeric fields safely.
    if "price" in data:
        item["price"] = float(data["price"])
    if "stock" in data:
        item["stock"] = int(data["stock"])

    return jsonify(item), 200


# DELETE /inventory/<int:item_id> -> delete an item
@app.route("/inventory/<int:item_id>", methods=["DELETE"])
def delete_inventory_item(item_id):
    """Delete an item by id and return 204 No Content on success."""
    items = app.config["INVENTORY"]
    item = _find_by_id(items, item_id)
    if not item:
        return jsonify({"error": "Item not found"}), 404

    app.config["INVENTORY"] = [i for i in items if i["id"] != item_id]
    return ("", 204)


# GET /inventory/search?barcode=... -> fetch product data from OpenFoodFacts
@app.route("/inventory/search", methods=["GET"])
def search_product():
    """
    Look up product details by barcode using OpenFoodFacts.

    This endpoint is read‑only: it returns a simplified subset of fields that I
    actually use in this project and does not modify local state.
    """
    barcode = request.args.get("barcode")
    if not barcode:
        return jsonify({"error": "Missing 'barcode' parameter"}), 400

    url = f"https://world.openfoodfacts.net/api/v2/product/{barcode}.json"
    try:
        resp = requests.get(url, timeout=5)
        data = resp.json()
        if data.get("status") != 1:
            return jsonify({"error": "Product not found"}), 404

        product = data["product"]
        result = {
            "barcode": barcode,
            "product_name": product.get("product_name", "Unknown Product"),
            "brands": product.get("brands", "Unknown Brand"),
            "ingredients_text": product.get("ingredients_text", "N/A"),
        }
        return jsonify(result), 200
    except requests.RequestException as e:
        # Surface a friendly error when the network call fails.
        return jsonify({"error": f"Failed to fetch product data: {str(e)}"}), 500


# POST /inventory/import -> fetch from OpenFoodFacts and add to local array
@app.route("/inventory/import", methods=["POST"])
def import_from_barcode():
    """
    Import an item by barcode from OpenFoodFacts and add it to the inventory.

    The request body may include optional `price` and `stock` so new items can
    be created with sensible defaults in one call.
    """
    payload = request.get_json() or {}
    barcode = str(payload.get("barcode", "")).strip()
    if not barcode:
        return jsonify({"error": "Missing 'barcode' in body"}), 400

    url = f"https://world.openfoodfacts.net/api/v2/product/{barcode}.json"
    try:
        resp = requests.get(url, timeout=5)
        data = resp.json()
        if data.get("status") != 1:
            return jsonify({"error": "Product not found"}), 404

        product = data["product"]
        items = app.config["INVENTORY"]
        new_item = {
            "id": _next_id(items),
            "barcode": barcode,
            "product_name": product.get("product_name", "Unknown Product"),
            "brands": product.get("brands", "Unknown Brand"),
            "ingredients_text": product.get("ingredients_text", "N/A"),
            # Allow caller to set price/stock when importing.
            "price": float(payload.get("price", 0)),
            "stock": int(payload.get("stock", 0)),
        }
        items.append(new_item)
        return jsonify(new_item), 201
    except requests.RequestException as e:
        return jsonify({"error": f"Failed to fetch product data: {str(e)}"}), 500


if __name__ == "__main__":
    # Debug server entry point for local development.
    app.run(debug=True)
