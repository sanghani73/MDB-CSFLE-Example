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
doc1 = {'Name': 'Jane Doe',
        'email': 'jane.doe@acme.com',
        'NI' : 'NI12999C',
        'OtherInfo': {
            'salary': 3000,
            'foo': 'bar'
            }
        }
doc2 = {'Name': 'Joe Bloggs',
        'email': 'joe.bloggs@acme.com',
        'NI' : 'NI123121C',
        'OtherInfo': {
                'salary': 2000,
                'some': 'data'
                }
        }

print( client.csfle_demo.people.insert_many([doc1,doc2]))
