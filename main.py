import requests, json
from flask import render_template, redirect, url_for, request, session, jsonify
from config import app
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
    return render_template('signup.html')

@app.route("/products", methods=['GET', 'POST'])
def products():
    return render_template('product.html')

@app.route("/farmer_profile", methods=['GET', 'POST'])
def farmer_profile():
    return render_template('farmer profile.html')

if __name__ == '__main__':
    app.run(debug=True)