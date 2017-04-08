from pymongo import MongoClient
import pprint

class MongoDB:
    def __init__(self, dbname):
        self._conn = MongoClient("localhost", 27017)
        self._db   = self._conn[dbname]

    def createCollection(self, name=""):
        return self._db[name]
    def update_order(self,collection,record,emp_id):
        self._db[collection].update({"emp_id" : emp_id}, {'$push': {"orders": record}})


    def insertRecord(self, collection, record):
        self._db[collection].insert_one(record)

    def findRecord(self, collection, kv):
        return self._db[collection].find_one(kv)

