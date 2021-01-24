import boto3
import json
import logging
from collections import defaultdict
import argparse

# create a DynamoDB client using boto3. The boto3 library will automatically
# use the credentials associated with our ECS task role to communicate with
# DynamoDB, so no credentials need to be stored/managed at all by our code!
client = boto3.client('dynamodb')

def getTisitsJson(items):
    # loop through the returned tisits and add their attributes to a new dict
    # that matches the JSON response structure expected by the frontend.
    tisitList = defaultdict(list)

    for item in items:
        tisit = {}

        tisit["TisitID"] = item["TisitID"]["S"]
        tisit["name"] = item["Name"]["S"]
        tisit["species"] = item["Species"]["S"]
        tisit["description"] = item["Description"]["S"]
        tisit["age"] = int(item["Age"]["N"])
        tisit["goodevil"] = item["GoodEvil"]["S"]
        tisit["lawchaos"] = item["LawChaos"]["S"]
        tisit["thumbImageUri"] = item["ThumbImageUri"]["S"]
        tisit["profileImageUri"] = item["ProfileImageUri"]["S"]
        tisit["likes"] = item["Likes"]["N"]
        tisit["adopted"] = item["Adopted"]["BOOL"]

        tisitList["tisits"].append(tisit)

    return tisitList

def getAllTisits():
    # Retrieve all Tisits from DynamoDB using the DynamoDB scan operation.
    # Note: The scan API can be expensive in terms of latency when a DynamoDB
    # table contains a high number of records and filters are applied to the
    # operation that require a large amount of data to be scanned in the table
    # before a response is returned by DynamoDB. For high-volume tables that
    # receive many requests, it is common to store the result of frequent/common
    # scan operations in an in-memory cache. DynamoDB Accelerator (DAX) or
    # use of ElastiCache can provide these benefits. But, because out Mythical
    # Tisits API is low traffic and the table is very small, the scan operation
    # will suit our needs for this workshop.
    response = client.scan(
        TableName='tisitTable'
    )

    logging.info(response["Items"])

    # loop through the returned tisits and add their attributes to a new dict
    # that matches the JSON response structure expected by the frontend.
    tisitList = getTisitsJson(response["Items"])

    return json.dumps(tisitList)

def queryTisitItems(filter, value):
    # Use the DynamoDB API Query to retrieve tisits from the table that are
    # equal to the selected filter values.
    response = client.query(
        TableName='TisitsTable',
        IndexName=filter+'Index',
        KeyConditions={
            filter: {
                'AttributeValueList': [
                    {
                        'S': value
                    }
                ],
                'ComparisonOperator': "EQ"
            }
        }
    )

    # loop through the returned tisits and add their attributes to a new dict
    # that matches the JSON response structure expected by the frontend.
    tisitList = getTisitsJson(response["Items"])

    # convert the create list of dicts in to JSON
    return json.dumps(tisitList)

def queryTisits(queryParam):

    logging.info(json.dumps(queryParam))

    filter = queryParam['filter']
    value = queryParam['value']

    return queryTisitItems(filter, value)

# So we can test from the command line
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--filter')
    parser.add_argument('-v', '--value')
    args = parser.parse_args()

    filter = args.filter
    value = args.value

    if args.filter and args.value:
        print(f'filter is {args.filter}')
        print(f'value is {args.value}')

        print('Getting filtered values')

        items = queryTisitItems(args.filter, args.value)
    else:
        print("Getting all values")
        items = getAllTisits()

    print(items)
