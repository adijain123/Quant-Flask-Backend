```python
import os
import logging

from flask import Flask, request, jsonify, session
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

from models import db, User
import finnhub
from backtest_engine import run_backtest
from liveChart import live_Chart
from companyInfo import company_Info


# --------------------------------------------------
# Flask application configuration
# --------------------------------------------------

app = Flask(__name__)

app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")

if not app.config["SECRET_KEY"]:
    raise RuntimeError("SECRET_KEY environment variable is not configured.")

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL",
    "sqlite:///flaskdb.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = False

# Session cookie configuration for cross-origin requests.
# Use HTTPS in production.
app.config["SESSION_COOKIE_SECURE"] = True
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "None"

# --------------------------------------------------
# Extensions
# --------------------------------------------------

bcrypt = Bcrypt(app)

CORS(
    app,
    resources={
        r"/*": {
            "origins": [
                "https://algo-trading-sigma.vercel.app"
            ]
        }
    },
    supports_credentials=True,
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"]
)

db.init_app(app)

# --------------------------------------------------
# Logging
# --------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# --------------------------------------------------
# Database initialization
# --------------------------------------------------

with app.app_context():
    db.create_all()

# --------------------------------------------------
# Finnhub configuration
# --------------------------------------------------

FINNHUB_API_KEY = os.environ.get("FINNHUB_API_KEY")

if not FINNHUB_API_KEY:
    logging.warning(
        "FINNHUB_API_KEY is not configured. Stock-data requests will fail."
    )
    finnhub_client = None
else:
    finnhub_client = finnhub.Client(api_key=FINNHUB_API_KEY)

symbols = [
    "AAPL", "GOOGL", "AMZN", "MSFT", "TSLA",
    "META", "NFLX", "NVDA", "WMT", "V"
]

# --------------------------------------------------
# Routes
# --------------------------------------------------

@app.route("/", methods=["GET"])
def hello_world():
    return jsonify({
        "message": "Algorithmic Trading API is running"
    })


@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json(silent=True) or {}

    firstname = data.get("firstname")
    lastname = data.get("lastname")
    email = data.get("email")
    password = data.get("password")

    if not all([firstname, lastname, email, password]):
        return jsonify({"error": "Missing signup fields"}), 400

    user_exists = User.query.filter_by(email=email).first() is not None

    if user_exists:
        return jsonify({"error": "Email already exists"}), 409

    hashed_password = bcrypt.generate_password_hash(
        password
    ).decode("utf-8")

    new_user = User(
        firstname=firstname,
        lastname=lastname,
        email=email,
        password=hashed_password
    )

    db.session.add(new_user)
    db.session.commit()

    session["user_id"] = new_user.id

    return jsonify({
        "id": new_user.id,
        "firstname": new_user.firstname,
        "lastname": new_user.lastname,
        "email": new_user.email
    }), 201


@app.route("/login", methods=["POST"])
def login_user():
    data = request.get_json(silent=True) or {}

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Missing email or password"}), 400

    user = User.query.filter_by(email=email).first()

    if user is None or not bcrypt.check_password_hash(
        user.password, password
    ):
        return jsonify({"error": "Unauthorized"}), 401

    session["user_id"] = user.id

    return jsonify({
        "id": user.id,
        "firstname": user.firstname,
        "lastname": user.lastname,
        "email": user.email
    }), 200


@app.route("/stockdata", methods=["POST"])
def fetch_stock_data():
    if finnhub_client is None:
        return jsonify({
            "error": "Stock data service is not configured"
        }), 503

    stock_data = []

    for symbol in symbols:
        try:
            data = finnhub_client.quote(symbol)

            current_price = data.get("c", 0)
            previous_close = data.get("pc", 0)
            change = data.get("dp", 0)

            if previous_close > current_price:
                change = -abs(change)

            stock_data.append({
                "symbol": symbol,
                "value": current_price,
                "change": change
            })

        except Exception:
            logging.exception(
                "Error fetching stock data for %s", symbol
            )

    if not stock_data:
        return jsonify({
            "error": "Unable to fetch stock data"
        }), 502

    return jsonify(stock_data), 200


@app.route("/api/backtest", methods=["POST"])
def backtest():
    data = request.get_json(silent=True) or {}

    strategy = data.get("strategy")
    symbol = data.get("sym")
    cash = data.get("cash")
    period = data.get("period")

    if any(value is None or value == "" for value in [
        strategy, symbol, cash, period
    ]):
        return jsonify({
            "error": "Missing backtest parameters"
        }), 400

    try:
        result = run_backtest(strategy, symbol, cash, period)
        return jsonify(result), 200

    except ValueError as e:
        logging.warning("Backtest validation error: %s", e)
        return jsonify({"error": str(e)}), 400

    except Exception:
        logging.exception("Backtest failed")
        return jsonify({
            "error": "An error occurred during backtesting"
        }), 500


@app.route("/liveChart", methods=["POST"])
def liveChart():
    data = request.get_json(silent=True) or {}
    symbol = data.get("symbol1")

    if not symbol:
        return jsonify({
            "error": "Missing 'symbol1' in request body"
        }), 400

    try:
        result = live_Chart(symbol)
        return jsonify(result), 200

    except ValueError as e:
        logging.warning("Live chart validation error: %s", e)
        return jsonify({"error": str(e)}), 400

    except Exception:
        logging.exception("Live chart request failed")
        return jsonify({
            "error": "Failed to fetch live chart data"
        }), 500


@app.route("/companyinfo", methods=["POST"])
def companyInfo():
    data = request.get_json(silent=True) or {}
    symbol = data.get("symbol")

    if not symbol:
        return jsonify({
            "error": "Missing 'symbol' in request body"
        }), 400

    try:
        result = company_Info(symbol)
        return jsonify(result), 200

    except ValueError as e:
        logging.warning("Company info validation error: %s", e)
        return jsonify({"error": str(e)}), 400

    except Exception:
        logging.exception("Company info request failed")
        return jsonify({
            "error": "Failed to fetch company info"
        }), 500


# --------------------------------------------------
# Local development
# --------------------------------------------------

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False
    )