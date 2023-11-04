import os
from flask import Flask
from flask_mysqldb import MySQL


app = Flask(__name__)
app.config['SECRET_KEY'] = 'MyKey'


mysql=MySQL(app)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'farmer_friend'
app.config['MYSQL_PORT'] = 3306


basedir = os.path.abspath(os.path.dirname(__file__))