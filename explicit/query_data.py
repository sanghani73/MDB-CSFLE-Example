from pathlib import Path
from pymongo import MongoClient
from pymongo.encryption import ClientEncryption, Algorithm

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

encrypted_card = client_encryption.encrypt(
    "1234-5678-9101-1121",
    Algorithm.AEAD_AES_256_CBC_HMAC_SHA_512_Deterministic,
    key_alt_name='Card'
)
credit_card = {"type": "credit_card", "value": encrypted_card}

filter={
    'sensitive_data': {
        '$elemMatch': {
            'type': 'credit_card', 
            'value': encrypted_card
        }
    }
}

for doc in coll.find(filter=filter):
    print(doc)
    d = doc['sensitive_data']
    for x in d:
        if x['type'] in ['credit_card','PIN']:
            f = client_encryption.decrypt(x['value'])
            print(x['type'],' = ', f)
    print('---------------------------------')

