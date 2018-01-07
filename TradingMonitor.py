'''
version : 20180106-v1
'''
from SendNotificationEmail import *
import subprocess
import logging
import time
import os
import re

logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s %(message)s',filename='/var/log/TradingMonitor.log',level=logging.INFO)
logger = logging.getLogger('TradingMonitor')

def findThisProcess( process_name ):
  ps     = subprocess.Popen("ps -eaf | grep "+process_name, shell=True, stdout=subprocess.PIPE)
  output = ps.stdout.read()
  ps.stdout.close()
  ps.wait()

  return output

# This is the function you can use  
def isThisRunning( process_name ):
  output = findThisProcess( process_name )

  if re.search(('path/of/process'+process_name).encode(), output) is None:
    return False
  else:
    return True

if __name__ == '__main__':
    fromEmail = "CRYPTOSALON@cryptosalon.org"
    toEmail = "ikooyoon@gmail.com"
    emailSubject = "Korbit_Trading_XRP DIED"
    sne = SendNotificationEmail()
    emailBody = sne.makeEmailBody('Korbit_Trading_XRP DIED')
    
    if isThisRunning('korbit_trading_xrp1') == False:
        print("Not running")
    else:
        print("Running!")
        