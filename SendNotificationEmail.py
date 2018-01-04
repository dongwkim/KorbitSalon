'''
author             : kiwon.yoon
purpose            : Sending notification email
last modified      : 20180105
pre-requisition    : configuring sendmail
'''
from email.mime.text import MIMEText
from subprocess import Popen, PIPE
import time

class SendNotificationEmail:
    def __init(self):
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
        emailBody = "*" * 80 + "\n"
        emailBody = emailBody + "* DEAL MADE => " + myCurrentTime + "\n"
        emailBody = emailBody + "*" * 80 + "\n"
        emailBody = emailBody + "* " + pBody + "\n"
        emailBody = emailBody + "*" * 80 + "\n"
        return emailBody
        
if __name__ == "__main__":
    fromEmail = "CRYPTOSALON@cryptosalon.org"
    toEmail = "ikooyoon@gmail.com"
    emailSubject = "Notification from CRYPTOSALON"

    sne = SendNotificationEmail()
    emailBody = sne.makeEmailBody('BUY XRP 13')
    sne.sendEmail(fromEmail, toEmail, emailSubject, emailBody)
