# import configparser
# from flask.ext.sqlalchemy import SQLAlchemy
from flask import Flask, jsonify, request, escape
import flask
# from mail import send
from db import db
import time
import json,uuid
from flask.ext.mysql import MySQL

# from flask_mysql import MySQL
from mail import send_mail
import datetime

app = Flask(__name__)
mysql = MySQL()
mongo = db.MongoDB("bot_stats")
session = {}
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
    count = cursor.execute("select e.employee_id, e.first_name,e.last_name from employees e,user u where u.email = '" + _email + "' AND u.password = '" + _password + "' AND e.employee_id=u.employee_id");
    data = cursor.fetchone()
    returnData = None
    if (count != 0):
        id = uuid.uuid4()

        session[str(id)]={'email' : _email,'password' : _password, 'emp_id':data[0]}
        #session[str(id)]['password'] = request.form['password']
        #session['email'] = request.form['email']
        #session['password'] =  request.form['password']
        print str(id)
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
    print session    
    return jsonify(returnData)


@app.route('/logout',methods=['POST'])
def logout():
    # remove the email from the session if it's there
    sidOrg = (request.get_json(silent=True)['sessionId'])

    print str(sidOrg)
    print session
    for k in session:
        print 'session {}'.format(len(k))
    #content = (request.get_json(silent=True)["result"])
    if str(sidOrg) in session:
        session.pop(sidOrg)
        #session.pop('password')
        #session.pop('sid')
        return jsonify({"status":True,"message":"logout successfully"})
    else:
        return jsonify({"status":False,"message":"session not found"})

@app.route("/test", methods=['POST'])
def test():
    sid = (request.get_json(silent=True)['result']['contexts']["sessionId"])
    content = (request.get_json(silent=True)["result"])
    print(content["action"])
    d = []
    if sid in session:
      if content["action"] == "getLunchMenu":
              return get_lunch_items()
      if content["action"] == "bookLunch":
          return bookLunch()
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
      if content["action"] == "requestFacility":
          return request_facility(content)
      if content["action"] == "applyLeaves":
          return apply_leaves(content)
      if content["action"] == "applyODs":
          return apply_ods(content)
      if content["action"] == "getBestWeekend":
          return get_best_leaves()
      return "action not recognized"
    else:
      return generateResponse("Not Logged in", "", {})

def generateResponse(msg, source, resData):
    data = {
        "speech": msg,
        "displayText": msg
    }
    if (source):
        data["source"] = source
        if (resData):
            data["data"] = resData
    return jsonify(data)


def bookLunch():
    sid = (request.get_json(silent=True)['result']['contexts']["sessionId"])
  cursor = mysql.connect().cursor()
  cursor.execute("select items from lunch_items where items_date = CURDATE()")
  items = cursor.fetchone()
  emp_id = session[sid]["emp_id"]
  print items
  order = {"timestamp": time.time(),"items":items[0], "num": 1}
  userData = mongo.findRecord("food_orders",{"emp_id" : emp_id})
  print userData
  if(userData):
      mongo.update_order("food_orders",order,emp_id)
  else:
      mongo.insertRecord("food_orders",{"emp_id" : emp_id,"orders":[order]})
  send_mail({'to':session[sid]['email']}, 'Lunch booking confirmation', 'Your lunch has been booked', 'facilities@gslab.com')
  return generateResponse("Lunch has been booked! Hope you enjoy as always.", "", {})

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

def track_request(content):
    ti = collect_ticket_info(content)
    if not ti:
      return generateResponse('Sorry, no items found for the request', '', {})
    mail = collect_mails(ti[1])
    return generateResponse("I found these items related to your request: {}\nLatest mail:\n{}".format(ti[0], mail), '', {})
    
def collect_ticket_info(content):
    item = content["parameters"]["name"]
    emp_id = content["parameters"]["emp_id"]
    cursor = mysql.connect().cursor()
    count = cursor.execute("select t.idtickets, e.first_name from tickets t, employees e where t.assigned_id=e.employee_id and t.name like '%"+item+"%' and t.emp_id='"+emp_id+"'")
    if count:
      data = cursor.fetchone()
      return ('Ticket id: {} Assigned to:  {}'.format(data[0], data[1]),data[0]) 
    else:
      return ()

def collect_mails(tkt_id):
  sid = (request.get_json(silent=True)['result']['contexts']["sessionId"])
  mail = imaplib.IMAP4_SSL('imap.gmail.com')
  mail.login(session[sid]['email'], session[sid]['_password'])
  mail.list()
  # Out: list of "folders" aka labels in gmail.
  mail.select("inbox") # connect to inbox.

  result, data = mail.search(None, '(FROM "facilities" SUBJECT "Tkt#{}")'.format(tkt_id))

  ids = data[0] # data is a list.
  id_list = ids.split() # ids is a space separated string
  latest_email_id = id_list[-1] # get the latest

  result, data = mail.fetch(latest_email_id, "(RFC822)") # fetch the email body (RFC822)             for the given ID

  raw_email = data[0][1] # here's the body, which is raw text of the whole email
  print(raw_email)

