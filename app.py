from flask import Flask, render_template, request
import sqlite3
import os

current_dir = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('home.html')






if __name__ == '__main__':
    app.run(debug=True)