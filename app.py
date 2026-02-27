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

# @app.route('/login')
# def login_post():
#     return
     

@app.route('/company-signup')
def company_signup():
    return render_template('companysignup.html')

@app.route('/user-signup')
def user_signup():
    return render_template('usersignup.html')




if __name__ == '__main__':
    app.run(debug=True)