import boto3
import json
import logging
from collections import defaultdict

# create a DynamoDB client using boto3. The boto3 library will automatically
# use the credentials associated with our ECS task role to communicate with
# DynamoDB, so no credentials need to be stored/managed at all by our code!
client = boto3.client('dynamodb')

def getAllTisits():

    # Retrieve all Mysfits from DynamoDB using the DynamoDB scan operation.
    # Note: The scan API can be expensive in terms of latency when a DynamoDB
    # table contains a high number of records and filters are applied to the
    # operation that require a large amount of data to be scanned in the table
    # before a response is returned by DynamoDB. For high-volume tables that
    # receive many requests, it is common to store the result of frequent/common
    # scan operations in an in-memory cache. DynamoDB Accelerator (DAX) or
    # use of ElastiCache can provide these benefits. But, because out Mythical
    # Mysfits API is low traffic and the table is very small, the scan operation
    # will suit our needs for this workshop.
    response = client.scan(
        TableName='tisitTable'
    )

    logging.info(response["Items"])

    # loop through the returned tisits and add their attributes to a new dict
    # that matches the JSON response structure expected by the frontend.
    tisitList = defaultdict(list)
    for item in response["Items"]:
        tisit = {}
        tisit["mysfitId"] = item["MysfitId"]["S"]
        tisit["name"] = item["Name"]["S"]
        tisit["goodevil"] = item["GoodEvil"]["S"]
        tisit["lawchaos"] = item["LawChaos"]["S"]
        tisit["species"] = item["Species"]["S"]
        tisit["thumbImageUri"] = item["ThumbImageUri"]["S"]
        tisitList["tisits"].append(tisit)

    # convert the create list of dicts in to JSON
    return json.dumps(tisitList)

def queryTisits(queryParam):

    logging.info(json.dumps(queryParam))

    # Use the DynamoDB API Query to retrieve tisits from the table that are
    # equal to the selected filter values.
    response = client.query(
        TableName='tisitTable',
        IndexName=queryParam['filter']+'Index',
        KeyConditions={
            queryParam['filter']: {
                'AttributeValueList': [
                    {
                        'S': queryParam['value']
                    }
                ],
                'ComparisonOperator': "EQ"
            }
        }
    )

    tisitList = defaultdict(list)
    for item in response["Items"]:
        tisit = {}
        tisit["mysfitId"] = item["MysfitId"]["S"]
        tisit["name"] = item["Name"]["S"]
        tisit["goodevil"] = item["GoodEvil"]["S"]
        tisit["lawchaos"] = item["LawChaos"]["S"]
        tisit["species"] = item["Species"]["S"]
        tisit["thumbImageUri"] = item["ThumbImageUri"]["S"]
        tisitList["tisits"].append(tisit)

    return json.dumps(tisitList)

# Retrive a single tisit from DynamoDB using their unique mysfitId
def getTisit(mysfitId):

    # use the DynamoDB API GetItem, which gives you the ability to retrieve
    # a single item from a DynamoDB table using its unique key with super
    # low latency.
    response = client.get_item(
        TableName='tisitTable',
        Key={
            'MysfitId': {
                'S': mysfitId
            }
        }
    )

    item = response["Item"]

    tisit = {}
    tisit["mysfitId"] = item["MysfitId"]["S"]
    tisit["name"] = item["Name"]["S"]
    tisit["age"] = int(item["Age"]["N"])
    tisit["goodevil"] = item["GoodEvil"]["S"]
    tisit["lawchaos"] = item["LawChaos"]["S"]   
    tisit["species"] = item["Species"]["S"]
    tisit["description"] = item["Description"]["S"]
    tisit["thumbImageUri"] = item["ThumbImageUri"]["S"]
    tisit["profileImageUri"] = item["ProfileImageUri"]["S"]
    tisit["likes"] = item["Likes"]["N"]
    tisit["adopted"] = item["Adopted"]["BOOL"]

    return json.dumps(tisit)

# increment the number of likes for a tisit by 1
def likeTisit(mysfitId):

    # Use the DynamoDB API UpdateItem to increment the number of Likes
    # the tisit has by 1 using an UpdateExpression.
    response = client.update_item(
        TableName='tisitTable',
        Key={
            'MysfitId': {
                'S': mysfitId
            }
        },
        UpdateExpression="SET Likes = Likes + :n",
        ExpressionAttributeValues={':n': {'N': '1'}}
    )

    response = {}
    response["Update"] = "Success";

    return json.dumps(response)

# mark a tisit as adopted
def adoptTisit(mysfitId):

    # Use the DynamoDB API UpdateItem to set the value of the tisit's
    # Adopted attribute to True using an UpdateExpression.
    response = client.update_item(
        TableName='tisitTable',
        Key={
            'MysfitId': {
                'S': mysfitId
            }
        },
        UpdateExpression="SET Adopted = :b",
        ExpressionAttributeValues={':b': {'BOOL': True}}
    )

    response = {}
    response["Update"] = "Success";

    return json.dumps(response)
