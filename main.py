# Rest API- tis is a backend API that follows the four rules below
# 1. It has to have a route
# 2. It has to have a method (POST/GET/PUT/DELETE)
# 3. It has to have a status code (200,201,403)
# 4. It has to return data as JSON (key: value pairs)

from flask import Flask, request, jsonify

app = Flask (__name__)

@app.route("/")
def home():
    if request.method == "GET":
        data = {"Flask API" : "Version 1"}
        return jsonify(data), 200
    else:
        error = {"Error" : "Method not allowed"}
        return jsonify(error), 403

app.run(debug=True)