from flask import Flask, flash, render_template, request
import sqlite3
import os

current_dir = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/home.html')
def home(): 
    return render_template('home.html')

@app.route('/login.html')
def login():
    return render_template('login.html')

@app.route('/company-signup')
def company_signup():
    return render_template('companysignup.html')

@app.route('/addcompany', methods=['POST'])
def add_company():
    
    email = request.form['email']
    password = request.form['password']
    company_name = request.form['company_name']
    lisense_no = request.form['license_no']
    usertype = 0  # Company user

    conn = sqlite3.connect(os.path.join(current_dir, 'test.db'))
    cursor = conn.cursor()
    cursor.execute("INSERT INTO USERS (company_name, email, pass, license_no, usertype) VALUES (?, ?, ?, ?, ?)", (company_name, email, password, lisense_no, usertype))
    conn.commit()
    conn.close()

    return render_template('login.html', message='Company registered successfully. Please log in.')

@app.route('/adduser', methods=['POST'])
def add_user():
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']
    skills = request.form['skills']
    portfolio = request.form['portfolio']
    usertype = 1  # Regular user

    conn = sqlite3.connect(os.path.join(current_dir, 'test.db'))
    cursor = conn.cursor()
    cursor.execute("INSERT INTO USERS (name, email, pass, skills, portfolio, usertype) VALUES (?, ?, ?, ?, ?, ?)", (name, email, password, skills, portfolio, usertype))
    conn.commit()
    conn.close()

    return render_template('login.html', message='User registered successfully. Please log in.')

@app.route('/user-signup')
def user_signup():
    return render_template('usersignup.html')

@app.route('/login', methods=['POST'])
def login_post():
    email = request.form['email']
    password = request.form['password']
    role = request.form['role']


    conn = sqlite3.connect(os.path.join(current_dir, 'test.db'))
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM USERS WHERE email=? AND pass=? AND usertype=?", (email, password, role))
    user = cursor.fetchone()
    conn.close()

    if user:
        if role == 0 and user[1] == email and user[2] == password:  # Company user
            return render_template('companydashboard.html', user=user)
        elif role == 1 and user[1] == email and user[2] == password:  # Regular user 
            return render_template('userdashboard.html', user=user)
        else:
            flash("Invalid Credentials ❌")
            return render_template('login.html', error='Invalid credentials')
    else:
        flash("Invalid Credentials ❌")
        return render_template('login.html', error='Invalid credentials')

if __name__ == '__main__':
    app.run(debug=True)