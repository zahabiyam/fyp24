import requests, json
from flask import render_template, redirect, url_for, request, session, jsonify
from config import app, mysql
from datetime import datetime

#################### UPDATED TO CHECK PULL PUSH GIT ###############
############ Second Check ############
######### VIEW FUNCTIONS ##########

to_reload = False

@app.route('/',methods=['GET','POST'])
def index():
    return render_template('index.html')

@app.route('/login',methods=['GET','POST'])
def login():
    return render_template('login.html')

@app.route('/signup',methods=['GET','POST'])
def signup():
    if request.method != 'POST':
        return render_template('signup.html')
    data = request.get_json()
    print(data, request.get_data())

@app.route('/signup_farmer',methods=["GET","POST"])
def signup_farmer():
    
    if request.method != 'POST':
        return ''
    
    data = request.get_json()['data']
    user_data = {}
    
    for i in data:
        user_data[i['name']] = str(i['value'])

    if user_data['password'] != user_data['reenter-password']:
        return jsonify({"success":False, "message":"Passwords do not match"})
    
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO useraccount (username, password, role) values (%s, %s, %s)", (user_data['username'], user_data['password'], user_data['category']))
    mysql.connection.commit()
    user_id = cur.lastrowid
    if user_data['category'] == 'farmer':
        cur.execute("INSERT INTO farmer (Name, Location, ContactPhone, ContactEmail, FarmSize, FarmingExperience, UserAccountID) VALUES (%s, %s, %s, %s, %s, %s, %s)", (user_data['username'], '', user_data['phone'], user_data['email'], '', '', user_id))
        mysql.connection.commit()

    return jsonify({"success":True, 'message':'User created successfully', "category":user_data['category']})

@app.route("/products", methods=['GET', 'POST'])
def products():
    return render_template('product.html')

@app.route("/farmer", methods=['GET', 'POST'])
def farmer():
    return render_template('farmer.html')

if __name__ == '__main__':
    app.run(debug=True)