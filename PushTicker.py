#!/bin/python3
import pymongo
from KorbitBase import *
from pymongo.errors import ConnectionFailure
import pprint


class ToMongo(KorbitBase):

    def __init__(self):
        super().__init__
        self.myDictionary = {'timestamp':9999999999999, 'last':'0', 'bid':'0','ask':'0', 'low':'0','high':'0','tx_1min_delta':'0', 'tx_10min_delta':'0' ,
                             'tx_60min_delta':'0','tx_10min_avg':'0', 'tx_60min_avg':'0'}
    
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
    def find(self,mydict):
        try:
            return self.col.find(mydict)
        except ConnectionFailure:
            print("{:20s} | MongoDB is not responsed in a second!".format(""))
    def findOne(self,mydict):
        try:
            return self.col.find_one(mydict)
        except ConnectionFailure:
            print("{:20s} | MongoDB is not responsed in a second!".format(""))
    def findRange(self,mydict,cond):
        try:
            return self.col.find(mydict,cond)
        except ConnectionFailure:
            print("{:20s} | MongoDB is not responsed in a second!".format(""))

    def findAgg(self,mydict):
        try:
            return self.col.aggregate(mydict)
        except ConnectionFailure:
            print("{:20s} | MongoDB is not responsed in a second!".format(""))

    def getValues(self,pTimestamp):
        currentTimestamp = pTimestamp
        #my_range_aggr = [{ "$match":{"timestamp": {"$gte": search_stime, "$lt": search_etime}}} ,{'$group' : {"_id": "null", "average": {"$avg" : "$last"}}}]
        mdbResult = self.findOne({"timestamp":currentTimestamp})

        countMdbResult = len(mdbResult)

        myDictionaryList = list()

        if (mdbResult):
            #tickerDetail = mdbResult[i].split (':')
            #tickerDetail = mdbResult[i].split (':')

            self.myDictionary['timestamp'] = mdbResult['timestamp']
            self.myDictionary['last'] = mdbResult['last']
            self.myDictionary['bid'] = mdbResult['bid']
            self.myDictionary['ask'] = mdbResult['ask']
            self.myDictionary['low'] = mdbResult['low']
            self.myDictionary['high'] = mdbResult['high']

            self.myDictionary['tx_1min_delta'] = self.getDelta(currentTimestamp,1)
            self.myDictionary['tx_10min_delta'] = self.getDelta(currentTimestamp, 10)
            self.myDictionary['tx_60min_delta'] = self.getDelta(currentTimestamp, 60)
            self.myDictionary['tx_10min_avg'] = self.getAverage(currentTimestamp, 10)
            self.myDictionary['tx_60min_avg'] = self.getAverage(currentTimestamp, 60)
            #print('****YE Data : ' + str(self.myDictionary))
            myDictionaryList.append(self.myDictionary)
            #return self.myDictionary
            return myDictionaryList
        else:
            #print('No Data : ' + str(pTimestamp))
            return 0

        return self.myDictionary

    def getDelta(self,currentTimestamp, intv):
        delta = 0
        agg = [{"$match":{"timestamp": {"$gte": currentTimestamp - intv*60*1000, "$lt": currentTimestamp}}},{"$group": { "_id": "null","minlast":{"$min":"$last"},"maxlast":{"$max":"$last"}}}]
        mdbout = self.findAgg(agg)
        for i in mdbout:
            #print(i['maxlast'] , i['minlast'])
            delta = i['maxlast'] - i['minlast'] 
        return round(delta,2)

    def getAverage(self,currentTimestamp, intv):
        avg = 0
        agg = [{"$match":{"timestamp": {"$gte": currentTimestamp - intv*60*1000, "$lt": currentTimestamp}}},{"$group": { "_id": "null","avg":{"$avg":"$last"}}}]
        mdbout = self.findAgg(agg)
        for i in mdbout:
            #print(i['maxlast'] , i['minlast'])
            avg = i['avg']
        return round(avg,2)

if __name__ == "__main__":

    mymongo = ToMongo()
    mymongo.initMongo('korbitsalon-mongo1',27017,'crypto','xrp_ticker')
    tslist = []

    search_stime = mymongo.getEpochTime('2019-06-30 00:00:00')
    search_etime = mymongo.getEpochTime('2019-09-09 00:57:00')
    #print(search_stime)
    #my_one_find = { "timestamp": search_time}
    my_range_find = { "timestamp": {'$gte': search_stime, '$lt': search_etime}}
    mdbout = mymongo.findRange(my_range_find,{"timestamp":1,"_id":0})

    for ticker in  mdbout:
        #print(ticker)
        tslist.append(ticker['timestamp'])
    tslist.sort()
    #print(len(tslist))
    my_range_aggr = [{ "$match":{"timestamp": {"$gte": search_stime, "$lt": search_etime}}} ,{'$group' : {"_id": "null", "average": {"$avg" : "$last"}}}]
    my_one = { "timestamp": 1567961286036 }
    findone = mymongo.findOne(my_one)
    findagg = mymongo.getValues(1567961286036)
    print(findagg)
    #findagg = mymongo.findAgg(my_range_aggr)
    #[ print(i['average']) for i in findagg ]




