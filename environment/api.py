#import configparser  
#from flask.ext.sqlalchemy import SQLAlchemy  
from flask import Flask, jsonify, request
from flask.ext.mysql import MySQL
#from flask_mysql import MySQL
#from mail import send 

app= Flask(__name__)

mysql = MySQL()

app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'master'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

@app.route("/test", methods=['POST'])
def test():  
    content = (request.get_json(silent=True)["result"])
    print(content["action"])
    d = []
          
    if content["action"] == "getLunchMenu":
        return get_lunch_items()
    if content["action"] == "getSnacksMenu":
        return get_snacks_items()
    if content["action"] == "makeACall":
        return generateResponse("CallConfirmed")
    if content["action"] == "bookingConfirmed":
        bookLunch(no=2)
        return generateResponse("A booking mail has been sent")
    if content["action"] == "doWebRtcCall" :
        #to do compare here name with the email ID and send email Id a data param
        return get_mail_id(content)
    return "action not recognized"

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

def booklunch(no):
    sendMail()

def get_lunch_items():
    cursor = mysql.connect().cursor()
    cursor.execute("select items from lunch_items where items_date = CURDATE()")
    data = cursor.fetchone()
    return generateResponse("Theres " + data[0], "show", {"list": data})

def get_snacks_items():
    cursor = mysql.connect().cursor()
    cursor.execute("select snacks from lunch_items where items_date = CURDATE()")
    data = cursor.fetchone()
    return generateResponse("Theres " + data[0], "show", {"list": data})

def get_mail_id(content):
    name = content["parameters"]["name"]
    cursor = mysql.connect().cursor()
    num = cursor.execute('select email, first_name, last_name from employees where first_name like "%'+name+'%"')
    if (num > 2):
      print("call ml")
      return generateResponse("Did you mean... ?","call",{"to":"null", "name": "null"})
    else:
      data = cursor.fetchone()
      return generateResponse("Call has been placed","call",{"to":data[0], "name": data[1] + ' ' + data[2]})

if __name__ == "__main__":  
    app.run(host='0.0.0.0')
