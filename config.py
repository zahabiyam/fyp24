import os
from flask import Flask
from flask_mysqldb import MySQL


app = Flask(__name__)
app.config['SECRET_KEY'] = 'MyKey'


os.environ["API_KEY"] = "7704d000af68868d3284bb7b620104ae"
mysql=MySQL(app)
# app.config['MYSQL_HOST'] = '192.168.10.4'
app.config['MYSQL_HOST'] = '182.188.46.104'
app.config['MYSQL_USER'] = 'admin'
app.config['MYSQL_PASSWORD'] = 'Admin!123'
app.config['MYSQL_DB'] = 'farmer_friend'
app.config['MYSQL_PORT'] = 3307


basedir = os.path.abspath(os.path.dirname(__file__))