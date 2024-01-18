import requests, json
from flask import render_template, redirect, url_for, request, session, jsonify
from config import app, mysql
from datetime import datetime
import random

#################### UPDATED TO CHECK PULL PUSH GIT ###############
############ Second Check ############
######### VIEW FUNCTIONS ##########

to_reload = False

@app.route('/',methods=['GET','POST'])
def index():
    # if "farmer_id" in session.keys():
    farmer_id = session.get("farmer_id")
    # if "buyer_id" in session.keys():
    buyer_id = session.get("buyer_id")
    if not farmer_id and not buyer_id:
        return render_template('index.html')
    return render_template('index.html', farmer_id=farmer_id, buyer_id=buyer_id)


@app.route('/logout',methods=['GET','POST'])
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/farmer_login',methods=['GET','POST'])
def farmer_login():
    if request.method != 'POST':
        return render_template('farmer_login.html')
    
    data = request.get_json()['data']
    user_data = {}
    for i in data:
        user_data[i['name']] = str(i['value'])
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM user_account WHERE username = %s AND password = %s", (user_data['username'], user_data['password']))
    user = cur.fetchone()
    f_user = cur.execute("SELECT * FROM user_account WHERE username = %s AND password = %s AND role = 'farmer'", (user_data['username'], user_data['password']))
    if not user:
        return jsonify({"success":False, "message":"Invalid username or password"})
    if not f_user:
        return jsonify({"success":False, "message":"You are not a farmer"})
    session['farmer_id'] = user[0]
    return jsonify({"success":True, "message":"Login successful", "category":user[3]})

@app.route('/buyer_login',methods=['GET','POST'])
def buyer_login():
    if request.method != 'POST':
        return render_template('buyer_login.html')
    
    data = request.get_json()['data']
    user_data = {}
    for i in data:
        user_data[i['name']] = str(i['value'])
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM user_account WHERE username = %s AND password = %s", (user_data['username'], user_data['password']))
    user = cur.fetchone()
    c_user = cur.execute("SELECT * FROM user_account WHERE username = %s AND password = %s AND role = 'customer'", (user_data['username'], user_data['password']))
    print(user)
    if not user:
        return jsonify({"success":False, "message":"Invalid username or password"})
    if not c_user:
        return jsonify({"success":False, "message":"You are not a buyer"})
    session['buyer_id'] = user[0]
    return jsonify({"success":True, "message":"Login successful", "category":user[3]})

@app.route('/signup',methods=['GET','POST'])
def signup():
    if request.method != 'POST':
        return render_template('signup.html')

@app.route('/profile',methods=['GET','POST'])
def profile():
    # user_id = session.get('user_id')
    if 'farmer_id' not in session.keys() and 'buyer_id' not in session.keys():
        return redirect(url_for('farmer_login'))
    
    farmer_id = session.get('farmer_id')
    buyer_id = session.get('buyer_id')
    
    cur = mysql.connection.cursor()
    if farmer_id:
        cur.execute("SELECT * FROM farmer WHERE UserAccountID = %s", (farmer_id,))
        user = cur.fetchone()
        user = {
            'name': user[1],
            'location': user[2],
            'phone': user[3],
            'email': user[4],
            'farm_size': user[5],
            'farming_experience': user[6]
        }
    elif buyer_id:
        cur.execute("SELECT * FROM buyer WHERE UserAccountID = %s", (buyer_id,))
        user = cur.fetchone()
        user = {
            'name': user[1],
            'location': user[2],
            'phone': user[3],
            'email': user[4],
        }
    print(user)
    
    return render_template('profile.html', user=user, farmer_id=farmer_id, buyer_id=buyer_id)

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

    cur.execute("SELECT * from user_account where username = %s and password = %s", (user_data['username'], user_data['password']))
    user = cur.fetchone()
    if user:
        return jsonify({"success":False, "message":"User already exists"})


    cur.execute("INSERT INTO user_account (username, password, role) values (%s, %s, %s)", (user_data['username'], user_data['password'], user_data['category']))
    mysql.connection.commit()
    user_id = cur.lastrowid

    # session['user_id'] = user_id

    if user_data['category'] == 'farmer':
        cur.execute("INSERT INTO farmer (Name, Location, ContactPhone, ContactEmail, FarmSize, FarmingExperience, UserAccountID) VALUES (%s, %s, %s, %s, %s, %s, %s)", (user_data['username'], '', user_data['phone'], user_data['email'], 0, 0, user_id))
    elif user_data['category'] == 'customer':
        cur.execute("INSERT INTO buyer (Name, Location, ContactPhone, ContactEmail, UserAccountID) VALUES (%s, %s, %s, %s, %s)", (user_data['username'], '', user_data['phone'], user_data['email'], user_id))
    mysql.connection.commit()

    return jsonify({"success":True, 'message':'User created successfully', "category":user_data['category']})


