from flask import Flask, request, jsonify, session
from models import db, User
from flask_bcrypt import Bcrypt
from flask_cors import CORS, cross_origin
import finnhub
from backtest_engine import run_backtest
import logging
from liveChart import live_Chart
from companyInfo import company_Info

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = 'cairocoders-ednalan'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flaskdb.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

# Initialize extensions
bcrypt = Bcrypt(app)
CORS(app, supports_credentials=True)
db.init_app(app)

# Create database tables
with app.app_context():
    db.create_all()

# Routes
@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/signup", methods=["POST"])
def signup():
    firstname = request.json["firstname"]
    lastname = request.json["lastname"]
    email = request.json["email"]
    password = request.json["password"]

    user_exists = User.query.filter_by(email=email).first() is not None

    if user_exists:
        return jsonify({"error": "Email already exists"}), 409
    
    hashed_password = bcrypt.generate_password_hash(password)
    new_user = User(firstname=firstname, lastname=lastname, email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    session["user_id"] = new_user.id

    return jsonify({
        "id": new_user.id,
        "firstname": new_user.firstname,
        "lastname": new_user.lastname,
        "email": new_user.email,
    })

@app.route("/login", methods=["POST"])
def login_user():
    email = request.json["email"]
    password = request.json["password"]

    user = User.query.filter_by(email=email).first()

    if user is None:
        return jsonify({"error": "Unauthorized Access"}), 401
    
    if not bcrypt.check_password_hash(user.password, password):
        return jsonify({"error": "Unauthorized"}), 401

    session["user_id"] = user.id
    
    return jsonify({
        "id": user.id,
        "firstname": user.firstname,
        "lastname": user.lastname,
        "email": user.email,
    })

# Initialize Finnhub client
finnhub_client = finnhub.Client(api_key="cpe4ie1r01qh24fmfqj0cpe4ie1r01qh24fmfqjg")

# List of symbols
symbols = ["AAPL", "GOOGL", "AMZN", "MSFT", "TSLA", "META", "NFLX", "NVDA", "WMT", "V"]

@app.route('/stockdata', methods=['POST'])
def fetch_stock_data():
    stock_data = []

    for symbol in symbols:
        data = finnhub_client.quote(symbol)
        change = data['dp']
        if data['pc'] > data['c']:
            change = -abs(change)
        
        stock_info = {
            "symbol": symbol,
            "value": data['c'],
            "change": change
        }
        stock_data.append(stock_info)

    return jsonify(stock_data)

@app.route("/api/backtest", methods=["POST"])
@cross_origin()
def backtest():
    request_data = request.json
    strategy = request_data["strategy"]
    symbol = request_data["symbol"]
    cash = request_data["cash"]
    timeframe = request_data["timeframe"]
    datetimefrom = request_data["datetimefrom"]
    datetimeto = request_data["datetimeto"]
    
    try:
        result = run_backtest(strategy, symbol, cash, timeframe, datetimefrom, datetimeto)
        return jsonify(result)
    except ValueError as e:
        logging.error(f"ValueError: {e}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logging.error(f"Exception: {e}")
        return jsonify({"error": "An error occurred during backtesting"}), 500

@app.route("/liveChart", methods=["POST"]) 
def liveChart():
    symbol = request.json["symbol"]
    try:
        result = live_Chart(symbol)
        return jsonify(result)
    except ValueError as e:
        logging.error(f"ValueError: {e}")
        return jsonify({"error": str(e)}), 400

@app.route("/companyinfo", methods=["POST"]) 
def companyInfo():
    symbol = request.json["symbol1"]
    try:
        result = company_Info(symbol)
        return jsonify(result)
    except ValueError as e:
        logging.error(f"ValueError: {e}")
        return jsonify({"error": str(e)}), 400    

if __name__ == "__main__":
    app.run(debug=True)
