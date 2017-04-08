# import configparser
# from flask.ext.sqlalchemy import SQLAlchemy
from flask import Flask, jsonify, request, session, Session,escape
import flask
# from mail import send
import json,uuid
from flask.ext.mysql import MySQL

# from flask_mysql import MySQL
# from mail import send
app = Flask(__name__)
mysql = MySQL()

app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'master'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)



@app.route('/login', methods=['POST'])
def login():
    #content = (request.get_json(silent=True))
    _email = (request.get_json(silent=True)['email'])
    _password = (request.get_json(silent=True)['password'])
    print _email
    cursor = mysql.connect().cursor()
    count = cursor.execute("select e.first_name,e.last_name from employees e,user u where u.email = '" + _email + "' AND u.password = '" + _password + "' AND e.employee_id=u.employee_id");
    data = cursor.fetchone()
    returnData = None
    if (count != 0):
        id = uuid.uuid4()

        session[str(id)]={'email' : _email,'password' : _password}
        #session[str(id)]['password'] = request.form['password']
        #session['email'] = request.form['email']
        #session['password'] =  request.form['password']
        returnData = {
            "status": True,
            "data": data,
            "session_id" :  id
        }
    else:
        returnData = {
            "status": False,
            "errorMessage": "Wrong username or password"
        }
    return jsonify(returnData)


@app.route('/logout',methods=['POST'])
def logout():
    # remove the email from the session if it's there
    sidOrg = (request.get_json(silent=True)['session_id'])
    #content = (request.get_json(silent=True)["result"])
    if sidOrg in session:
        session.pop(sidOrg)
        #session.pop('password')
        #session.pop('sid')
        return generateResponse("Logged Out successfully","",{})

@app.route("/test", methods=['POST'])
def test():
    sid = (request.get_json(silent=True)["sessionId"])
    content = (request.get_json(silent=True)["result"])
    print(content["action"])
    d = []

    if content["action"] == "getLunchMenu":
        if sid in session:
            return get_lunch_items()
        else:
            return generateResponse("Not Logged in", "", {})
    if content["action"] == "getSnacksMenu":
        return get_snacks_items()
    if content["action"] == "makeACall":
        return generateResponse("CallConfirmed")
    if content["action"] == "bookingConfirmed":
        bookLunch(no=2)
        return generateResponse("A booking mail has been sent")
    if content["action"] == "doWebRtcCall":
        # to do compare here name with the email ID and send email Id a data param
        return get_mail_id(content)
    if content["action"] == "trackRequest":
        return track_request(content)
    return "action not recognized"


def generateResponse(msg, source, resData):
    data = {
        "speech": msg,
        "displayText": msg
    }
    if (source):
        data["source"] = source;
        if (resData):
            data["data"] = resData;
    return jsonify(data)


def booklunch(no):
    sendMail()


def get_lunch_items():
    if 'email' in session:
        cursor = mysql.connect().cursor()
        cursor.execute("select items from lunch_items where items_date = CURDATE()")
        data = cursor.fetchone()
        return generateResponse("Theres " + data[0], "show", {"list": data})
    else:
        return generateResponse("Not Logged in","",{})

def get_snacks_items():
    cursor = mysql.connect().cursor()
    cursor.execute("select snacks from lunch_items where items_date = CURDATE()")
    data = cursor.fetchone()
    return generateResponse("Theres " + data[0], "show", {"list": data})

def track_request(content):
    ti = collect_ticket_info(content)
    mail = collect_mails(ti[1])
    return "I found these items related to your request: {}\nLatest mail:\n{}".format(ti[0], mail)
    
def collect_ticket_info(content):
    item = content["parameters"]["name"]
    emp_id = content["parameters"]["emp_id"]
    cursor = mysql.connect().cursor()
    cursor.execute("select t.idtickets, e.first_name from tickets t, employees e where t.assigned_id=e.employee_id and t.name like '%"+item+"%' and t.emp_id='"+emp_id+"'")
    data = cursor.fetchone()
    return ('Ticket id: {} Assigned to:  {}'.format(data[0], data[1]),data[0]) 

def collect_mails(tkt_id):
  mail = imaplib.IMAP4_SSL('imap.gmail.com')
  mail.login('abhijeet.bhagat@gslab.com', 'm@v3r1ck')
  mail.list()
  # Out: list of "folders" aka labels in gmail.
  mail.select("inbox") # connect to inbox.

  result, data = mail.search(None, '(FROM "abhijeet bhagat" SUBJECT "Tkt#{}")'.format(tkt_id))

  ids = data[0] # data is a list.
  id_list = ids.split() # ids is a space separated string
  latest_email_id = id_list[-1] # get the latest

  result, data = mail.fetch(latest_email_id, "(RFC822)") # fetch the email body (RFC822)             for the given ID

  raw_email = data[0][1] # here's the body, which is raw text of the whole email
  print(raw_email)

def request_facility():
    pass


def get_mail_id(content):
    name = content["parameters"]["name"]
    cursor = mysql.connect().cursor()
    num = cursor.execute(
        'select email, first_name, last_name from employees where first_name like "%' + name + '%" or last_name like "%' + name + '%"')
    if (num > 2):
        print("call ml")
        return generateResponse("Did you mean... ?", "call", {"to": "null", "name": "null"})
    else:
        data = cursor.fetchone()
        return generateResponse("Call has been placed", "call", {"to": data[0], "name": data[1] + ' ' + data[2]})


if __name__ == "__main__":
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    sess = Session()
    app.debug = True
    app.run(host='0.0.0.0')


