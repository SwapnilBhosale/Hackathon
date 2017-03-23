from pymongo import MongoClient
import pprint

class MongoDB: 
    def __init__(self, dbname):
        self._conn = MongoClient("localhost", 27017)
        self._db   = self._conn[dbname]

    def createCollection(self, name=""):
        return self._db[name]
    
    def insertRecord(self, collection, record):
        self._db[collection].insert_one(record)

    def findRecord(self, collection, kv):
        return self._db[collection].find_one(kv)

if __name__ == '__main__':
    database   = MongoDB("stats")
    pprint.pprint (database.findRecord("food_orders", {"emp_id" : 'gs-0834'}))
