"""
The following URL was used to create the python backend: 
https://tms-dev-blog.com/python-backend-with-javascript-frontend-how-to/
"""

from flask import Flask, render_template
import requests
import json
import flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Root address of the backend
@app.route('/')
def hello_world():
    data = ''
    return render_template('index.html', dataToRender=data)

# Health-check endpoint
@app.route('/health', methods=["GET"])
def health():
    return "Hello World"