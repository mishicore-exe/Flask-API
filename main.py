# Rest API- tis is a backend API that follows the four rules below
# 1. It has to have a route
# 2. It has to have a method (POST/GET/PUT/DELETE)
# 3. It has to have a status code (200,201,403)
# 4. It has to return data as JSON (key: value pairs)

from flask import Flask, request, jsonify
from sqlalchemy import create_engine 
from models import Base

app = Flask (__name__)

# create a connection to the database using sqlalchemy engine
engine = create_engine("sqlite:///./flask_duka_api.db", echo=True)

# create tables into the database using sqlalchemy
Base.metadata.create_all(engine)


@app.route("/")
def home():
    if request.method == "GET":
        data = {"Flask API" : "Version 1"}
        return jsonify(data), 200
    else:
        error = {"Error" : "Method not allowed"}
        return jsonify(error), 405

app.run(debug=True)