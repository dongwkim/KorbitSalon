#!/bin/python3
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

    def findAgg(self,mydict):
        try:
            return self.col.aggregate(mydict)
        except ConnectionFailure:
            print("{:20s} | MongoDB is not responsed in a second!".format(""))


if __name__ == "__main__":

    mymongo = ToMongo()
    search_stime = mymongo.getEpochTime('2019-06-30 00:00:00')
    search_etime = mymongo.getEpochTime('2019-07-05 00:57:00')
    #print(search_stime)
    #my_one_find = { "timestamp": search_time}
    my_range_find = { "timestamp": {'$gte': search_stime, '$lt': search_etime}}
    mymongo.initMongo('korbitsalon-mongo1',27017,'crypto','xrp_ticker')

    timestamplist = []
    out = mymongo.findRange(my_range_find)

    for ticker in  out:
        #print(ticker)
        timestamplist.append(ticker['timestamp'])
    timestamplist.sort()
    print(len(timestamplist))
    my_range_aggr = [{ "$match":{"timestamp": {"$gte": search_stime, "$lt": search_etime}}} ,{'$group' : {"_id": "null", "average": {"$avg" : "$last"}}}]
    findagg = mymongo.findAgg(my_range_aggr)
    [ print(i['average']) for i in findagg ]