def request_facility(content):
    sid = (request.get_json(silent=True)['result']['contexts']["sessionId"])
    print('sid - '+sid)
    print(session[sid])
    facility_items = content['parameters']['facilityItems']
    it_items = content['parameters']['itItems']
    conn = mysql.connect()
    cursor = conn.cursor()
    tids = []
    if len(it_items) > 0:
      for item in it_items:
        rows = '("{}", "{}", "{}", "{}")'.format('IT', item, 1, session[sid]['emp_id'])
        num = cursor.execute('insert into tickets (type, name, inventory_id, emp_id) values {}'.format(rows))
        conn.commit()
        tids.append('Tkt#{} for {}'.format(cursor.lastrowid, item))
    if len(facility_items) > 0:
      for item in facility_items:
        rows = '("{}", "{}", "{}", "{}")'.format('OTHERS', item, 1, session[sid]['emp_id'])
        num = cursor.execute('insert into tickets (type, name, inventory_id, emp_id) values {}'.format(rows))
        conn.commit()
        tids.append('Tkt#{} for {}'.format(cursor.lastrowid, item))
    for sub in tids:
      send_mail({'to':session[sid]['email']}, sub, 'Thank you for the request! Someone soon will take care of it.', 'facilities@gslab.com')

    return generateResponse("Here you go ?? - {}".format('\n'.join(tids)), "placed", {'tracking_id': cursor.lastrowid})

def get_mail_id(content):
    name = content["parameters"]["name"]
    conn = mysql.connect()
    cursor = conn.cursor()
    num = cursor.execute('select email, first_name, last_name from employees where first_name like "%' + name + '%" or last_name like "%' + name + '%"')
    if (num > 2):
        print("call ml")
        return generateResponse("Did you mean... ?", "call", {"to": "null", "name": "null"})
    else:
        data = cursor.fetchone()
        return generateResponse("Call has been placed", "call", {"to": data[0], "name": data[1] + ' ' + data[2]})

def apply_leaves(content):
  return insert_and_send_mail(content, 'Leave', 'PL', '')

def apply_ods(content):
  reason = content['parameters']['reason']
  return insert_and_send_mail(content, 'OD', 'OD', reason)

def insert_and_send_mail(content, _type, e_type, reason):
  sid = (request.get_json(silent=True)['result']['contexts']["sessionId"])
  conn = mysql.connect()
  cursor = conn.cursor()
  if content['parameters']['periodDate']:
    date = content['parameters']['periodDate']
    arr = date.split('/')
    start = datetime.datetime.strptime(arr[0], "%Y-%m-%d").date()
    end = datetime.datetime.strptime(arr[1], "%Y-%m-%d").date()
    leaves = []
    while start <= end:
      fd = start.strftime('%Y-%m-%d')
      leaves.append(fd)
      row = '("{}", CURDATE(), "{}", "{}", "{}")'.format('gs-0834', fd, e_type, reason)
      cursor.execute('insert into leaves (emp_id, apply_date, for_date, type, reason) values {}'.format(row))
      conn.commit()
      send_mail({'to':session[sid]['email']}, _type + ' application for ' + fd, 'Your manager will approve it soon.', 'facilities@gslab.com')
      start = start + datetime.timedelta(days=1)
    return generateResponse(_type + 's have applied for the following dates - {}'.format('\n'.join(leaves)), "done", {})
  else:
    date = content['parameters']['startDate']
    row = '("{}", CURDATE(), "{}", "{}", "{}")'.format('gs-0834', date, e_type, reason)
    cursor.execute('insert into leaves (emp_id, apply_date, for_date, type, reason) values {}'.format(row))
    conn.commit()
    send_mail({'to':session[sid]['email']}, _type + ' application for ' + date, 'Your manager will approve it soon.', 'facilities@gslab.com')
    return generateResponse(_type + ' has been applied for - {}'.format(date), "done", {})

def get_best_leaves():
    cursor = mysql.connect().cursor()
    cursor.execute(" select * from holidays where DAYNAME(hdate) = 'Friday' or DAYNAME(hdate) = 'Monday';")
    data = cursor.fetchall()
    lst = []
    for t in data:
      if t[0].weekday() == 4:
        lst.append(t[0].strftime('%Y-%m-%d') + ' to ' + (t[0] + datetime.timedelta(days=2)).strftime('%Y-%m-%d') + ' - 3 days')
      else:
        lst.append((t[0] + datetime.timedelta(days=2)).strftime('%Y-%m-%d') + ' to ' + t[0].strftime('%Y-%m-%d') + ' - 3 days')
    return generateResponse("Here's what i found - \n{}".format('\n'.join(lst)), '', {})

if __name__ == "__main__":
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    #sess = Session()
    app.debug = True
    app.run(host='0.0.0.0')


