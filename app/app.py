from flask import jsonify, request
from . import create_app

app = create_app()

@app.route("/", methods=["GET"])
def root():
    # Module 6 pattern: simple JSON welcome
    return jsonify({"message": "Inventory API ready"}), 200

if __name__ == "__main__":
    app.run(debug=True)
