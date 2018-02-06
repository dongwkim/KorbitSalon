#!/usr/bin/python3
'''
author             : kiwon.yoon
purpose            : Sending notificatin email
last modified      : 20180105
'''
from email.mime.text import MIMEText
from subprocess import Popen, PIPE
import time

class SendNotificationEmail:
    def __init__(self):
        pass
    
    def sendEmail(self, pFromEmail, pToEmail, pSubject, pBody):
        msg = MIMEText(pBody)
        msg["From"] = pFromEmail
        msg["To"] = pToEmail
        msg["Subject"] = pSubject
        
        #print(msg)
        myPipe = Popen(["/usr/sbin/sendmail", "-t", "-oi"], stdin=PIPE)
        myPipe.communicate(msg.as_string().encode())
    
    def makeEmailBody(self, pBody):
        myCurrentTime = time.strftime("%H:%M:%S")
        emailBody = "*" * 10 + "\n"
        emailBody = emailBody + "* DEAL MADE => " + myCurrentTime + "\n"
        emailBody = emailBody + "*" * 10 + "\n"
        emailBody = emailBody + "* " + pBody + "\n"
        emailBody = emailBody + "*" * 10 + "\n"
        return emailBody
        
if __name__ == "__main__":
    fromEmail = "notification@cryptosalon.org"
    toEmail = "tairu.kim@gmail.com"
    #toEmail = "korbitnotification@gmail.com"
    emailSubject = "Buy {} Coin at price {}".format(10,2500)

    sne = SendNotificationEmail()
    emailBody = sne.makeEmailBody('BUY XRP 12')
    sne.sendEmail(fromEmail, toEmail, emailSubject, emailBody)
