import os

from flask import Flask, render_template

from routes.auth_api import bp as auth_api_bp
from routes.locations_api import bp as locations_api_bp
from routes.users_api import bp as users_api_bp
from routes.subscriptions_api import bp as subscriptions_api_bp

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY",
    "washworld-dev-secret-change-me",
)

app.register_blueprint(locations_api_bp)
app.register_blueprint(auth_api_bp)
app.register_blueprint(users_api_bp)
app.register_blueprint(subscriptions_api_bp)


@app.route('/')
def index():
    return render_template('dashboard.html')