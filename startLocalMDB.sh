killall mongod
rm -rf db
mkdir -p db
mongod --dbpath=./db --logpath ./db/mongodb.log --fork