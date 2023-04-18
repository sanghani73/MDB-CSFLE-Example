import csv 
import time
from pathlib import Path

from pymongo import MongoClient
from pymongo.encryption_options import AutoEncryptionOpts

# Change to your database connection string
URI_STRING = "mongodb://127.0.0.1:27017/test"
CSV_FILE="mockData_test.csv"

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

header = ["PERSONID", "FIRST_NAME", "LAST_NAME", "DOB", "STREET", "DOORNUMBER", "CITY", "TOWN", "STATE", "POSTCODE", "COUNTRY", "ADDRESS_TYPE", "ADDITIONAL_FIELD1", "ADDITIONAL_FIELD2", "DEPARTMENT", "GRADE", "PERFORMANCE_QUARTER", "EMPLOYMENT_TYPE", "BONUS_STATUS","PAYMENT_DATE"]

st = time.time()
with MongoClient(URI_STRING, auto_encryption_opts=csfle_opts) as client:
    with open(CSV_FILE, 'r') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',')
        for row in spamreader:
            # print(row)
            PersonDetails = {
                header[1] : row[1],
                header[2] : row[2],
                header[3] : row[3],
                header[4] : row[4],
                header[5] : row[5],
                header[6] : row[6],
                header[7] : row[7],
                header[8] : row[8],
                header[9] : row[9],
                header[10] : row[10]
            }
            OtherInfo = {
                header[11] : row[11],
                header[12] : row[12],
                header[13] : row[13],
                header[14] : row[14],
                header[15] : row[15],
                header[16] : row[16],
                header[17] : row[17],
                header[18] : row[18],
                header[19] : row[19],
            }
            doc = {
                header[0] : row[0],
                'PersonDetails' : PersonDetails,
                'OtherInfo' : OtherInfo
            }
            # print(doc)
            client.csfle_demo.people.insert_one(doc)
            # print(client.csfle_demo.people.find_one())

et = time.time()
elapsed_time = et - st
print('Execution time:', elapsed_time, 'seconds')

# with MongoClient(URI_STRING, auto_encryption_opts=csfle_opts) as client:
#     print(client.csfle_demo.people.find_one())
