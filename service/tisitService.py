from flask import Flask, jsonify, json, Response, request
from flask_cors import CORS
import tisitTableClient

app = Flask(__name__)
CORS(app)

# The service basepath has a short response just to ensure that healthchecks
# sent to the service root will receive a healthy response.
@app.route("/")
def healthCheckResponse():
    return jsonify({"message" : "Nothing here, used for health check. Try /tisits instead."})

# Retrive tisits from DynamoDB based on provided querystring params, or all
# tisits if no querystring is present.
@app.route("/tisits", methods=['GET'])
def getTisits():

    filterCategory = request.args.get('filter')
    if filterCategory:
        filterValue = request.args.get('value')
        queryParam = {
            'filter': filterCategory,
            'value': filterValue
        }
        serviceResponse = tisitTableClient.queryTisits(queryParam)
    else:
        serviceResponse = tisitTableClient.getAllTisits()

    flaskResponse = Response(serviceResponse)
    flaskResponse.headers["Content-Type"] = "application/json"

    return flaskResponse

# retrieve the full details for a specific mysfit with their provided path
# parameter as their ID.
@app.route("/tisits/<mysfitId>", methods=['GET'])
def getTisit(mysfitId):
    serviceResponse = tisitTableClient.getTisit(mysfitId)

    flaskResponse = Response(serviceResponse)
    flaskResponse.headers["Content-Type"] = "application/json"

    return flaskResponse

# increment the number of likes for the provided mysfit.
@app.route("/tisits/<mysfitId>/like", methods=['POST'])
def likeTisit(mysfitId):
    serviceResponse = tisitTableClient.likeTisit(mysfitId)

    flaskResponse = Response(serviceResponse)
    flaskResponse.headers["Content-Type"] = "application/json"

    return flaskResponse

# indicate that the provided mysfit should be marked as adopted.
@app.route("/tisits/<mysfitId>/adopt", methods=['POST'])
def adoptTisit(mysfitId):
    serviceResponse = tisitTableClient.adoptTisit(mysfitId)

    flaskResponse = Response(serviceResponse)
    flaskResponse.headers["Content-Type"] = "application/json"

    return flaskResponse

# Run the service on the local server it has been deployed to,
# listening on port 8080.
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
