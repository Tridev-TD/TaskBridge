from flask import Flask, flash, render_template, request
import sqlite3
import os
import requests
from flask import jsonify

# --- Setup paths and Flask ---
current_dir = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(current_dir, 'auth.db')

app = Flask(__name__)
app.secret_key = "taskbridge_secret"

# --- Initialize Database ---
def init_db():
    """Create USERS table if it doesn't exist"""
    try:
        with sqlite3.connect(DB_PATH, timeout=20, check_same_thread=False) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    ID INTEGER PRIMARY KEY AUTOINCREMENT,
                    NAME TEXT NOT NULL,
                    EMAIL TEXT UNIQUE NOT NULL,
                    PASS TEXT NOT NULL,
                    SKILLSET TEXT,
                    GITNAME TEXT,
                    RESUME BLOB,
                    PLACE TEXT
                )
            """)
            # Organization Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS org (
                    ID INTEGER PRIMARY KEY AUTOINCREMENT,
                    NAME TEXT NOT NULL,
                    EMAIL TEXT UNIQUE NOT NULL,
                    PASS TEXT NOT NULL,
                    LISNO TEXT,
                    TYPE TEXT,
                    LOCATION TEXT
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



@app.route('/addcompany', methods=['POST'])
def add_company():
    email = request.form['email']
    password = request.form['password']
    company_name = request.form['company_name']
    license_no = request.form['license_no']
    org_type = request.form['org_type']
    loc= request.form['location']
   

    try:
        with sqlite3.connect(DB_PATH, timeout=20, check_same_thread=False) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO org (NAME, EMAIL, PASS, LISNO, TYPE, LOCATION) VALUES (?, ?, ?, ?, ?, ?)", 
                (company_name, email, password, license_no,org_type,loc)
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
    resume = request.files.get('resume')
    pla= request.form['location']

    gitsc= calculate_github_score(socials)
    
    if resume:
        resume_blob = resume.read()
    else:
        resume_blob = None

    try:
        with sqlite3.connect(DB_PATH, timeout=20, check_same_thread=False) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (NAME, EMAIL, PASS, SKILLSET, GITNAME, RESUME, PLACE,GITSCORE) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", 
                (name, email, password, skills, socials, resume_blob, pla,gitsc["github_score"])
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

            # 1️⃣ Check in users table
            cursor.execute("SELECT * FROM users WHERE email=?", (email,))
            user = cursor.fetchone()

            if user:
                if password == user[4]:   # pass column index in users table
                    return render_template('userdashboard.html', user=user)

            # 2️⃣ If not in users, check in org table
            cursor.execute("SELECT * FROM org WHERE email=?", (email,))
            org = cursor.fetchone()

            if org:
                if password == org[5]:   # pass column index in org table
                    return render_template('companydashboard.html', org=org)

    except sqlite3.OperationalError as e:
        flash(f"Database error: {e}")
        return render_template('login.html')

    # ❌ If nothing matched
    return render_template('login.html', error="Invalid Credentials ❌")


@app.route('/companytasks')
def company_tasks():
    return render_template('companytasks.html')

@app.route('/companycompetitions')
def company_competitions():
    return render_template('companycompetitions.html')







# --- Main ---
if __name__ == '__main__':
    import os
    # Only initialize DB in the child process (Flask debug reloader)
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        init_db()
    app.run(debug=True)