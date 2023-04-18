# MDB-CSFLE-Example

This repository is my sandbox for playing with MongoDB's automatic client side field level encryption.

I did use [this tutorial](https://www.mongodb.com/developer/languages/python/python-quickstart-fle/) to help me get started.

The example will read a CSV file, transform the data into a suitable format and load it into a MongoDB database encrypting certain fields along the way.

For speed, I've written this in python 3 but please note that the code really is very basic and could be optimized to be significantly faster.
The primary purpose of this exercise was for me to get familiar with the CSFLE functionality.

## Set up
Ensure you have downloaded and installed MongoDB Enterprise Edition if running locally. You can also run this using MongoDB Atlas (it will work on the [free tier](https://www.mongodb.com/cloud/atlas/register)), in which case simply update the connection URI to your cluster.

Install pymongo with encryption dependencies
> pip3 install "pymongo[encryption,srv]~=3.11" 

Install libmongocrypt following [this link](https://www.mongodb.com/docs/manual/core/csfle/reference/libmongocrypt/#mongocryptd-installation)

> brew install mongodb/brew/libmongocrypt

If running locally start local db by running:
> ./startLocalMDB.sh

## Data
The source data for these scripts will use a CSV file containing the following columns:

>"PERSONID", "FIRST_NAME", "LAST_NAME", "DOB", "STREET", "DOORNUMBER", "CITY", "TOWN", "STATE", "POSTCODE", "COUNTRY", "ADDRESS_TYPE", "ADDITIONAL_FIELD1", "ADDITIONAL_FIELD2", "DEPARTMENT", "GRADE", "PERFORMANCE_QUARTER", "EMPLOYMENT_TYPE", "PAYMENT_DATE"

This will be transformed and stored into the following MongoDB model:

```
{
    '_id': ObjectId('643ebd69439337ed2399f09f'), 
    'PERSONID': 'A10000', 
    'PersonDetails': {
        'FIRST_NAME': 'Johanna', 
        'LAST_NAME': 'Ross', 
        'DOB': '15/8/1968', 
        'STREET': 'Erieta Trail', 
        'DOORNUMBER': '65', 
        'CITY': 'Efcavaji', 
        'TOWN': 'gl', 
        'STATE': 'KS', 
        'POSTCODE': 'IM9H 7CL', 
        'COUNTRY': 'England'
    }, 
    'OtherInfo': {
        'ADDRESS_TYPE': 'Home', 
        'ADDITIONAL_FIELD1': 'OiosqoTYhPVXKCxLF', 
        'ADDITIONAL_FIELD2': 'QJgcnBwWwMwIlECKAUT', 
        'DEPARTMENT': 'IT', 
        'GRADE': 'A', 
        'PERFORMANCE_QUARTER': '2023Q1', 
        'EMPLOYMENT_TYPE': 'Employee', 
        'BONUS_STATUS': 'NOT_INITIATED', 
        'PAYMENT_DATE': '8/4/1999'
    }
}
```

## Contents
The repo contains the following files to try out CSFLE:
- *mockData.csv.zip* - containing 1,000,000 randomly generated records (pls uncompress and rename file accordingly)
- *mockData_test.csv* - a subset (around 30) of the records from mockData.csv for testing (saves waiting to load 1,000,000 records)
- *mockData_duplicates* - containg entries with a duplicate ID but a different value for one of the other fields (ADDRESS_TYPE)
- *create_key.py* - the script to create a local KMS provider and a key as well as setup the MongoDB collection with a suitable JSON schema
- *create_unique_index.py* - script to create a unique index on PEOPLEID and OtherInfo.ADDRESS_TYPE so that you can run the test with the index to catch duplicates
- *csfle_main.py* - script to insert the data from mockData.csv file in a single loop using the insert_one operation (this took around 6 mins to run on my laptop)
- *csfle_add_duplicates.py* - script to add the duplicates from mockData_duplicates
- *csfle_delete_duplicates.py* - script to find and delete the duplicates (allows you to tidy up and re-run the add duplicates if you wanted to add a unique index on the compound values)
- *csfle_find_one.py* - example to return a decrypted document
- *startLocalMDB.sh* - simple script to start a local mongoDB instance if running locally (ensure you've installed MongoDB Enterprise if using this)


## Script Execution
1. Ensure your database is up and running and that you've modified the connection URI accordingly
2. Run `python3 create_key.py` to create a locak KMS, store a key, create a new database called **csfle_demo** with a collection called **people** that has an appropriate schema validator
3. Run `python3 csfle_main.py` to load the sample data (change the file name used if you want to load the 1,000,000 records)
4. Run `python3 csfle_find_one.py` to validate that the data is indeed encrypted and that the client can see the decrypted information
5. Run `python3 csfle_add_duplicates.py` to add more documents with logic to identify duplicates
6. Run `python3 create_unique_index.py` to add a unique compound index on the collection so that you cannot add duplicate entries. Re-run the `csfle_main.py` to see what happens once index exists


