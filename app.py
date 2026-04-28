from flask import Flask, render_template, request
import os



app = Flask(__name__)


@app.route('/')
def index():
    return render_template('dashboard.html')