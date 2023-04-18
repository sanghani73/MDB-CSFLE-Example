from pymongo import MongoClient, ASCENDING

# Change to your database connection string
URI_STRING = "mongodb://127.0.0.1:27017/test"

with MongoClient(URI_STRING) as client:
    x = client.csfle_demo.people.create_index([("PERSONID", ASCENDING),("OtherInfo.ADDRESS_TYPE", ASCENDING)], unique=True)
    print("index created ", x)