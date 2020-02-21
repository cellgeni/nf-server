import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
auth_token = os.getenv("AUTH_TOKEN", "nfauthtoken")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
app.auth_token = auth_token
db = SQLAlchemy(app)
