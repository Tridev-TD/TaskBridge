from flask import Flask, render_template, request
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

@app.route('/user-signup')
def user_signup():
    return render_template('usersignup.html')

@app.route('/login', methods=['POST'])
def login_post():
    email = request.form['email']
    password = request.form['password']
    role = request.form['role']


    conn = sqlite3.connect(os.path.join(current_dir, 'database.db'))
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM USERS WHERE email=? AND pass=? AND usertype=?", (email, password, role))
    user = cursor.fetchone()
    conn.close()

    if user:
        if role == 0 and user[1] == email and user[2] == password:  # Company user
            return render_template('companydashboard.html', user=user)
        elif role == 1 and user[1] == email and user[2] == password:  # Regular user 
            return render_template('userdashboard.html', user=user)
        
        
if __name__ == '__main__':
    app.run(debug=True)