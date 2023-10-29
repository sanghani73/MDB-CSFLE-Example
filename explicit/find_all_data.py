from pathlib import Path
from pymongo import MongoClient
from pymongo.encryption import ClientEncryption

URI_STRING = "mongodb://127.0.0.1:27017/test"

# Load the master key from 'key_bytes.bin':
key_bin = Path("key_bytes.bin").read_bytes()

# Configure a single, local KMS provider, with the saved key:
kms_providers = {"local": {"key": key_bin}}

key_vault_namespace = "csfle_demo.__keystore_explict"

client = MongoClient("mongodb://localhost:27017")
coll = client.csfle_demo.people
client_encryption = ClientEncryption(
    kms_providers,
    key_vault_namespace,
    client,
    coll.codec_options,
)

filter={}
for doc in coll.find(filter=filter):
    print(doc)
    d = doc['sensitive_data']
    for x in d:
        if x['type'] in ['credit_card','PIN']:
            f = client_encryption.decrypt(x['value'])
            print(x['type'],' = ', f)
    print('---------------------------------')

