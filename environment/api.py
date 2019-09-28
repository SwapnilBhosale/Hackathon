# import configparser
# from flask.ext.sqlalchemy import SQLAlchemy
from flask import Flask, jsonify, request
import flask
# from mail import send
from db import db
import time
import json,uuid
from flaskext.mysql import MySQL

#import pandas as pd
#import numpy as np
#from sklearn.tree import DecisionTreeClassifier, export_graphviz
#from sklearn.model_selection import train_test_split


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
    print( _email)
    cursor = mysql.connect().cursor()
    count = cursor.execute("select u.user_id, u.first_name,u.last_name from users u where u.email = '" + _email + "' AND u.password = '" + _password+"'")
    data = cursor.fetchone()
    returnData = None
    if (count != 0):
        id = uuid.uuid4()

        session[str(id)]={'email' : _email,'password' : _password, 'emp_id':data[0]}
        #session[str(id)]['password'] = request.form['password']
        #session['email'] = request.form['email']
        #session['password'] =  request.form['password']
        print( str(id))
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
    print( session )   
    return jsonify(returnData)


@app.route('/logout',methods=['POST'])
def logout():
    # remove the email from the session if it's there
    sidOrg = (request.get_json(silent=True)['sessionId'])

    print( str(sidOrg))
    print( session)
    for k in session:
        print( 'session {}'.format(len(k)))
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
    print(request.get_json())
    #sid = (request.get_json(silent=True)['result']['event'][0]['parameters']["sessionId"])
    #print( sid)
    #print( session)
    content = (request.get_json(silent=True)["result"])
    print((content["action"]))
    d = []
    #if sid in session:
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
    if content["action"] == "showMap":
        return openMap(content)
    if content["action"] == "showMapDefault":
        return openMapDefault(content) 
    if content["action"] == "todayMenu":
        return openMenu(content)
    if content["action"] == "transitDefault":
        return openTransitDefault(content)
    if content["action"] == "transit":
        return openTransit(content)
    return "action not recognized"

def openTransit(content):
    msg = "Opening Schedule"
    source = "transit"
    data = {
        "from": content["parameters"]["from"], 
        "to": content["parameters"]["to"]
    }
    return generateResponse(msg, source, data)
    
def openTransitDefault(content):
    msg = "Opening Schedule"
    source = "transit"
    data = {
        "to": content["parameters"]["to"]
    }
    return generateResponse(msg, source, data)
def openMenu(content):
    msg = 'Opening Menu'
    source = 'menu'
    data = {
        "in": content["parameters"]["in"]
    }
    return generateResponse(msg, source, data)

def openMapDefault(content):
    msg = 'Opening Map'
    source = "map"
    data = {
        "to": content["parameters"]["to"]
    }
    return generateResponse(msg, source, data)

def openMap(content):

    msg = "opening map"
    source = "map"
    data = {
        "from": content['parameters']['from'],
        "to": content['parameters']['to']
    }
    return generateResponse(msg, source, data)


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
  sid = (request.get_json(silent=True)['result']['contexts']['parameters']["sessionId"])
  cursor = mysql.connect().cursor()
  cursor.execute("select items from lunch_items where items_date = CURDATE()")
  items = cursor.fetchone()
  emp_id = session[sid]["emp_id"]
  print( items)
  order = {"timestamp": time.time(),"items":items[0], "num": 1}
  userData = mongo.findRecord("food_orders",{"emp_id" : emp_id})
  print( userData)
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
    #mail = collect_mails(ti[1])
    return generateResponse("I found these items related to your request: {}".format(ti[0]), '', {})
    
def collect_ticket_info(content):
    sid = (request.get_json(silent=True)['result']['contexts'][0]['parameters']["sessionId"])
    item = content["parameters"]["name"]
    emp_id = session[sid]['emp_id']
    cursor = mysql.connect().cursor()
    count = cursor.execute("select t.idtickets, e.first_name from tickets t, employees e where t.assigned_id=e.employee_id and t.name like '%"+item+"%' and t.emp_id='"+emp_id+"'")
    if count:
      data = cursor.fetchone()
      return ('Ticket id: {} Assigned to:  {}'.format(data[0], data[1]),data[0]) 
    else:
      return ()

def collect_mails(tkt_id):
  sid = (request.get_json(silent=True)['result']['contexts'][0]['parameters']["sessionId"])
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
  print((raw_email))


def doStats(sessionId):
	print((session[sessionId]["emp_id"]))
	data = mongo.findRecord("food_orders",{"emp_id" : session[sessionId]["emp_id"]})
	df = pd.DataFrame(data["orders"])
	#print( pd
	#print((data)
	print( df.head())
	
	df_mod = df.copy();
	df['isBooked'] = df['num'] > 1
	df.drop('num', axis=1, inplace=True)
	df.drop('timestamp', axis=1, inplace=True)
	df['items'].str[1:-1].str.split(',', expand=True)
	df['a'] = df['items'].str.split(",").str.get(0)
	df['b'] = df['items'].str.split(",").str.get(1)
	df['c'] = df['items'].str.split(",").str.get(2)
	df['d'] = df['items'].str.split(",").str.get(3)
	df['e'] = df['items'].str.split(",").str.get(4)
	df['f'] = df['items'].str.split(",").str.get(5)
	df['g'] = df['items'].str.split(",").str.get(6)
	df['h'] = df['items'].str.split(",").str.get(7)
	df['i'] = df['items'].str.split(",").str.get(8)
	df.drop('items', axis=1, inplace=True)
	
	
	print( df.head())
	
	#train, test = train_test_split(df, test_size = 0.2)
	#X = train["items"]).split(",")
	#Y = train["isBooked"]
	#dff= df.DataFrame(d)
	#dtree = DecisionTreeClassifier(max_leaf_nodes=3,random_state=0,compute_importances = True)
	#dtree = dtree.fit(X, Y)
	#print( DataFrame(dtree.feature_importances_, columns = ["Imp"], index = X.columns).sort(['Imp'], ascending = False)
	
def request_facility(content):
    sid = (request.get_json(silent=True)['result']['contexts'][0]['parameters']["sessionId"])
    print(('sid - '+sid))
    print((session[sid]))
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
    num = cursor.execute('select email, first_name, last_name from users where first_name like "%' + name + '%" or last_name like "%' + name + '%"')
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
  sid = (request.get_json(silent=True)['result']['contexts'][0]['parameters']["sessionId"])
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


