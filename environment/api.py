import configparser  
from flask.ext.sqlalchemy import SQLAlchemy  
from flask import Flask, jsonify, request

application = Flask(__name__)

# Read config file
config = configparser.ConfigParser()  
config.read('rating_db.conf')

# MySQL configurations
application.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://' + config.get('DB', 'user') + ':' + config.get('DB', 'password') + '@' + config.get('DB', 'host') + '/' + config.get('DB', 'db') 
print(' Config : '+application.config['SQLALCHEMY_DATABASE_URI'])
application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

mysql = SQLAlchemy()

# map models
class Products(mysql.Model):  
    __tablename__ = 'products'
    id = mysql.Column(mysql.Integer, primary_key=True)
    rate = mysql.Column(mysql.Integer, nullable=False)
    name = mysql.Column(mysql.String(128), nullable=False)

    def __repr__(self):
        return '<Products (%s, %s) >' % (self.rate, self.name)

@application.route("/test", methods=['POST'])
def test():  
    content = (request.get_json(silent=True)["result"])
    print(content["action"])
    d = []
    def generateResponse(msg)
        return jsonify({"speech":msg,  "displayText":msg})
          
    if content["action"] == "getLunchMenu":
        return generateResponse("There's rice, chappatis, daal, mithai. Like it?")
    if content["action"] == "getSnacksMenu":
        return generateResponse("There's Poha. Like it?")
    if content["action"] == "makeACall":
        return generateResponse("CallConfirmed")
    if content["action"] == "bookingConfirmed":
        bookLunch(no=2)
        return generateResponse("A booking mail has been sent")
        
    return "action not recognized"

def booklunch(no):
    sendMail()

if __name__ == "__main__":  
    application.run(host='0.0.0.0')
