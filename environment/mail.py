import smtplib

from email.utils import formatdate
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase

from email import Encoders
import os, datetime

#config = fileutil.social

def send_invite(param):
    CRLF = "\r\n"
    attendees = param['to']
    attendees = ""
    try:
        for att in param['to']:
            attendees += "ATTENDEE;CUTYPE=INDIVIDUAL;ROLE=REQ-PARTICIPANT;PARTSTAT=NEEDS-ACTION;RSVP=TRUE;CN="+att+";X-NUM-GUESTS=0:mailto:"+att+CRLF
    except Exception as e:
        print e
    fro = "Bot <abhijeet.bhagat@gslab.com>"
    
    msg = MIMEMultipart('mixed')
    msg['Reply-To']=fro
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = 'Meeting invitation from abhi'
    msg['From'] = fro
    msg['To'] = attendees

    __location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))
    f= os.path.join(__location__, 'invite.ics')   
    ics_content = open(f).read()
    try:
        replaced_contents = ics_content.replace('startDate', param['meetingStartDate'])
        replaced_contents = replaced_contents.replace('endDate', param['meetingEndDate'])
        replaced_contents = replaced_contents.replace('telephonic', param['location'])
        replaced_contents = replaced_contents.replace('now', datetime.datetime.now().strftime("%Y%m%dT%H%M%SZ"))
    except Exception as e:
        print(e)
    if param.get('describe') is not None:
        replaced_contents = replaced_contents.replace('describe', param.get('describe'))
    else:
        replaced_contents = replaced_contents.replace('describe', '')
    replaced_contents = replaced_contents.replace('attend',  msg['To'])
    replaced_contents = replaced_contents.replace('subject',  param['subject'])
    part_email = MIMEText(replaced_contents,'calendar;method=REQUEST')

    msgAlternative = MIMEMultipart('alternative')
    
    ical_atch = MIMEBase('text/calendar',' ;name="%s"'%"invitation.ics")
    ical_atch.set_payload(replaced_contents)
    Encoders.encode_base64(ical_atch)
    ical_atch.add_header('Content-Disposition', 'attachment; filename="%s"'%f)
    
    msgAlternative.attach(part_email)
    msgAlternative.attach(ical_atch)
    msg.attach(msgAlternative)
    mailServer = smtplib.SMTP('smtp.gmail.com', 587)
    mailServer.ehlo()
    mailServer.starttls()
    mailServer.ehlo()
    mailServer.login('abhijeet.bhagat@gslab.com', 'm@v3r1ck')
    mailServer.sendmail(fro, param['to'], msg.as_string())
    mailServer.close()

def send_mail(param, subject, body, sender):
    msg = MIMEText(body)
    msg['Reply-To']=sender
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = param['to']
    mailServer = smtplib.SMTP('smtp.gmail.com', 587)
    mailServer.ehlo()
    mailServer.starttls()
    mailServer.ehlo()
    mailServer.login('abhijeet.bhagat@gslab.com', 'm@v3r1ck')
    mailServer.sendmail(sender, param['to'], msg.as_string())
    mailServer.close()
if __name__ == "__main__" :
    #send_invite({"to":["abhijeet.bhagat@gslab.com"],"subject":"Party reminder","location":"flat","description":"Hangout","meetingStartDate":"20170512T083000Z","meetingEndDate":"20170512T093000Z"})
    send_mail({'to':'abhijeet.bhagat@gslab.com'}, 'Lets see lights', 'its time!', 'abhijeet.bhagat@gslab.com')
