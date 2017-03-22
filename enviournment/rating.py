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

@application.route("/")
def hello():  
    return "Hello World!"

@application.route("/test", methods=['POST'])
def test():  
    content = (request.get_json(silent=True)["result"])
    print(content["action"])
    d = []
    def generateResponse(msg):
        return jsonify({"speech":msg,  "displayText":msg})
          
    if content["action"] == "getLunchMenu":
        return generateResponse("rice available")
        
    return "action not recognized"

@application.route('/product', methods=['POST'])
def createProduct():

    print('inside product')
    # fetch name and rate from the request
    rate = request.get_json()["rate"]
    name = request.get_json()["name"]

    print('name '+name+' , rate : '+rate)
    product = Products(rate=rate, name=name) #prepare query statement

    curr_session = mysql.session #open database session
    try:
        curr_session.add(product) #add prepared statment to opened session
        curr_session.commit() #commit changes
    except:
        curr_session.rollback()
        curr_session.flush() # for resetting non-commited .add()

    productId = product.id #fetch last inserted id
    data = Products.query.filter_by(id=productId).first() #fetch our inserted product

    result = [data.name, data.rate] #prepare visual data

    return jsonify(session=result)

if __name__ == "__main__":  
    application.run(host='0.0.0.0')
