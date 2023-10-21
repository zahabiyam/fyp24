import os
from flask import Flask
import mysql


app = Flask(__name__)
app.config['SECRET_KEY'] = 'MyKey'


# mysql=MySQL(bd_report)
# bd_report.config['MYSQL_HOST'] = '182.188.46.104'
# bd_report.config['MYSQL_USER'] = 'admin'
# bd_report.config['MYSQL_PASSWORD'] = 'Admin!123'
# bd_report.config['MYSQL_DB'] = 'bd_report'
# bd_report.config['MYSQL_PORT'] = 3307


basedir = os.path.abspath(os.path.dirname(__file__))