@app.route("/products", methods=['GET', 'POST'])
def products():
    user_id = session.get('user_id')
    farmer_id = session.get('farmer_id')
    buyer_id = session.get('buyer_id')
    return render_template('product.html', farmer_id=farmer_id, buyer_id=buyer_id)

@app.route("/farmer", methods=['GET', 'POST'])
def farmer():
    return render_template('farmer.html')

@app.route("/buyer", methods=['GET', 'POST'])
def buyer():
    if 'buyer_id' not in session.keys():
        return redirect(url_for('farmer_login'))
    buyer_id = session.get('buyer_id')
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM buyer WHERE UserAccountID = %s", (buyer_id,))
    user = cur.fetchone()
    user = {
        'name': user[1],
        'location': user[2],
        'phone': user[3],
        'email': user[4],
    } 
    return render_template('buyer.html', user=user)

@app.route("/buyer/update", methods=['GET', 'POST'])
def buyer_update():
    if 'buyer_id' not in session.keys():
        return redirect(url_for('buyer_login'))
    if request.method != 'POST':
        return redirect(url_for('index'))
    buyer_id = session.get('buyer_id')
    data = request.get_json()['data']
    user_data = {}
    for i in data:
        user_data[i['name']] = str(i['value'])
    cur = mysql.connection.cursor()
    cur.execute("UPDATE buyer SET NAME = %s, Location = %s, ContactPhone = %s, ContactEmail = %s WHERE UserAccountID = %s", (user_data['name'], user_data['address'], user_data['phone_number'], user_data['email'], buyer_id))
    mysql.connection.commit()
    mysql.connection.close()
    return jsonify({"success":True, "message":"Profile updated successfully"})
    # return render_template('buyer_update.html', user=user)

@app.route("/checkout", methods=['GET', 'POST'])
def checkout():
    if request.method != 'POST':
        return redirect(url_for('index'))
    
    if 'farmer_id' not in session.keys() and 'buyer_id' not in session.keys():
        return redirect(url_for('farmer_login'))
    
    data = request.get_json()['data']
    print(data)
    return render_template('checkout.html', data=data)

@app.route("/pinvoice", methods=['GET', 'POST'])
def pinvoice():

    if 'buyer_id' not in session.keys() and 'farmer_id' not in session.keys():
        return redirect(url_for('farmer_login'))
    
    data = session.get("checkout_data")
    date = datetime.now().strftime("%d/%m/%Y")
    data['date'] = date
    data['invoice_number'] = "INV-"+ str(random.randint(10000, 99999))
    for i in data['products']:
        i['product_price'], i['product_quantity'] = int(i['product_price']), int(i['product_quantity'])
    print(data)
    return render_template('invoice.html', data=data)

@app.route("/invoice", methods=['GET', 'POST'])
def invoice():
    if request.method != 'POST':
        return redirect(url_for('index'))
    if 'buyer_id' not in session.keys() and 'farmer_id' not in session.keys():
        return redirect(url_for('farmer_login'))
    data = request.get_json()['data']
    session["checkout_data"] = data
    return {
        "success":True
    }

if __name__ == '__main__':
    app.run(debug=True)