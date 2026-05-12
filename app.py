from flask import Flask, render_template, request

from routes.locations_api import bp as locations_api_bp

app = Flask(__name__)

app.register_blueprint(locations_api_bp)


@app.route('/')
def index():
    return render_template('dashboard.html')