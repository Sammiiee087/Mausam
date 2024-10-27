from re import L
import flask
from flask import Flask, render_template, request, redirect, flash, url_for, session
from flask_restful import Api, Resource
from flask_httpauth import HTTPBasicAuth
import time
import json
import requests
import json
from config import *
import sqlite3
from flask_session import Session
from functools import wraps

app = Flask(__name__)

app.config['SECRET_KEY'] = FLASK_KEY
app.config['SESSION_TYPE'] = 'filesystem'

Session(app)

auth = HTTPBasicAuth()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Login Route
@app.route("/login/", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()

        if user:
            session['user'] = user[1]
            flash('Login successful!', 'success')
            print(session)
            return redirect(url_for('home'))
        else:
            flash('Invalid credentials, please try again.', 'error')

    return render_template('login.html', company_name=COMPANY_NAME)

# Signup Route
@app.route("/signup/", methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('Passwords do not match!', 'error')
            return redirect(url_for('signup'))

        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()

        flash('Signup successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html', company_name=COMPANY_NAME)

@app.route("/logout/")
def logout():
    session.pop('user', None) 
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('home.html', company_name=COMPANY_NAME)

@app.route("/faq/", methods=['GET', 'POST'])
def faq():
    return render_template('faq.html', company_name=COMPANY_NAME)

@app.route("/about/", methods=['GET','POST'])
def about():
    return render_template('about.html', company_name = COMPANY_NAME)

def create_table():
    conn = sqlite3.connect('form_data.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS submissions 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  name TEXT NOT NULL, 
                  email TEXT NOT NULL, 
                  phone TEXT, 
                  subject TEXT, 
                  message TEXT NOT NULL)''')
    conn.commit()
    conn.close()
    
def create_user_table():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  username TEXT NOT NULL, 
                  password TEXT NOT NULL)''')
    conn.commit()
    conn.close()
    
def print_table():
    conn = sqlite3.connect('form_data.db')
    c = conn.cursor()
    c.execute("SELECT * FROM submissions")
    rows = c.fetchall()
    conn.close()
    
    for row in rows:
        print(row)

@app.route('/contact/', methods=['GET', 'POST'])
@login_required
def contact():
    if request.method == 'POST':
        data = request.get_json()
        name = data['name']
        email = data['email']
        phone = data['phone']
        subject = data['subject']
        message = data['message']
        
        if not name or not email or not message:
            flash('Name, Email, and Message are required!', 'error')
            return redirect('/contact')

        conn = sqlite3.connect('form_data.db')
        c = conn.cursor()
        c.execute("INSERT INTO submissions (name, email, phone, subject, message) VALUES (?, ?, ?, ?, ?)", 
                  (name, email, phone, subject, message))
        conn.commit()
        submission_id = c.lastrowid
        conn.close()
        
        # flash(f'Form submitted successfully! Your support ticket ID is {submission_id}', 'success')
        # return render_template('form.html', company_name = COMPANY_NAME, submission_number=submission_id)

    return render_template('form.html', company_name=COMPANY_NAME)

@app.route("/weather/", methods=['GET', 'POST'])
@login_required
def weather():
    if request.method == 'POST':
        print(request.form['query'])
        data = getWeatherData(request.form['query'])
        return render_template('weather.html', company_name = COMPANY_NAME, data = data, google_maps_api_key = GOOGLEMAPSAPI_KEY)

    return render_template('weather.html', company_name = COMPANY_NAME)

def getWeatherData(query):
    url = "http://api.weatherapi.com/v1/current.json"
    querystring = {"key": WEATHERAPI_KEY, "q":str(query), "days":"1"}
    payload = ""
    response = requests.request("GET", url, data=payload, params=querystring)
    r = response.json()
    cr = json.dumps(r, indent=2)
    return json.loads(cr)

if __name__ == "__main__":
    create_table()
    create_user_table()
    print_table()
    app.run(debug=True, port=8000)
