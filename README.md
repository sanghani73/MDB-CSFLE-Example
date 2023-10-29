# MDB-CSFLE-Example

This repository is my sandbox for playing with and getting familiar with MongoDB's automatic & explicit client side field level encryption.

The use case for the automatic encryption is to automatically encrypt two fields in the following document:

```
{
    'Name': 'Jane Doe',
    'email': 'jane.doe@acme.com',
    'NI' : 'NI12999C',
    'OtherInfo': {
        'salary': 3000,
        'foo': 'bar'
    }
}
```

The goal is to have the driver automatically encrypt the `NI` field in a way that will allow it to be queried in subsequent operations. 
In addition everything contained within the `OtherInfo` field should be encrypted so that it is possible to add fields/objects to it in the future and have them automatically encrypted.

One of the current limitations of the CSFLE automatic encryption is a [lack of support for objects and arrays using deterministic encryption](https://www.mongodb.com/docs/manual/core/csfle/fundamentals/encryption-algorithms/#support-for-encrypting-objects-and-arrays). So I've also added a use case where I want encrypt some values held in array elements in a way that allows me to query them in subsequent operations. So using the following model:

```
{
    "name": "Jane Doe",
    "email": "jane@example.com",
    "sensitive_data": [
        {"type": "ssn", "value": "123-45-6789"}
        {"type": "credit_card", "4321-5678-9101-9999"},
        {"type": "PIN", "9999"}
        ]
}
```

Ensure that the `credit_card` is encrypted so that it can be queried and encrypt the PIN using a non-deterministic encryption algorithm.


## Set up
Ensure you have downloaded and installed MongoDB Enterprise Edition if running locally. You can also run this using MongoDB Atlas (it will work on the [free tier](https://www.mongodb.com/cloud/atlas/register)), in which case simply update the connection URI to your cluster.

Install pymongo with encryption dependencies
> pip3 install "pymongo[encryption,srv]~=3.11" 

Install libmongocrypt following [this link](https://www.mongodb.com/docs/manual/core/csfle/reference/libmongocrypt/#mongocryptd-installation)

> brew install mongodb/brew/libmongocrypt

If you have MongoDB running locally start local db by running (not this will kill any monogd process and clean up the local DB files before starting a new local standalone database):
> ./startLocalMDB.sh

## Contents
The repo has seperated the automatic and explicit encryption examples into seperate directories. However each contains the following files:
- *create_key.py* - this needs to be run first as it will generate a local key to represent a KMS and will create the data encryption keys that are held in the key vault collection
- *add_data.py* - the code that adds records to the database, encrypting the various fields either automatically or explicitally 
- *find_all_data.py* - the code that fetches all the data inserted via the `add_data.py` script
- *query_data.py* - the code that fetches a specific record from the data set using a deterministically encrypted value
At the top level you'll find: 
- *startLocalMDB.sh* - simple script to start a local mongoDB instance if running locally (ensure you've installed MongoDB Enterprise if using this)
- *README.me* - this readme


## Script Execution
1. Ensure you've executed the setup as per the instructions above and that your database is up and running.
2. Modify the connection URI accordingly within the various scripts
3. Run `python3 create_key.py` to create a locak KMS, store a key, create a new database called **csfle_demo** with a collection called **people** that has an appropriate schema validator (if using automatic CSFLE)
4. Run `python3 add_data.py` to create some sample data that will either explicitilly or automatically encrypt the various fields as per the use cases
5. Run `python3 find_all_data.py` to fetch all the data, the output shows the encrypted and decrypted values
5. Run `python3 query_data.py` to find a specifc record based on a filter criteria

## CSFLE Breakdown
Take a look at the [documentation](https://www.mongodb.com/docs/manual/core/csfle/fundamentals/automatic-encryption/) for a great picture of the general flow of automatic CSFLE. I've tried to capture some common questions here:

1) For automatic CSFLE, it looks like we're storing a keyId in the schema. Is this the actual key that encrypts/decrypts the data?

No, the `keyId` field in the schema definition is the unique id of the document holding the actual key within the key valut database and collection that was defined in the `create_key.py` script. If you query this collection you will see there is a field called `keyMaterial` which is the key. 

2) Does the driver fetch the actual encryption key every time an opertion is processed on a collection that contains encrypted values? If so is this key cached (and assuming it is can this process be managed)?

It is the [libmongocrypt](https://github.com/mongodb/libmongocrypt) that is responsible for coordinating the encryption and decryption operations. It requests the driver to fetch keys when needed by supplying the filter for a "find" command (which the driver then executes sending the response back to the library). The actual encryption key ((DEK) stored in the `keyMaterial` field in the vault collection document) is cached for one minute after fetching. This time is not configurable and is not impacted if the key is used (so using the key will not extend its lifetime). 

3) When performing the decryption explicitilly, we're not supplying the `keyId` or any other information about the encryption key (other than the details of the vault collection). How does the decryption happen?

The ciphertext of the encrypted value includes the key id hence it is not required. The ciphertext format for CSFLE is documented in the specification: [BSON Binary Subtype 6](https://github.com/mongodb/specifications/blob/d1157f7e135b5a98c50a1cc342597a0905a99a58/source/client-side-encryption/subtype6.rst#types-1-and-2-ciphertext) 

4) How does key rotation of my "master key" held in my KMS impact CSFLE?

The CSFLE feature uses [envelope encryption](https://www.mongodb.com/docs/v7.0/reference/glossary/#std-term-envelope-encryption) which means that the key managed by the customer is used to encrypt the key that us used to encrypt the data. So when you need to rotate the "master key", you will need to rewrap the data key. This can be done via the [KeyVault.rewrapManyDataKey](https://www.mongodb.com/docs/v7.0/reference/method/KeyVault.rewrapManyDataKey/#mongodb-method-KeyVault.rewrapManyDataKey) method. The [following document ](https://www.mongodb.com/docs/v7.0/core/queryable-encryption/fundamentals/manage-keys/) gives you an overive of key rotation and its impact on CSFLE (it is from the Queryable Encryption docs but the process around rotation works in the same way).

More information about CSFLE can be found in [this specification document](https://github.com/mongodb/specifications/blob/d1157f7e135b5a98c50a1cc342597a0905a99a58/source/client-side-encryption/client-side-encryption.rst)