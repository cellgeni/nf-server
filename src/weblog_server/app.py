import os
import http
import pymongo
from flask import Flask, request

app = Flask(__name__)

# Connect to database
MONGODB_USERNAME = os.getenv("MONGODB_USERNAME")
MONGODB_PASSWORD = os.getenv("MONGODB_PASSWORD")
MONGODB_HOST = os.getenv("MONGODB_HOST", "127.0.0.1")
MONGODB_PORT = os.getenv("MONGODB_PORT", 27017)
mongo = pymongo.MongoClient(f"mongodb://{MONGODB_USERNAME}:{MONGODB_PASSWORD}@{MONGODB_HOST}:{MONGODB_PORT}/")
db = mongo["nf-server"]

# NEXTFLOW minimum required fileds
MINIMUM_REQUIRED_FIELDS = set(["runName","runId","event","utcTime"])

@app.route("/log", methods=["POST"])
def receive_weblog():
    nextflow_message = request.get_json()
    # quick sanity check for minimum fields
    if MINIMUM_REQUIRED_FIELDS <= set(nextflow_message.keys()):        
        # store in mongodb
        db.logs.insert_one(nextflow_message)
        return "OK", http.HTTPStatus.OK
    else:
        return "Not valid nexflow message", http.HTTPStatus.BAD_REQUEST

if __name__ == "__main__":
    app.run(host= "127.0.0.1", port=9999, debug=True)

