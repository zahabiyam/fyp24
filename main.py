import requests, json
from flask import render_template, redirect, url_for, request, session, jsonify
from config import app, mysql
from datetime import datetime
import random
from weather_helpers import coordinates, getweather, getaqi,getWeatherDayWise

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
    
    if not buyer_id:
        return render_template('index.html', farmer_id=farmer_id)
    chat_notification = 0
    cur = mysql.connection.cursor()
    cur.execute("""SELECT c.`id`, ua.`username` 'name', p.`Name` 'product_name', p.`id` 'product_id', c.`sender_id` 'farmer_id', c.`receiver_id` 'buyer_id'
                    FROM chat_notification c
                    JOIN user_account ua ON c.`sender_id` = ua.`id` AND ua.`role` = 'farmer'
                    JOIN chat ch ON c.`chat_id` = ch.`id`
                    JOIN product p ON ch.`product_id` = p.`id`
                    WHERE c.`receiver_id` = %s AND c.`seen` = %s
                    GROUP BY p.`id`, c.`sender_id`
                """, (buyer_id, 0))
    chat_notification = cur.fetchall()
    notification_data = []
    for i in chat_notification:
        notification_data.append({
            'notification_id': i[0],
            'farmer_name': i[1],
            'product_name': i[2],
            'product_id': i[3],
            'farmer_id': i[4],
            'buyer_id': i[5]
        })
    print(chat_notification)
    print(notification_data)

    return render_template('index.html', buyer_id=buyer_id, notification_data = notification_data)


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
    
    notification_id = request.args.get('notification_id')
    
    open_chat = False
    product_id = None
    prod_farmer_id = None
    if notification_id:
        print("open chat")
        print(notification_id)
        cur.execute("UPDATE chat_notification SET seen = %s WHERE id = %s", (1, notification_id))
        mysql.connection.commit()
        cur.execute("""SELECT ch.`product_id`, c.`sender_id` FROM chat_notification c
                    JOIN chat ch ON c.`chat_id` = ch.`id`
                    WHERE c.`id` = %s""", (notification_id,))
        chat_data = cur.fetchone()
        product_id = chat_data[0]
        prod_farmer_id = chat_data[1]
        open_chat = True
    
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


    cur = mysql.connection.cursor()
    cur.execute("""SELECT c.`id`, ua.`username` 'name', p.`Name` 'product_name', p.`id` 'product_id', c.`sender_id` 'farmer_id', c.`receiver_id` 'buyer_id'
                    FROM chat_notification c
                    JOIN user_account ua ON c.`sender_id` = ua.`id` AND ua.`role` = 'farmer'
                    JOIN chat ch ON c.`chat_id` = ch.`id`
                    JOIN product p ON ch.`product_id` = p.`id`
                    WHERE c.`receiver_id` = %s AND c.`seen` = %s
                    GROUP BY p.`id`, c.`sender_id`
                """, (buyer_id, 0))
    chat_notification = cur.fetchall()
    notification_data = []
    for i in chat_notification:
        notification_data.append({
            'notification_id': i[0],
            'farmer_name': i[1],
            'product_name': i[2],
            'product_id': i[3],
            'farmer_id': i[4],
            'buyer_id': i[5]
        })
    return render_template('product.html', products=product_data, farmer_id=farmer_id, buyer_id=buyer_id, open_chat=open_chat, product_id=product_id, prod_farmer_id=prod_farmer_id, notification_data = notification_data)


@app.route("/chat", methods=['GET', 'POST'])
def chat():
    if request.method == 'POST':
        data = request.get_json()['data']
        print(data)
        try:        
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO chat (product_id, sender_id, receiver_id, message, sent_at, sender_type) VALUES (%s, %s, %s, %s, %s, %s)", (data['product_id'], data['sender_id'], data['receiver_id'], data['message'], datetime.now(), data['sender_type']))            
            mysql.connection.commit()
            chat_id = cur.lastrowid
            cur.execute("INSERT INTO chat_notification (sender_id, receiver_id, chat_id, seen, created_at) VALUES (%s, %s, %s, %s, %s)", (data['sender_id'], data['receiver_id'], chat_id, 0, datetime.now()))
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

    if request.method != 'POST':
        return render_template("farmer/get_weather.html")

    res_date = request.args.get("date")
    print(res_date)
    cur = mysql.connection.cursor()
    cur.execute("SELECT zipcode FROM farmer WHERE UserAccountID = %s", (farmer_id,))
    zipcode = cur.fetchone()[0]

    zipcode = int(zipcode)
    units = request.form.get("units")

    # Get latitude and longitude for zipcode
    latlong = coordinates(zipcode)
    lat = latlong["lat"]
    lon = latlong["lon"]

    # Get weather by latitude and longitude
    # weather = getweather(lat, lon, units)
    weather = getWeatherDayWise(lat, lon, units, date=res_date)
    aqi = getaqi(lat, lon)
    print(weather)
    # print(aqi)
    return render_template("full_weather.html", weather=weather, aqi=aqi, units=units)
    



if __name__ == '__main__':
    app.run(debug=True, port=5001)