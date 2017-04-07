#import configparser  
#from flask.ext.sqlalchemy import SQLAlchemy  
from flask import Flask, jsonify, request
from flaskext.mysql import MySQL
#from mail import send
import  json

app= Flask(__name__)

mysql = MySQL()

app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'master'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

@app.route('/login', methods = ['POST'])
def login():
    _email = request.form['email']
    _password = request.form['password']
    cursor = mysql.connect().cursor()
    cursor.execute("select e.first_name,e.last_name from employees e,user u where u.email = '"+_email+"' AND u.password = '"+_password+"' AND e.employee_id=u.employee_id");
    data = cursor.fetchone();
    returnData = None
    if(data) :
        returnData = {
            "status" : True,
            "data" : data
        }
    else :
        returnData = {
            "status" : False,
            "errorMessage" : "Wrong username or password"
        }
    return jsonify(returnData)


@app.route("/test", methods=['POST'])
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
        return get_lunch_items()
    if content["action"] == "getSnacksMenu":
        return generateResponse("There's Poha. Like it?")
    if content["action"] == "makeACall":
        return generateResponse("CallConfirmed")
    if content["action"] == "bookingConfirmed":
        bookLunch(no=2)
        return generateResponse("A booking mail has been sent")
    if content["action"] == "doWebRtcCall" :
        #to do compare here name with the email ID and send email Id a data param
	#return get_mail_id(content["action"]["parameters"])
        return generateResponse("Call has been placed","call",{"to":"abhijeet.bhagat@gslab.com"})
        
    return "action not recognized"

def booklunch(no):
    sendMail()
def get_lunch_items():
    cursor = mysql.connect().cursor()
    cursor.execute("select items from lunch_items where items_date = CURDATE()")
    data = cursor.fetchone()
    return jsonify(data)

def get_mail_id(value):
    cursor = mysql.connect().cursor()
    cursor.execute('select * from employees where first_name like %i'+value['given-name']+'%')
if __name__ == "__main__":  
    app.run(host='0.0.0.0')


