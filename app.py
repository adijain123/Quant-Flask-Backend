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

# Configure logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(message)s")

# Create database tables
with app.app_context():
    db.create_all()

# Routes
@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    firstname = data.get("firstname")
    lastname = data.get("lastname")
    email = data.get("email")
    password = data.get("password")

    if not all([firstname, lastname, email, password]):
        return jsonify({"error": "Missing signup fields"}), 400

    user_exists = User.query.filter_by(email=email).first() is not None
    if user_exists:
        return jsonify({"error": "Email already exists"}), 409
    
    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
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
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Missing email or password"}), 400

    user = User.query.filter_by(email=email).first()
    if user is None or not bcrypt.check_password_hash(user.password, password):
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
        try:
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
        except Exception as e:
            logging.error(f"Error fetching stock data for {symbol}: {e}")

    return jsonify(stock_data)

@app.route("/api/backtest", methods=["POST"])
@cross_origin()
def backtest():
    data = request.get_json()
    strategy = data.get("strategy")
    symbol = data.get("sym")
    cash = data.get("cash")
    period = data.get("period")
    
    if not all([strategy, symbol, cash, period]):
        return jsonify({"error": "Missing backtest parameters"}), 400

    try:
        result = run_backtest(strategy, symbol, cash, period)
        return jsonify(result)
    except ValueError as e:
        logging.error(f"ValueError: {e}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logging.error(f"Exception: {e}")
        return jsonify({"error": "An error occurred during backtesting"}), 500

@app.route("/liveChart", methods=["POST"]) 
def liveChart():
    data = request.get_json()
    symbol = data.get("symbol1")
    if not symbol:
        return jsonify({"error": "Missing 'symbol1' in request body"}), 400

    try:
        result = live_Chart(symbol)
        return jsonify(result)
    except ValueError as e:
        logging.error(f"ValueError: {e}")
        return jsonify({"error": str(e)}), 400

@app.route("/companyinfo", methods=["POST"]) 
def companyInfo():
    data = request.get_json()
    symbol = data.get("symbol")
    if not symbol:
        return jsonify({"error": "Missing 'symbol' in request body"}), 400

    try:
        result = company_Info(symbol)
        return jsonify(result)
    except ValueError as e:
        logging.error(f"ValueError: {e}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logging.error(f"Exception: {e}")
        return jsonify({"error": "Failed to fetch company info"}), 500

if __name__ == "__main__":
    app.run(debug=True)
