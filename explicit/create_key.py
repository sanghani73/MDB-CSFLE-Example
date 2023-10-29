# create_key.py

from pathlib import Path
from secrets import token_bytes

from bson.binary import STANDARD
from bson.codec_options import CodecOptions
from pymongo import MongoClient
from pymongo.encryption import ClientEncryption
from pymongo.encryption_options import AutoEncryptionOpts

URI_STRING = "mongodb://127.0.0.1:27017/test"

# Generate a secure 96-byte secret key:
key_bytes = token_bytes(96)

Path("key_bytes.bin").write_bytes(key_bytes)

# Configure a single, local KMS provider, with the saved key:
kms_providers = {"local": {"key": key_bytes}}
csfle_opts = AutoEncryptionOpts(
   kms_providers=kms_providers, key_vault_namespace="csfle_demo.__keystore_explict"
)

# Connect to MongoDB with the key information generated above:
with MongoClient(URI_STRING, auto_encryption_opts=csfle_opts) as client:
   print("Resetting demo database & keystore ...")
   client.drop_database("csfle_demo")

   # Create a ClientEncryption object to create the data key below:
   client_encryption = ClientEncryption(
      kms_providers,
      "csfle_demo.__keystore_explict",
      client,
      CodecOptions(uuid_representation=STANDARD),
   )

   print("Creating key in MongoDB ...")
   key_card_id = client_encryption.create_data_key("local", key_alt_names=["Card"])
   key_pin_id = client_encryption.create_data_key("local", key_alt_names=["PIN"])

