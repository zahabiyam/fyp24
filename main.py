import requests, json
from flask import render_template, redirect, url_for, request, session, jsonify
from config import app, mysql
from datetime import datetime
import random
from weather_helpers import coordinates, getweather, getaqi

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
        return render_template('farmer/farmer_login.html')
    
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
        return render_template('customer/buyer_login.html')
    
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
    profile_type = ""
    products = []
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
        profile_type = "Farmer"
        cur.execute("SELECT * FROM product WHERE FarmerID = %s", (farmer_id,))
        product_data = cur.fetchall()
        for i in product_data:
            products.append({
                'id': i[0],
                'name': i[1],
                'image_url': i[2],
                'description': i[3],
                'category': i[4],
                'price': i[5],
                'quantity': i[6],
                'farmer_id': i[7]
            })
    elif buyer_id:
        cur.execute("SELECT * FROM buyer WHERE UserAccountID = %s", (buyer_id,))
        user = cur.fetchone()
        user = {
            'name': user[1],
            'location': user[2],
            'phone': user[3],
            'email': user[4],
        }
        profile_type = "Buyer"
    print(user)
    
    return render_template('profile.html', user=user, farmer_id=farmer_id, buyer_id=buyer_id, profile_type=profile_type, products=products)

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
        cur.execute("INSERT INTO farmer (Name, Location, ContactPhone, ContactEmail, FarmSize, FarmingExperience, zipcode, UserAccountID) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (user_data['username'], '', user_data['phone'], user_data['email'], 0, 0, user_data['zipcode'],user_id))
    elif user_data['category'] == 'customer':
        cur.execute("INSERT INTO buyer (Name, Location, ContactPhone, ContactEmail, UserAccountID) VALUES (%s, %s, %s, %s, %s)", (user_data['username'], '', user_data['phone'], user_data['email'], user_id))
    mysql.connection.commit()

    return jsonify({"success":True, 'message':'User created successfully', "category":user_data['category']})


@app.route("/products", methods=['GET', 'POST'])
def products():
    farmer_id = session.get('farmer_id')
    buyer_id = session.get('buyer_id')
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM product")
    products = cur.fetchall()
    product_data = []
    for i in products:
        product_data.append({
            'id': i[0],
            'name': i[1],
            'image_url': i[2],
            'description': i[3],
            'category': i[4],
            'price': i[5],
            'quantity': i[6],
            'farmer_id': i[7]
        })
    print(product_data, buyer_id)
    return render_template('product.html', products=product_data, farmer_id=farmer_id, buyer_id=buyer_id)


@app.route("/chat", methods=['GET', 'POST'])
def chat():
    if request.method == 'POST':
        data = request.get_json()['data']
        print(data)
        try:        
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO chat (product_id, sender_id, receiver_id, message, sent_at, sender_type) VALUES (%s, %s, %s, %s, %s, %s)", (data['product_id'], data['sender_id'], data['receiver_id'], data['message'], datetime.now(), data['sender_type']))
            mysql.connection.commit()
        except Exception as e:
            print(e)
            return jsonify({"success":False, "message":"Message not sent"})
        return jsonify({"success":True, "message":"Message sent successfully"})
    
    product_id = request.args.get('product_id')
    buyer_id = request.args.get('buyer_id')
    cur = mysql.connection.cursor()
    
    
    # cur.execute("SELECT * FROM chat WHERE product_id = %s", (product_id,))
    # chats = cur.fetchall()
    query = f"""
        SELECT c.product_id,p.name,c.`sender_type`,c.`sender_id`,c.`receiver_id`,ua.username AS sender_name,
        uc.username AS reciever_name, c.`message`
        FROM chat c
        JOIN user_account ua
        ON ua.id=c.sender_id
        JOIN product p
        ON c.product_id=p.`id`
        JOIN user_account uc
        ON uc.id=c.`receiver_id`
        WHERE (c.`receiver_id` = {buyer_id} OR c.`sender_id` = {buyer_id} ) AND p.id = {product_id};
    """
    cur.execute(query)
    chats = cur.fetchall()

    chat_data = []
    for i in chats:
        chat_data.append({
            'product_id': i[0],
            'product_name': i[1],
            'sender_type': i[2],
            'sender_id': i[3],
            'receiver_id': i[4],
            'sender_name': i[5],
            'receiver_name': i[6],
            'message': i[7]
        })
    return jsonify(chat_data)

@app.route("/farmer", methods=['GET', 'POST'])
def farmer():
    return render_template('farmer/farmer.html')

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
    return render_template('customer/buyer.html', user=user)

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
    return jsonify({"success":True, "message":"Profile updated successfully"})
    # return render_template('buyer_update.html', user=user)

@app.route("/file_upload", methods=['GET', 'POST'])
def file_upload():
    print("here")
    attachment_file = request.files.get("file")
    filename = attachment_file.filename
    file_url = "static/uploads/"+filename
    attachment_file.save("static/uploads/"+filename)
    return jsonify({"success":True, "message":"File uploaded successfully", "file_url":file_url})

@app.route("/product_delete", methods=['POST'])
def product_delete():
    if 'farmer_id' not in session.keys():
        return redirect(url_for('farmer_login'))
    product_id = request.args.get('product_id')
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM product WHERE id = %s", (product_id,))
    mysql.connection.commit()
    return jsonify({"success":True, "message":"Product deleted successfully"})

@app.route("/product_update", methods=['GET', 'POST'])
def product_update():
    print(session.keys())
    if 'farmer_id' not in session.keys():
        return redirect(url_for('farmer_login'))
    if request.method != 'POST':
        product_id = request.args.get('product_id')
        print(product_id)
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM product WHERE id = %s", (product_id,))
        product = cur.fetchone()
        products = {
            'id': product[0],
            'name': product[1],
            'image_url': product[2],
            'description': product[3],
            'category': product[4],
            'price': product[5],
            'quantity': product[6],
            'farmer_id': product[7]
        }
        return render_template('farmer/product_update.html', products=products, farmer_id=product[7])
    
    data = request.get_json()['data']
    user_data = {}
    for i in data:
        user_data[i['name']] = str(i['value'])
    farmer_id = session.get('farmer_id')
    print(user_data)
    
    cur = mysql.connection.cursor()
    cur.execute("UPDATE product SET Name = %s, image_url = %s, Description = %s, Category = %s, Price = %s, QuantityAvailable = %s WHERE FarmerID = %s", (user_data['product_name'], user_data['product_image_url'], user_data['product_description'], '', int(user_data['product_price']), int(user_data['product_quantity']), int(farmer_id)))
    mysql.connection.commit()
    return jsonify({"success":True, "message":"Product updated successfully"})
    # return render_template('farmer/product_update.html')

@app.route("/product_add", methods=['GET', 'POST'])
def product_add():
    if request.method == 'POST':
        data = request.get_json()['data']
        user_data = {}
        for i in data:
            user_data[i['name']] = str(i['value'])
        farmer_id = session.get('farmer_id')
        print(user_data)
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO product (Name, image_url, Description, Category, Price, QuantityAvailable, FarmerID) VALUES (%s, %s, %s, %s, %s, %s, %s)", (user_data['product_name'], user_data['product_image_url'], user_data['product_description'], '', int(user_data['product_price']), int(user_data['product_quantity']), int(farmer_id)))
        mysql.connection.commit()
        return jsonify({"success":True, "message":"Product added successfully"})

    if 'farmer_id' not in session.keys():
        return redirect(url_for('farmer_login'))
    farmer_id = session.get('farmer_id')
    return render_template('farmer/product_add.html', farmer_id=farmer_id)

@app.route("/checkout", methods=['GET', 'POST'])
def checkout():
    if request.method != 'POST':
        return redirect(url_for('index'))
    
    if 'buyer_id' not in session.keys():
        return redirect(url_for('buyer_login'))
    
    data = request.get_json()['data']
    print(data)
    return render_template('buyer/checkout.html', data=data)

@app.route("/invoice", methods=['GET', 'POST'])
def invoice():

    if 'buyer_id' not in session.keys() and 'farmer_id' not in session.keys():
        return redirect(url_for('farmer_login'))
    
    data = session.get("checkout_data")
    date = datetime.now().strftime("%d/%m/%Y")
    data['date'] = date
    data['invoice_number'] = "INV-"+ str(random.randint(10000, 99999))
    for i in data['products']:
        i['product_price'], i['product_quantity'] = int(i['product_price']), int(i['product_quantity'])
    print(data)
    return render_template('buyer/invoice.html', data=data)

@app.route("/pinvoice", methods=['GET', 'POST'])
def pinvoice():
    if request.method != 'POST':
        return redirect(url_for('index'))
    if 'buyer_id' not in session.keys() and 'farmer_id' not in session.keys():
        return redirect(url_for('farmer_login'))
    data = request.get_json()['data']
    session["checkout_data"] = data
    return {
        "success":True
    }

@app.route("/farmer_chat", methods=['GET', 'POST'])
def farmer_chat(): 
    farmer_id = session.get('farmer_id')
    if not farmer_id:
        return redirect(url_for('farmer_login'))
    
    query = f"""
        SELECT c.product_id,p.name,c.`sender_type`,c.`sender_id`,c.`receiver_id`,ua.username AS sender_name,
        uc.username AS reciever_name, c.`message`
        FROM chat c
        JOIN user_account ua
        ON ua.id=c.sender_id
        JOIN product p
        ON c.product_id=p.`id`
        JOIN user_account uc
        ON uc.id=c.`receiver_id`
        WHERE c.`receiver_id` = {farmer_id} OR c.`sender_id` = {farmer_id}
    """

    cur = mysql.connection.cursor()
    cur.execute(query)
    chats = cur.fetchall()
    chat_data = {}
    for product_id, product_name, sender_type, sender_id, receiver_id, sender_name, receiver_name, message in chats:
        if product_id not in chat_data:
            chat_data[product_id] = {
                "product_name": product_name,
                "customer_chats": {}
            }

        customer_id = receiver_id if sender_type == "farmer" else sender_id
        customer_name = receiver_name if sender_type == "farmer" else sender_name

        if customer_id not in chat_data[product_id]["customer_chats"]:
            chat_data[product_id]["customer_chats"][customer_id] = {
                "customer_name": customer_name,
                "messages": [],
            }

        chat_data[product_id]["customer_chats"][customer_id]["messages"].append({
            "message": message,
            "sender": sender_name,
            "receiver": receiver_name,
            "sender_type": sender_type
        })
    # make a list of chats based on product and customers
    print(json.dumps(chat_data, indent=4))

    # print(chats)
    
    return render_template('chat.html', chats=chat_data, range=range, len=len, farmer_id=farmer_id)


@app.route("/farmer/get_full_weather", methods=["GET", "POST"])
def full_weather():

    farmer_id = session.get('farmer_id')
    if not farmer_id:
        return redirect(url_for('farmer_login'))    

    cur = mysql.connection.cursor()
    cur.execute("SELECT zipcode FROM farmer WHERE UserAccountID = %s", (farmer_id,))
    zipcode = cur.fetchone()[0]

    zipcode = int(zipcode)
    units = "imperial" # request.form.get("units")

    # Get latitude and longitude for zipcode
    # latlong = coordinates(zipcode)
    # lat = latlong["lat"]
    # lon = latlong["lon"]

    # Get weather by latitude and longitude
    # weather = getweather(lat, lon, units)
    # aqi = getaqi(lat, lon)
    weather = {'lat': 24.8608, 'lon': 67.0104, 'tz': '+05:00', 'date': '2024-03-13', 'units': 'standard', 'cloud_cover': {'afternoon': 0.0}, 'humidity': {'afternoon': 35.97}, 
'precipitation': {'total': 0.0}, 'temperature': {'min': 295.26, 'max': 299.82, 'afternoon': 299.18, 'night': 295.58, 'evening': 298.45, 'morning': 295.26}, 'pressure': {'afternoon': 1015.2}, 'wind': {'max': {'speed': 9.68, 'direction': 272.46}}}

    aqi = {'coord': {'lon': 67.0104, 'lat': 24.8608}, 'list': [{'main': {'aqi': 3}, 'components': {'co': 283.72, 'no': 0.54, 'no2': 3, 'o3': 135.9, 'so2': 4.83, 'pm2_5': 21.8, 'pm10': 93.02, 'nh3': 2.03}, 'dt': 1710324000}, {'main': {'aqi': 3}, 'components': {'co': 297.07, 'no': 0.62, 'no2': 3.64, 'o3': 130.18, 'so2': 3.13, 'pm2_5': 16.78, 'pm10': 66.64, 'nh3': 2.34}, 'dt': 1710327600}, {'main': {'aqi': 3}, 'components': {'co': 317.1, 'no': 0.7, 'no2': 5.06, 'o3': 121.59, 'so2': 2.5, 'pm2_5': 12.68, 'pm10': 51.5, 'nh3': 2.63}, 'dt': 1710331200}, {'main': {'aqi': 3}, 'components': {'co': 407.22, 'no': 0.66, 'no2': 10.54, 'o3': 113.01, 'so2': 3.46, 'pm2_5': 17.2, 'pm10': 70.32, 'nh3': 4.56}, 'dt': 1710334800}, {'main': {'aqi': 3}, 'components': {'co': 494, 'no': 0.07, 'no2': 14.91, 'o3': 105.86, 'so2': 4.35, 'pm2_5': 23.7, 'pm10': 90.28, 'nh3': 7.22}, 'dt': 1710338400}, {'main': {'aqi': 4}, 'components': {'co': 547.41, 'no': 0, 'no2': 15.42, 'o3': 103, 'so2': 4.83, 'pm2_5': 29.38, 'pm10': 104.97, 'nh3': 8.87}, 'dt': 1710342000}, {'main': {'aqi': 4}, 'components': {'co': 560.76, 'no': 0, 'no2': 15.25, 'o3': 101.57, 'so2': 
5.25, 'pm2_5': 34.54, 'pm10': 119.14, 'nh3': 9.88}, 'dt': 1710345600}, {'main': {'aqi': 4}, 'components': {'co': 467.3, 'no': 0, 'no2': 12, 'o3': 101.57, 'so2': 
5.07, 'pm2_5': 29.77, 'pm10': 103.13, 'nh3': 9.25}, 'dt': 1710349200}, {'main': {'aqi': 3}, 'components': {'co': 370.5, 'no': 0, 'no2': 11.82, 'o3': 97.28, 'so2': 20.03, 'pm2_5': 22.47, 'pm10': 81.9, 'nh3': 7.79}, 'dt': 1710352800}, {'main': {'aqi': 3}, 'components': {'co': 303.75, 'no': 0, 'no2': 10.37, 'o3': 98.71, 'so2': 21.46, 'pm2_5': 20.46, 'pm10': 82.71, 'nh3': 5.76}, 'dt': 1710356400}, {'main': {'aqi': 3}, 'components': {'co': 293.73, 'no': 0, 'no2': 7.54, 'o3': 104.43, 
'so2': 13.95, 'pm2_5': 20.48, 'pm10': 80.63, 'nh3': 5.32}, 'dt': 1710360000}, {'main': {'aqi': 3}, 'components': {'co': 283.72, 'no': 0, 'no2': 6.77, 'o3': 105.86, 'so2': 14.78, 'pm2_5': 18.55, 'pm10': 72.58, 'nh3': 5.38}, 'dt': 1710363600}, {'main': {'aqi': 3}, 'components': {'co': 290.39, 'no': 0, 'no2': 6.86, 'o3': 103, 'so2': 14.66, 'pm2_5': 17.9, 'pm10': 66.04, 'nh3': 7.47}, 'dt': 1710367200}, {'main': {'aqi': 3}, 'components': {'co': 307.08, 'no': 0, 'no2': 6.77, 'o3': 98.71, 'so2': 11.68, 'pm2_5': 18.03, 'pm10': 62.23, 'nh3': 10.13}, 'dt': 1710370800}, {'main': {'aqi': 3}, 'components': {'co': 333.79, 'no': 0, 'no2': 7.37, 'o3': 
92.98, 'so2': 8.35, 'pm2_5': 18.39, 'pm10': 58.68, 'nh3': 12.16}, 'dt': 1710374400}, {'main': {'aqi': 3}, 'components': {'co': 410.56, 'no': 0, 'no2': 10.28, 'o3': 84.4, 'so2': 6.68, 'pm2_5': 20.4, 'pm10': 57.18, 'nh3': 15.2}, 'dt': 1710378000}, {'main': {'aqi': 3}, 'components': {'co': 741.01, 'no': 0, 'no2': 25.36, 'o3': 58.65, 'so2': 8.23, 'pm2_5': 33.03, 'pm10': 68.94, 'nh3': 22.8}, 'dt': 1710381600}, {'main': {'aqi': 4}, 'components': {'co': 1255.04, 'no': 5.81, 'no2': 45.24, 'o3': 29.68, 'so2': 11.44, 'pm2_5': 50.25, 'pm10': 87.62, 'nh3': 29.64}, 'dt': 1710385200}, {'main': {'aqi': 4}, 'components': {'co': 1548.77, 'no': 15.87, 'no2': 43.87, 'o3': 40.05, 'so2': 13.23, 'pm2_5': 57.23, 'pm10': 94.25, 'nh3': 30.65}, 'dt': 1710388800}, {'main': {'aqi': 3}, 'components': {'co': 1281.74, 'no': 
10.39, 'no2': 33.93, 'o3': 77.25, 'so2': 11.92, 'pm2_5': 47.08, 'pm10': 80.84, 'nh3': 25.33}, 'dt': 1710392400}, {'main': {'aqi': 3}, 'components': {'co': 907.9, 'no': 4.97, 'no2': 20.91, 'o3': 115.87, 'so2': 9.54, 'pm2_5': 33.13, 'pm10': 65.61, 'nh3': 18.75}, 'dt': 1710396000}, {'main': {'aqi': 3}, 'components': {'co': 
417.23, 'no': 1.27, 'no2': 6.43, 'o3': 137.33, 'so2': 5.25, 'pm2_5': 15.97, 'pm10': 47.55, 'nh3': 7.28}, 'dt': 1710399600}, {'main': {'aqi': 4}, 'components': {'co': 390.53, 'no': 1.19, 'no2': 5.91, 'o3': 140.19, 'so2': 4.77, 'pm2_5': 14.2, 'pm10': 42.8, 'nh3': 5.76}, 'dt': 1710403200}, {'main': {'aqi': 4}, 'components': {'co': 397.21, 'no': 1.27, 'no2': 6.43, 'o3': 141.62, 'so2': 4.83, 'pm2_5': 13.22, 'pm10': 37.35, 'nh3': 5.57}, 'dt': 1710406800}, {'main': {'aqi': 4}, 'components': {'co': 397.21, 'no': 1.27, 'no2': 6.94, 'o3': 143.05, 'so2': 5.07, 'pm2_5': 12.49, 'pm10': 32.84, 'nh3': 5.64}, 'dt': 1710410400}, {'main': {'aqi': 4}, 'components': {'co': 407.22, 'no': 1.27, 'no2': 7.88, 'o3': 140.19, 'so2': 5.19, 'pm2_5': 12.13, 'pm10': 30.41, 'nh3': 5.89}, 'dt': 1710414000}, {'main': {'aqi': 3}, 'components': {'co': 427.25, 'no': 1.22, 'no2': 10.11, 'o3': 135.9, 'so2': 5.19, 'pm2_5': 12.1, 'pm10': 29.31, 'nh3': 6.33}, 'dt': 1710417600}, {'main': {'aqi': 3}, 'components': {'co': 847.82, 'no': 1.98, 'no2': 32.9, 'o3': 104.43, 'so2': 8.11, 'pm2_5': 21.56, 'pm10': 40.13, 'nh3': 13.17}, 'dt': 1710421200}, {'main': 
{'aqi': 3}, 'components': {'co': 1335.14, 'no': 0.3, 'no2': 56.89, 'o3': 65.8, 'so2': 11.8, 'pm2_5': 39.05, 'pm10': 61.12, 'nh3': 23.81}, 'dt': 1710424800}, {'main': {'aqi': 4}, 'components': {'co': 1575.47, 'no': 0, 'no2': 61.01, 'o3': 51.5, 'so2': 14.31, 'pm2_5': 54.81, 'pm10': 80.46, 'nh3': 31.41}, 'dt': 1710428400}, 
{'main': {'aqi': 4}, 'components': {'co': 1628.88, 'no': 0, 'no2': 57.58, 'o3': 50.78, 'so2': 15.14, 'pm2_5': 64.65, 'pm10': 93.2, 'nh3': 34.45}, 'dt': 1710432000}, {'main': {'aqi': 4}, 'components': {'co': 1575.47, 'no': 0, 'no2': 50.72, 'o3': 51.5, 'so2': 14.54, 'pm2_5': 68.27, 'pm10': 98.19, 'nh3': 35.47}, 'dt': 1710435600}, {'main': {'aqi': 4}, 'components': {'co': 1335.14, 'no': 0, 'no2': 42.84, 'o3': 54.36, 'so2': 12.04, 'pm2_5': 58.81, 'pm10': 88.62, 'nh3': 31.92}, 'dt': 
1710439200}, {'main': {'aqi': 3}, 'components': {'co': 934.6, 'no': 0, 'no2': 31.19, 'o3': 64.37, 'so2': 8.35, 'pm2_5': 40.36, 'pm10': 68.54, 'nh3': 24.57}, 'dt': 1710442800}, {'main': {'aqi': 3}, 'components': {'co': 654.22, 'no': 0, 'no2': 18.51, 'o3': 80.82, 'so2': 6.14, 'pm2_5': 30.52, 'pm10': 57, 'nh3': 21.03}, 'dt': 1710446400}, {'main': {'aqi': 3}, 'components': {'co': 527.38, 'no': 0, 'no2': 11.31, 'o3': 92.98, 'so2': 5.13, 'pm2_5': 26.81, 'pm10': 51.14, 'nh3': 19.25}, 'dt': 1710450000}, {'main': {'aqi': 3}, 'components': {'co': 473.98, 'no': 0, 'no2': 8.23, 'o3': 100.14, 'so2': 4.53, 'pm2_5': 24.56, 'pm10': 47.26, 'nh3': 17.99}, 'dt': 1710453600}, {'main': {'aqi': 3}, 'components': {'co': 453.95, 'no': 0, 'no2': 7.37, 'o3': 100.14, 'so2': 4.29, 'pm2_5': 23.78, 'pm10': 46.01, 'nh3': 17.48}, 'dt': 1710457200}, {'main': {'aqi': 3}, 'components': {'co': 447.27, 'no': 0, 'no2': 7.45, 'o3': 100.14, 'so2': 4.17, 'pm2_5': 23.26, 'pm10': 45.46, 'nh3': 
17.23}, 'dt': 1710460800}, {'main': {'aqi': 2}, 'components': {'co': 473.98, 'no': 0, 'no2': 9.25, 'o3': 97.28, 'so2': 4.29, 'pm2_5': 23.86, 'pm10': 46.65, 'nh3': 17.73}, 'dt': 1710464400}, {'main': {'aqi': 3}, 'components': {'co': 734.33, 'no': 0, 'no2': 21.25, 'o3': 82.97, 'so2': 6.38, 'pm2_5': 32.26, 'pm10': 56.71, 'nh3': 21.28}, 'dt': 1710468000}, {'main': {'aqi': 3}, 'components': {'co': 1054.76, 'no': 1.72, 'no2': 38.04, 'o3': 65.09, 'so2': 8.7, 'pm2_5': 40.85, 'pm10': 67.05, 'nh3': 24.07}, 'dt': 1710471600}, {'main': {'aqi': 3}, 'components': {'co': 1228.33, 'no': 7.1, 'no2': 38.73, 'o3': 70.1, 'so2': 10.25, 'pm2_5': 45.38, 'pm10': 72.97, 'nh3': 25.33}, 'dt': 1710475200}, {'main': {'aqi': 3}, 'components': {'co': 1188.28, 'no': 7.82, 'no2': 32.9, 'o3': 90.84, 'so2': 11.09, 'pm2_5': 46.6, 'pm10': 75.12, 'nh3': 25.33}, 'dt': 1710478800}, {'main': {'aqi': 3}, 'components': {'co': 1054.76, 'no': 5.59, 'no2': 26.05, 'o3': 124.45, 'so2': 11.56, 'pm2_5': 45.11, 'pm10': 73.17, 'nh3': 23.56}, 'dt': 1710482400}, {'main': {'aqi': 4}, 'components': {'co': 534.06, 'no': 1.41, 'no2': 8.4, 'o3': 158.79, 'so2': 9.06, 'pm2_5': 32.79, 'pm10': 57.15, 'nh3': 10.51}, 'dt': 1710486000}, {'main': {'aqi': 4}, 'components': {'co': 494, 'no': 1.2, 'no2': 7.37, 'o3': 168.8, 'so2': 9.89, 
'pm2_5': 31.06, 'pm10': 52.63, 'nh3': 8.87}, 'dt': 1710489600}, {'main': {'aqi': 4}, 'components': {'co': 500.68, 'no': 1.24, 'no2': 8.05, 'o3': 173.09, 'so2': 10.97, 'pm2_5': 30.08, 'pm10': 50.31, 'nh3': 8.49}, 'dt': 1710493200}, {'main': {'aqi': 4}, 'components': {'co': 473.98, 'no': 1.16, 'no2': 8.23, 'o3': 175.95, 'so2': 11.44, 'pm2_5': 27.85, 'pm10': 47.03, 'nh3': 7.98}, 'dt': 1710496800}, {'main': {'aqi': 4}, 'components': {'co': 440.6, 'no': 1.03, 'no2': 8.31, 'o3': 171.66, 'so2': 11.09, 'pm2_5': 23.94, 'pm10': 42.05, 'nh3': 7.28}, 'dt': 1710500400}, {'main': {'aqi': 4}, 'components': {'co': 400.54, 'no': 0.82, 'no2': 8.82, 'o3': 161.65, 'so2': 10.85, 'pm2_5': 20.45, 'pm10': 38.03, 'nh3': 6.4}, 'dt': 1710504000}, {'main': {'aqi': 4}, 'components': {'co': 547.41, 'no': 0.78, 'no2': 18.68, 'o3': 140.19, 'so2': 13.23, 'pm2_5': 23.28, 'pm10': 40.83, 'nh3': 9.25}, 'dt': 1710507600}, {'main': {'aqi': 3}, 'components': {'co': 620.84, 'no': 0.06, 'no2': 21.94, 'o3': 125.89, 'so2': 11.56, 'pm2_5': 27.19, 'pm10': 42.5, 'nh3': 12.79}, 'dt': 1710511200}, {'main': {'aqi': 3}, 'components': {'co': 614.17, 'no': 0, 'no2': 18.68, 'o3': 121.59, 'so2': 7.99, 'pm2_5': 28.22, 'pm10': 41.95, 'nh3': 14.06}, 'dt': 1710514800}, {'main': {'aqi': 3}, 'components': {'co': 854.49, 'no': 0, 'no2': 25.71, 'o3': 105.86, 'so2': 8.23, 'pm2_5': 38.51, 'pm10': 53.47, 'nh3': 20.01}, 'dt': 1710518400}, {'main': {'aqi': 4}, 'components': {'co': 1134.87, 'no': 0, 'no2': 35.64, 'o3': 85.83, 'so2': 9.89, 'pm2_5': 52.82, 'pm10': 69.61, 'nh3': 27.61}, 'dt': 1710522000}, {'main': {'aqi': 4}, 'components': {'co': 1174.93, 'no': 0, 'no2': 39.07, 'o3': 75.82, 'so2': 9.54, 'pm2_5': 54.15, 'pm10': 70.79, 'nh3': 28.88}, 'dt': 1710525600}, {'main': {'aqi': 3}, 'components': {'co': 961.3, 'no': 0, 'no2': 34.62, 'o3': 74.39, 'so2': 7.33, 'pm2_5': 42.7, 'pm10': 57.59, 'nh3': 25.33}, 'dt': 1710529200}, {'main': {'aqi': 3}, 'components': {'co': 720.98, 'no': 0, 'no2': 24.33, 'o3': 77.96, 'so2': 5.6, 'pm2_5': 34.59, 'pm10': 48.67, 'nh3': 24.83}, 'dt': 1710532800}, {'main': {'aqi': 3}, 'components': {'co': 
620.84, 'no': 0, 'no2': 17.99, 'o3': 78.68, 'so2': 5.19, 'pm2_5': 32.63, 'pm10': 47.44, 'nh3': 26.85}, 'dt': 1710536400}, {'main': {'aqi': 3}, 'components': {'co': 567.44, 'no': 0, 'no2': 14.57, 'o3': 77.25, 'so2': 4.89, 'pm2_5': 31.15, 'pm10': 47.37, 'nh3': 28.88}, 'dt': 1710540000}, {'main': {'aqi': 3}, 'components': {'co': 560.76, 'no': 0, 'no2': 13.54, 'o3': 76.53, 'so2': 4.95, 'pm2_5': 31.15, 'pm10': 49.27, 'nh3': 30.65}, 'dt': 1710543600}, {'main': {'aqi': 3}, 'components': {'co': 594.14, 'no': 0, 'no2': 15.08, 'o3': 73.67, 'so2': 5.31, 'pm2_5': 33.03, 'pm10': 52.81, 'nh3': 32.42}, 'dt': 1710547200}, {'main': {'aqi': 3}, 'components': {'co': 747.68, 'no': 0, 'no2': 21.76, 'o3': 65.8, 'so2': 6.44, 'pm2_5': 39.65, 'pm10': 61.64, 'nh3': 35.97}, 'dt': 1710550800}, {'main': {'aqi': 4}, 'components': {'co': 1441.96, 'no': 0.33, 'no2': 51.41, 'o3': 29.68, 'so2': 10.49, 'pm2_5': 69.43, 'pm10': 95.82, 'nh3': 45.09}, 'dt': 1710554400}, {'main': {'aqi': 5}, 'components': {'co': 2536.77, 'no': 28.61, 'no2': 63.75, 'o3': 6.71, 'so2': 15.02, 'pm2_5': 108.34, 'pm10': 139.7, 'nh3': 52.69}, 'dt': 1710558000}, {'main': {'aqi': 5}, 'components': {'co': 3631.59, 'no': 61.69, 'no2': 67.17, 'o3': 16.09, 'so2': 19.79, 'pm2_5': 151.63, 'pm10': 188.31, 'nh3': 57.76}, 'dt': 1710561600}, 
{'main': {'aqi': 5}, 'components': {'co': 4058.84, 'no': 53.2, 'no2': 89.11, 'o3': 41.49, 'so2': 23.6, 'pm2_5': 187.48, 'pm10': 227.88, 'nh3': 58.77}, 'dt': 1710565200}, {'main': {'aqi': 5}, 'components': {'co': 3791.81, 'no': 24.59, 'no2': 101.45, 'o3': 124.45, 'so2': 24.08, 'pm2_5': 221.33, 'pm10': 262.94, 'nh3': 52.69}, 'dt': 1710568800}, {'main': {'aqi': 5}, 'components': {'co': 1134.87, 'no': 3.49, 'no2': 24.68, 'o3': 200.27, 'so2': 18.36, 'pm2_5': 79.23, 'pm10': 121.36, 'nh3': 16.72}, 'dt': 1710572400}, {'main': {'aqi': 5}, 'components': {'co': 934.6, 'no': 1.96, 'no2': 16.45, 'o3': 234.6, 'so2': 18.6, 'pm2_5': 81.46, 'pm10': 122.83, 'nh3': 14.69}, 'dt': 1710576000}, {'main': {'aqi': 5}, 'components': {'co': 847.82, 'no': 1.68, 'no2': 14.91, 'o3': 237.47, 'so2': 17.41, 'pm2_5': 73.17, 'pm10': 112.86, 'nh3': 13.68}, 'dt': 1710579600}, {'main': {'aqi': 4}, 'components': {'co': 520.71, 'no': 1.45, 'no2': 9.51, 'o3': 165.94, 'so2': 8.58, 'pm2_5': 31.92, 'pm10': 62.54, 'nh3': 7.03}, 'dt': 1710583200}, {'main': {'aqi': 4}, 'components': {'co': 453.95, 'no': 1.52, 'no2': 9.6, 'o3': 141.62, 'so2': 7.09, 'pm2_5': 19.86, 'pm10': 45.72, 'nh3': 5.26}, 'dt': 1710586800}, {'main': {'aqi': 3}, 'components': {'co': 467.3, 'no': 1.45, 'no2': 12, 'o3': 133.04, 'so2': 8.46, 'pm2_5': 18.29, 'pm10': 43.36, 'nh3': 4.88}, 'dt': 1710590400}, {'main': {'aqi': 3}, 'components': {'co': 988.01, 'no': 2.54, 'no2': 39.41, 'o3': 100.14, 'so2': 13.83, 'pm2_5': 31.49, 'pm10': 59.4, 'nh3': 12.54}, 'dt': 1710594000}, {'main': {'aqi': 3}, 'components': {'co': 1348.5, 'no': 0.33, 'no2': 58.95, 'o3': 72.24, 'so2': 
20.98, 'pm2_5': 48.9, 'pm10': 79.78, 'nh3': 20.01}, 'dt': 1710597600}, {'main': {'aqi': 4}, 'components': {'co': 1388.55, 'no': 0, 'no2': 54.84, 'o3': 69.38, 'so2': 25.75, 'pm2_5': 62.47, 'pm10': 94.32, 'nh3': 23.31}, 'dt': 1710601200}, {'main': {'aqi': 5}, 'components': {'co': 1708.98, 'no': 0, 'no2': 62.38, 'o3': 57.22, 'so2': 29.09, 'pm2_5': 87.51, 'pm10': 121.33, 'nh3': 31.16}, 'dt': 1710604800}, {'main': {'aqi': 5}, 'components': {'co': 2109.53, 'no': 0.02, 'no2': 74.71, 'o3': 34.33, 'so2': 28.37, 'pm2_5': 114.77, 'pm10': 151.07, 'nh3': 41.04}, 'dt': 1710608400}, {'main': {'aqi': 5}, 'components': {'co': 2109.53, 'no': 0.12, 'no2': 74.03, 'o3': 22.89, 'so2': 23.6, 'pm2_5': 117.08, 'pm10': 153.39, 'nh3': 44.08}, 'dt': 1710612000}, {'main': {'aqi': 5}, 'components': {'co': 1615.52, 'no': 0.05, 'no2': 59.63, 'o3': 26.46, 'so2': 17.17, 'pm2_5': 91.9, 'pm10': 125.84, 'nh3': 38.51}, 'dt': 1710615600}, {'main': {'aqi': 4}, 'components': {'co': 1081.47, 'no': 0, 'no2': 39.07, 'o3': 40.41, 'so2': 12.64, 'pm2_5': 69.36, 'pm10': 99.73, 'nh3': 33.95}, 'dt': 1710619200}, {'main': {'aqi': 4}, 'components': {'co': 714.3, 'no': 0, 'no2': 22.96, 'o3': 57.22, 'so2': 11.21, 'pm2_5': 56.4, 'pm10': 82.59, 'nh3': 31.92}, 'dt': 1710622800}, {'main': {'aqi': 3}, 'components': {'co': 527.38, 'no': 0, 'no2': 14.57, 'o3': 72.24, 'so2': 11.92, 'pm2_5': 49.81, 'pm10': 71.8, 'nh3': 28.63}, 'dt': 1710626400}, {'main': {'aqi': 3}, 'components': {'co': 
540.73, 'no': 0, 'no2': 13.88, 'o3': 76.53, 'so2': 13.35, 'pm2_5': 49.66, 'pm10': 69.19, 'nh3': 27.61}, 'dt': 1710630000}, {'main': {'aqi': 3}, 'components': {'co': 614.17, 'no': 0, 'no2': 16.79, 'o3': 72.96, 'so2': 14.07, 'pm2_5': 49.51, 'pm10': 67.86, 'nh3': 29.39}, 'dt': 1710633600}, {'main': {'aqi': 3}, 'components': {'co': 727.65, 'no': 0, 'no2': 22.28, 'o3': 62.94, 'so2': 13.95, 'pm2_5': 48.12, 'pm10': 66.47, 'nh3': 31.92}, 'dt': 1710637200}, {'main': {'aqi': 4}, 'components': {'co': 1255.04, 'no': 0.12, 'no2': 45.24, 'o3': 32.19, 'so2': 16.21, 'pm2_5': 63.67, 'pm10': 84.74, 'nh3': 37.49}, 'dt': 1710640800}, {'main': {'aqi': 5}, 'components': {'co': 1842.5, 'no': 10.95, 'no2': 58.95, 'o3': 14.48, 'so2': 18.6, 'pm2_5': 77.84, 'pm10': 101.78, 'nh3': 39.52}, 'dt': 1710644400}, {'main': {'aqi': 5}, 'components': {'co': 2109.53, 'no': 23.69, 'no2': 54.15, 'o3': 29.68, 'so2': 20.03, 'pm2_5': 80.15, 'pm10': 108.49, 'nh3': 36.99}, 'dt': 1710648000}, {'main': {'aqi': 5}, 'components': {'co': 2456.67, 'no': 27.05, 'no2': 62.38, 'o3': 48.64, 'so2': 23.84, 'pm2_5': 96.13, 'pm10': 133.44, 'nh3': 41.04}, 'dt': 1710651600}, {'main': {'aqi': 5}, 'components': {'co': 2937.32, 'no': 19.89, 'no2': 80.2, 'o3': 103, 'so2': 28.61, 'pm2_5': 127.55, 'pm10': 178.13, 'nh3': 44.58}, 'dt': 1710655200}, {'main': {'aqi': 5}, 'components': {'co': 1161.58, 'no': 3.97, 'no2': 28.45, 'o3': 191.69, 'so2': 47.68, 'pm2_5': 63.75, 'pm10': 105.84, 'nh3': 16.97}, 'dt': 1710658800}, {'main': {'aqi': 5}, 'components': {'co': 1001.36, 'no': 2.74, 'no2': 22.62, 'o3': 220.3, 'so2': 50.55, 'pm2_5': 66.3, 'pm10': 103.97, 'nh3': 14.69}, 'dt': 1710662400}, {'main': {'aqi': 5}, 'components': {'co': 961.3, 'no': 2.1, 'no2': 20.74, 'o3': 243.19, 'so2': 44.82, 'pm2_5': 71.78, 'pm10': 108.64, 'nh3': 14.06}, 'dt': 1710666000}]}

    print(weather)
    print(aqi)
    return render_template("full_weather.html", weather=weather, aqi=aqi, units=units)



if __name__ == '__main__':
    app.run(debug=True, port=5001)