from flask import jsonify, request
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

if __name__ == "__main__":
    app.run(debug=True)
