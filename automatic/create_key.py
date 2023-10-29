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
   kms_providers=kms_providers, key_vault_namespace="csfle_demo.__keystore"
)

# Connect to MongoDB with the key information generated above:
with MongoClient(URI_STRING, auto_encryption_opts=csfle_opts) as client:
   print("Resetting demo database & keystore ...")
   client.drop_database("csfle_demo")

   # Create a ClientEncryption object to create the data key below:
   client_encryption = ClientEncryption(
      kms_providers,
      "csfle_demo.__keystore",
      client,
      CodecOptions(uuid_representation=STANDARD),
   )

   print("Creating key in MongoDB ...")
   key_id = client_encryption.create_data_key("local")

   schema = {
   "bsonType": "object",
   "properties": {
         "NI": {
            "encrypt": {
               "bsonType": "string",
               # Change to "AEAD_AES_256_CBC_HMAC_SHA_512-Random" if you do not need to filter by this field
               "algorithm": "AEAD_AES_256_CBC_HMAC_SHA_512-Deterministic",
               "keyId": [key_id],  # Reference the key, which is the UUID created above
            }
         },
         "OtherInfo": {
            "encrypt": {
               "bsonType": "object",
               # Change to "AEAD_AES_256_CBC_HMAC_SHA_512-Deterministic" if you need to filter by this field
               "algorithm": "AEAD_AES_256_CBC_HMAC_SHA_512-Random",
               "keyId": [key_id],  # Reference the key, which is the UUID created above
            }            
         }
      },
   }

   print("Creating 'people' collection in 'csfle_demo' database (with schema) ...")
   client.csfle_demo.create_collection(
      "people",
      codec_options=CodecOptions(uuid_representation=STANDARD),
      validator={"$jsonSchema": schema},
   )