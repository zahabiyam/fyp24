import os
from flask import Flask
from flask_mysqldb import MySQL


app = Flask(__name__)
app.config['SECRET_KEY'] = 'MyKey'


mysql=MySQL(app)
app.config['MYSQL_HOST'] = '192.168.10.4'
app.config['MYSQL_USER'] = 'admin'
app.config['MYSQL_PASSWORD'] = 'Admin!123'
app.config['MYSQL_DB'] = 'farmer_friend'
app.config['MYSQL_PORT'] = 3307


basedir = os.path.abspath(os.path.dirname(__file__))