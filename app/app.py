from flask import jsonify, request
import requests
from . import create_app

app = create_app()

def _next_id(items):
    return max((i["id"] for i in items), default=0) + 1

def _find_by_id(items, item_id):
    return next((i for i in items if i["id"] == item_id), None)

@app.route("/", methods=["GET"])
def root():
    return jsonify({"message": "Inventory API ready"}), 200

# GET /inventory -> list all items
@app.route("/inventory", methods=["GET"])
def list_inventory():
    items = app.config["INVENTORY"]
    return jsonify(items), 200

# GET /inventory/<int:item_id> -> get one item
@app.route("/inventory/<int:item_id>", methods=["GET"])
def get_inventory_item(item_id):
    items = app.config["INVENTORY"]
    item = _find_by_id(items, item_id)
    if not item:
        return jsonify({"error": "Item not found"}), 404
    return jsonify(item), 200

# POST /inventory -> create a new item
@app.route("/inventory", methods=["POST"])
def create_inventory_item():
    items = app.config["INVENTORY"]
    data = request.get_json() or {}

    # minimal validation per Course 8 style: require product_name
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
    items = app.config["INVENTORY"]
    item = _find_by_id(items, item_id)
    if not item:
        return jsonify({"error": "Item not found"}), 404

    data = request.get_json() or {}

    for field in ["barcode", "product_name", "brands", "ingredients_text"]:
        if field in data:
            item[field] = str(data[field]) if data[field] is not None else ""

    if "price" in data:
        item["price"] = float(data["price"])
    if "stock" in data:
        item["stock"] = int(data["stock"])

    return jsonify(item), 200

# DELETE /inventory/<int:item_id> -> delete an item
@app.route("/inventory/<int:item_id>", methods=["DELETE"])
def delete_inventory_item(item_id):
    items = app.config["INVENTORY"]
    item = _find_by_id(items, item_id)
    if not item:
        return jsonify({"error": "Item not found"}), 404

    app.config["INVENTORY"] = [i for i in items if i["id"] != item_id]
    return ("", 204)

# GET /inventory/search?barcode=... -> fetch product data from OpenFoodFacts
@app.route("/inventory/search", methods=["GET"])
def search_product():
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
        return jsonify({"error": f"Failed to fetch product data: {str(e)}"}), 500

# POST /inventory/import -> fetch from OpenFoodFacts and add to local array
@app.route("/inventory/import", methods=["POST"])
def import_from_barcode():
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
            # allow caller to set price/stock when importing
            "price": float(payload.get("price", 0)),
            "stock": int(payload.get("stock", 0)),
        }
        items.append(new_item)
        return jsonify(new_item), 201
    except requests.RequestException as e:
        return jsonify({"error": f"Failed to fetch product data: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)
