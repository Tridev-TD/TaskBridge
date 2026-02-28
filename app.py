from flask import Flask, flash, render_template, request
import sqlite3
import os
import requests
from flask import jsonify

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

@app.route('/companytask')
def company_task():
    return render_template('companytasks.html')

@app.route('/companycomp')
def company_comp():
    return render_template('companycompetitions.html')

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

    return render_template('login.html', message='User registered successfully.')

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

@app.route('/companytasks')
def company_tasks():
    return render_template('companytasks.html')

@app.route('/companycompetitions')
def company_competitions():
    return render_template('companycompetitions.html')



def calculate_github_score(username):
    base_url = "https://api.github.com/users/"

    # Fetch user profile
    user_res = requests.get(base_url + username)
    if user_res.status_code != 200:
        return {"error": "User not found"}

    user_data = user_res.json()

    # Fetch repositories
    repo_res = requests.get(base_url + username + "/repos?per_page=100")
    repos = repo_res.json()

    # Basic metrics
    public_repos = user_data.get("public_repos", 0)
    followers = user_data.get("followers", 0)

    total_stars = 0
    total_forks = 0
    languages = set()

    for repo in repos:
        total_stars += repo.get("stargazers_count", 0)
        total_forks += repo.get("forks_count", 0)
        if repo.get("language"):
            languages.add(repo.get("language"))

    # ---------- SCORING ----------

    # 1. Repo Score (20)
    repo_score = min(public_repos * 2, 20)

    # 2. Star Score (20)
    star_score = min(total_stars * 1.5, 20)

    # 3. Fork Score (10)
    fork_score = min(total_forks * 1, 10)

    # 4. Language Score (10)
    lang_count = len(languages)
    if lang_count >= 6:
        language_score = 10
    elif lang_count >= 4:
        language_score = 7
    elif lang_count >= 2:
        language_score = 5
    else:
        language_score = 2

    # 5. Community Score (10)
    community_score = min(followers * 0.5, 10)

    # 6. Profile Completeness (10)
    profile_score = 0
    if user_data.get("bio"):
        profile_score += 2
    if user_data.get("location"):
        profile_score += 2
    if user_data.get("blog"):
        profile_score += 2
    if user_data.get("avatar_url"):
        profile_score += 2
    if public_repos > 0:
        profile_score += 2

    # Simple activity score based on repo updates (20)
    activity_score = 0
    recent_active = 0
    for repo in repos:
        if repo.get("updated_at"):
            recent_active += 1
    activity_score = min(recent_active, 20)

    # Final Score
    github_score = (
        repo_score +
        star_score +
        fork_score +
        language_score +
        community_score +
        profile_score +
        activity_score
    )

    github_score = min(round(github_score, 2), 100)

    return {
        "username": username,
        "github_score": github_score,
        "breakdown": {
            "repo_score": repo_score,
            "star_score": star_score,
            "fork_score": fork_score,
            "language_score": language_score,
            "community_score": community_score,
            "profile_score": profile_score,
            "activity_score": activity_score
        }
    }







@app.route("/github-score/<username>")
def github_score(username):
    result = calculate_github_score(username)
    return result

if __name__ == "__main__":
    app.run(debug=True)



# --- Main ---
if __name__ == '__main__':
    import os
    # Only initialize DB in the child process (Flask debug reloader)
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        init_db()
    app.run(debug=True)