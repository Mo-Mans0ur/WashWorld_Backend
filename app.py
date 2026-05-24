import os

from flask import Flask, jsonify, render_template, request

from routes.auth_api import bp as auth_api_bp
from routes.locations_api import bp as locations_api_bp
from routes.users_api import bp as users_api_bp
from routes.subscriptions_api import bp as subscriptions_api_bp
from routes.cars_api import bp as cars_api_bp
from routes.wash_log_api import bp as wash_log_api_bp
from routes.offers_api import bp as offers_api_bp

app = Flask(__name__)


@app.before_request
def handle_options():
    if request.method == "OPTIONS":
        from routes.api_common import apply_cors
        return apply_cors(jsonify({}))
app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY",
    "washworld-dev-secret-change-me",
)

app.register_blueprint(locations_api_bp)
app.register_blueprint(auth_api_bp)
app.register_blueprint(users_api_bp)
app.register_blueprint(subscriptions_api_bp)
app.register_blueprint(cars_api_bp)
app.register_blueprint(wash_log_api_bp)
app.register_blueprint(offers_api_bp)


@app.route('/')
def index():
    return render_template('dashboard.html')