import time
from pathlib import Path

from pymongo import MongoClient
from pymongo.encryption_options import AutoEncryptionOpts

# Change to your database connection string
URI_STRING = "mongodb://127.0.0.1:27017/test"

# Load the master key from 'key_bytes.bin':
key_bin = Path("key_bytes.bin").read_bytes()

# Configure a single, local KMS provider, with the saved key:
kms_providers = {"local": {"key": key_bin}}

# Create a configuration for PyMongo, specifying the local master key,
# the collection used for storing key data
# json schema specifying field encryption is added as validator on collection so no need to specify:
csfle_opts = AutoEncryptionOpts(
   kms_providers,
   "csfle_demo.__keystore"
)

duplicates = ["A10000","A10001","A10002","A10003","A10004","A10005","A10006","A10007","A10008","A10009","A10010"]

st = time.time()
with MongoClient(URI_STRING, auto_encryption_opts=csfle_opts) as client:
    for row in duplicates:
        x = client.csfle_demo.people.delete_one({"PERSONID": row, "OtherInfo.ADDRESS_TYPE": "Office"})
        if x.deleted_count!=0:
            print('Deleted', row)

et = time.time()
elapsed_time = et - st
print('Execution time:', elapsed_time, 'seconds')
