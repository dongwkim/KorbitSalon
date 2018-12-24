import pymongo


class PushTicker2Mongo():

    def __init__(self):
        return
    
    def initMongo(self, pHost, pPort, pDb, pCol):
        self.uri = "mongodb://%s:%s" % (pHost, pPort)
        self.cli = pymongo.MongoClient(self.uri)
        self.db = self.cli[pDb]
        self.col = self.db[pCol]
    def insertOne(self,mydict):
        self.col.insert_one(mydict)


mydict = { "name":"dongwki" ,"age": "36"}
mymongo = PushTicker2Mongo()
mymongo.initMongo('crypto-mongo-1',27017,'crypto','korbit_ticker')


