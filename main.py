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
    user_id = session.get('user_id')
    if not user_id:
        return render_template('index.html')
    return render_template('index.html', user_id=user_id)
    

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method != 'POST':
        return render_template('login.html')
    
    data = request.get_json()['data']
    user_data = {}
    for i in data:
        user_data[i['name']] = str(i['value'])
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM user_account WHERE username = %s AND password = %s", (user_data['username'], user_data['password']))
    user = cur.fetchone()
    print(user)
    if not user:
        return jsonify({"success":False, "message":"Invalid username or password"})
    session['user_id'] = user[0]
    return jsonify({"success":True, "message":"Login successful", "category":user[3]})

@app.route('/signup',methods=['GET','POST'])
def signup():
    if request.method != 'POST':
        return render_template('signup.html')

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
    cur.execute("INSERT INTO user_account (username, password, role) values (%s, %s, %s)", (user_data['username'], user_data['password'], user_data['category']))
    mysql.connection.commit()
    user_id = cur.lastrowid

    session['user_id'] = user_id

    if user_data['category'] == 'farmer':
        cur.execute("INSERT INTO farmer (Name, Location, ContactPhone, ContactEmail, FarmSize, FarmingExperience, UserAccountID) VALUES (%s, %s, %s, %s, %s, %s, %s)", (user_data['username'], '', user_data['phone'], user_data['email'], 0, 0, user_id))
        mysql.connection.commit()

    return jsonify({"success":True, 'message':'User created successfully', "category":user_data['category']})

@app.route("/products", methods=['GET', 'POST'])
def products():
    return render_template('product.html')

@app.route("/farmer", methods=['GET', 'POST'])
def farmer():
    return render_template('farmer.html')

@app.route("/profile", methods=['GET', 'POST'])
def profile():
    return render_template('profile.html')

if __name__ == '__main__':
    app.run(debug=True)