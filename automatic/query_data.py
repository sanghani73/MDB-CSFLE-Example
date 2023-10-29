# csfle_main.py

from pathlib import Path
from pymongo import MongoClient
from pymongo.encryption_options import AutoEncryptionOpts

URI_STRING = "mongodb://127.0.0.1:27017/test"

# Load the master key from 'key_bytes.bin':
key_bin = Path("key_bytes.bin").read_bytes()

# Configure a single, local KMS provider, with the saved key:
kms_providers = {"local": {"key": key_bin}}

# Create the CSFLE options object specifying the local master key provider and the location of the data encryption key vault,
# the collection used for storing key data
csfle_opts = AutoEncryptionOpts(
   kms_providers,
   "csfle_demo.__keystore"
)

client = MongoClient(URI_STRING, auto_encryption_opts=csfle_opts)
print('with CSFLE')
for doc in client.csfle_demo.people.find({"NI":"NI12999C"}):
    print(doc)
print('---------------------------------')
print('without CSFLE')
for doc in MongoClient(URI_STRING).csfle_demo.people.find({"NI":"NI12999C"}):
    print(doc)

