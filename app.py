from flask import Flask, flash, render_template, request
import sqlite3
import os

# --- Setup paths and Flask ---
current_dir = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(current_dir, 'task.db')

app = Flask(__name__)
app.secret_key = "taskbridge_secret"

# --- Initialize Database ---
def init_db():
    """Create USERS table if it doesn't exist"""
    try:
        with sqlite3.connect(DB_PATH, timeout=20, check_same_thread=False) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS USERS (
                    ID INTEGER PRIMARY KEY AUTOINCREMENT,
                    EMAIL TEXT NOT NULL,
                    PASS TEXT NOT NULL,
                    NAME TEXT NOT NULL,
                    SKILLS TEXT,
                    SOCIALS TEXT,
                    USERTYPE INTEGER NOT NULL,
                    ORGTYPE TEXT,
                    LISNO TEXT
                )
            """)
            conn.commit()
            print("Database initialized successfully ✅")
    except sqlite3.OperationalError as e:
        print(f"Database error: {e}")

# --- Routes ---
@app.route('/')
@app.route('/home.html')
def home(): 
    return render_template('home.html')

@app.route('/login.html')
def login():
    return render_template('login.html')
@app.route('/user-signup')
def user_signup():
    return render_template('usersignup.html')

@app.route('/company-signup')
def company_signup():
    return render_template('companysignup.html')

@app.route('/addcompany', methods=['POST'])
def add_company():
    email = request.form['email']
    password = request.form['password']
    company_name = request.form['company_name']
    license_no = request.form['license_no']
    org_type = request.form['org_type']
    usertype = 0 

    try:
        with sqlite3.connect(DB_PATH, timeout=20, check_same_thread=False) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO USERS (NAME, EMAIL, PASS, LISNO, USERTYPE, ORGTYPE) VALUES (?, ?, ?, ?, ?, ?)", 
                (company_name, email, password, license_no, usertype,org_type)
            )
            conn.commit()
    except sqlite3.OperationalError as e:
        flash(f"Database error: {e}")
        return render_template('companysignup.html')

    return render_template('companydashboard.html', message='Company registered successfully.')

@app.route('/adduser', methods=['POST'])
def add_user():
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']
    skills = request.form['skills']
    socials = request.form['portfolio'] 
    usertype = 1 

    try:
        with sqlite3.connect(DB_PATH, timeout=20, check_same_thread=False) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO USERS (NAME, EMAIL, PASS, SKILLS, SOCIALS, USERTYPE) VALUES (?, ?, ?, ?, ?, ?)", 
                (name, email, password, skills, socials, usertype)
            )
            conn.commit()
            print("Success")
    except sqlite3.OperationalError as e:
        flash(f"Database error: {e}")
        return render_template('usersignup.html')

    return render_template('userdashboard.html', message='User registered successfully.')

@app.route('/login', methods=['POST'])
def login_post():
    email = request.form['email'].strip()
    password = request.form['password'].strip()
     

    try:
        with sqlite3.connect(DB_PATH, timeout=20, check_same_thread=False) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM USERS WHERE EMAIL=?", 
                (email,)
            )
            user = cursor.fetchone()
    except sqlite3.OperationalError as e:
        flash(f"Database error: {e}")
        return render_template('login.html')

    if user:
        db_email = user[1]
        db_pass = user[2]
        db_role = user[6]
        print(db_role)
        if email == db_email and password == db_pass:
            if db_role == 0:
                return render_template('companydashboard.html', user=user)
            else:
                return render_template('userdashboard.html', user=user)

    errorm="Invalid Credentials ❌"
    return render_template('login.html', error=errorm)

# --- Main ---
if __name__ == '__main__':
    import os
    # Only initialize DB in the child process (Flask debug reloader)
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        init_db()
    app.run(debug=True)