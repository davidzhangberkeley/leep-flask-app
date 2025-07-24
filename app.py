import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from agent import vertexApp

import base64
import os


stored_data = {}
stored_session = ""

app = Flask(__name__)
CORS(app)

# Write the credentials JSON file on startup
if os.environ.get("GOOGLE_CREDENTIALS_BASE64"):
    with open("/app/credentials.json", "wb") as f:
        f.write(base64.b64decode(os.environ["GOOGLE_CREDENTIALS_BASE64"]))


@app.route("/")
def home():
    return "hello"


@app.route("/createWorkflow", methods=["POST"])
def upload():
    global stored_data
    if request.is_json:
        stored_data = request.get_json()
        return jsonify({"message": "Data received and stored."}), 200
    else:
        return jsonify({"error": "Request must be JSON"}), 400


@app.route("/createSession", methods=["POST"])
def create_session():
    global stored_session
    if request.is_json:
        user_id = request.get_json()["user_id"]
        print("IMPORTANT SUPER IMPORTANT" + user_id)
        stored_session = vertexApp.create_session(user_id=user_id).id
        return jsonify({"message": "Data received and stored."}), 200
    else:
        return jsonify({"error": "Request must be JSON"}), 400


@app.route("/getSession", methods=["GET"])
def get_session():
    global stored_session
    old_session = stored_session
    stored_session = ""
    return jsonify({"id": old_session}), 200


@app.route("/getWorkflow", methods=["GET"])
def get_data():
    global stored_data
    if stored_data:
        session_id = stored_data["session_id"]
        user_id = stored_data["user_id"]
        message = stored_data["message"]
        workflow = {}
        for event in vertexApp.stream_query(
            user_id=user_id,
            session_id=session_id,
            message=message,
        ):
            workflow = event
        stored_data = {}
        return jsonify({"err": 0, "workflow": workflow}), 200
    else:
        return jsonify({"err": 1, "workflow": ""}), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
