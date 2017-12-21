import csv
import json
import requests

class UserSessionInfo:    
    def __init__(self, pSecFilePath):
        self.secFilePath=pSecFilePath
        # key/secret/email/passwd for authentication
        self.accessInfo = 4*[None]
        self.authAtt = ['key','secret','email','password']
        self.urlPrefix = 'https://api.korbit.co.kr/v1'
        self.mySession= requests.Session()
    
    def setAccessInfo(self):
        pass
        
    def readSecFile(self):
        with open(secFilePath) as csvfile:
            keys = csv.DictReader(csvfile, delimiter=',')

            for secrow in keys:
                self.accessInfo[0] = secrow[self.authAtt[0]]
                self.accessInfo[1] = secrow[self.authAtt[1]]
                self.accessInfo[2] = secrow[self.authAtt[2]]
                self.accessInfo[3] = secrow[self.authAtt[3]]
            
            csvfile.close()
#        print(self.accessInfo)

#    def pooling(self):
#        global s
#        s = requests.Session()

    def doPost(self, pUrlPostFix, header='', **params):
        url = '{}/{}'.format(self.urlPrefix, pUrlPostFix)
 #       print(url)
        restResult = self.mySession.post(url, params=params, headers=header)
#        print(restResult, restResult.headers['content-type'])
        print(restResult.text)
        if restResult.status_code == 200:
            return json.loads(restResult.text)
        else:
            raise Exception('{}/{}'.format(restResult.status_code,str(restResult)))

secFilePath="D:\ikoogit\KorbitSalon\ikoo\mykey.csv"
myToken=UserSessionInfo(secFilePath)
myToken.setAccessInfo()
myToken.readSecFile()
#myToken.pooling()
myToken.doPost('oauth2/access_token', client_id=myToken.accessInfo[0], client_secret=myToken.accessInfo[1], username=myToken.accessInfo[2], password=myToken.accessInfo[3], grant_type='password')



 # def requestToken():
 #     client_id,client_secret = getKey(keydir)
#     token = post('oauth2/access_token', client_id=client_id, client_secret=client_secret, username='dotorry@gmail.com', password='DDo3145692', grant_type='password')

#        token['timestamp'] = time.time()

#        store_token('korbit_token.json', token)

#        return token