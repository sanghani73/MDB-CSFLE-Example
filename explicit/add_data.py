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

example_document = {
    "name": "John Doe",
    "email": "john@example.com",
    "sensitive_data": [
        {"type": "ssn", "value": "123-45-6789"}
    ]
}
encrypted_card = client_encryption.encrypt(
    "1234-5678-9101-1121",
    Algorithm.AEAD_AES_256_CBC_HMAC_SHA_512_Deterministic,
    key_alt_name='Card'
)
credit_card = {"type": "credit_card", "value": encrypted_card}

encrypted_pin = client_encryption.encrypt(
    "1234",
    Algorithm.AEAD_AES_256_CBC_HMAC_SHA_512_Random,
    key_alt_name='PIN'
)
pin = {"type": "PIN", "value": encrypted_pin}

example_document["sensitive_data"].append(credit_card)
example_document["sensitive_data"].append(pin)

print(coll.insert_one(example_document))

# add a second document so that we can show queries on encrypted data
example_document = {
    "name": "Jane Doe",
    "email": "jane@example.com",
    "sensitive_data": [
        {"type": "ssn", "value": "123-45-6789"}
    ]
}
encrypted_card = client_encryption.encrypt(
    "4321-5678-9101-9999",
    Algorithm.AEAD_AES_256_CBC_HMAC_SHA_512_Deterministic,
    key_alt_name='Card'
)
credit_card = {"type": "credit_card", "value": encrypted_card}

encrypted_pin = client_encryption.encrypt(
    "9876",
    Algorithm.AEAD_AES_256_CBC_HMAC_SHA_512_Random,
    key_alt_name='PIN'
)
pin = {"type": "PIN", "value": encrypted_pin}

example_document["sensitive_data"].append(credit_card)
example_document["sensitive_data"].append(pin)

print(coll.insert_one(example_document))
