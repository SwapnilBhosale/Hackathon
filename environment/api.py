#import configparser  
#from flask.ext.sqlalchemy import SQLAlchemy  
from flask import Flask, jsonify, request
#from mail import send 

application = Flask(__name__)

# Read config file
#config = configparser.ConfigParser()  
#config.read('rating_db.conf')

# MySQL configurations
#application.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://' + config.get('DB', 'user') + ':' + config.get('DB', 'password') + '@' + config.get('DB', 'host') + '/' + config.get('DB', 'db') 
#print(' Config : '+application.config['SQLALCHEMY_DATABASE_URI'])
#application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

#mysql = SQLAlchemy()

# map models

@application.route("/test", methods=['POST'])
def test():  
    content = (request.get_json(silent=True)["result"])
    print(content["action"])
    d = []
    def generateResponse(msg,source,resData):
        data = {
            "speech" : msg,
            "displayText" : msg
        }
        if(source):
            data["source"] = source;
        if(resData):
            data["data"] = resData;
        return jsonify(data)
          
    if content["action"] == "getLunchMenu":
        return generateResponse("There's rice, chappatis, daal, mithai. Like it?")
    if content["action"] == "getSnacksMenu":
        return generateResponse("There's Poha. Like it?")
    if content["action"] == "makeACall":
        return generateResponse("CallConfirmed")
    if content["action"] == "bookingConfirmed":
        bookLunch(no=2)
        return generateResponse("A booking mail has been sent")
    if content["action"] == "doWebRtcCall" :
        #to do compare here name with the email ID and send email Id a data param
        return generateResponse("Call has been placed","call",{"to":"abhijeet.bhagat@gslab.com"})
        
    return "action not recognized"

def booklunch(no):
    sendMail()

if __name__ == "__main__":  
    application.run(host='0.0.0.0')
