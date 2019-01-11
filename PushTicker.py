import pymongo
from KorbitBase import *
from pymongo.errors import ConnectionFailure
import pprint


class ToMongo(KorbitBase):

    def __init__(self):
        pass
    
    def initMongo(self, pHost, pPort, pDb, pCol):
        self.uri = "mongodb://%s:%s" % (pHost, pPort)
        self.cli = pymongo.MongoClient(self.uri, serverSelectionTimeoutMS=1000, connectTimeoutMS=1000)
        self.db = self.cli[pDb]
        self.col = self.db[pCol]
    def insertOne(self,mydict):
        try:
            self.col.insert_one(mydict)
        except ConnectionFailure:
            print("{:20s} | MongoDB is not responsed in a second!".format(""))
    def findOne(self,mydict):
        try:
            return self.col.find_one(mydict)
        except ConnectionFailure:
            print("{:20s} | MongoDB is not responsed in a second!".format(""))
    def findRange(self,mydict):
        try:
            return self.col.find(mydict)
        except ConnectionFailure:
            print("{:20s} | MongoDB is not responsed in a second!".format(""))


if __name__ == "__main__":

    mymongo = ToMongo()
    search_stime = mymongo.getEpochTime('2019-01-12 01:41:00')
    search_etime = mymongo.getEpochTime('2019-01-12 01:45:00')
    #print(search_stime)
    #my_one_find = { "timestamp": search_time}
    my_range_find = { "timestamp": {'$gte': search_stime, '$lt': search_etime}}
    mymongo.initMongo('crypto-mongo-1',27017,'crypto','korbit_ticker')
    for doc in  mymongo.findRange(my_range_find):
        print(doc)


