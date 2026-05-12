print("🔥 THIS IS THE REAL APP.PY FILE 🔥")

from flask import Flask, render_template, request, redirect, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

from flask import Response
import csv


# ------------------ Flask App ------------------
app = Flask(__name__)
app.secret_key = "symposium_secret_key"   # SET ONLY ONCE

# ------------------ Routes ------------------
print("RULES ROUTE LOADED")

@app.route('/rules')
def rules():
    if 'user_id' not in session:
        return redirect('/login')
    return render_template('rules.html')

# ------------------ Database Connection ------------------
def get_db_connection():
    conn = sqlite3.connect('symposium.db')
    conn.row_factory = sqlite3.Row
    return conn

# ------------------ Database Connection ------------------
def get_db_connection():
    conn = sqlite3.connect('symposium.db')
    conn.row_factory = sqlite3.Row
    return conn


# ------------------ TEAM ID GENERATOR ------------------

EVENT_PREFIX = {
    "Debugging": "DBG",
    "AI Prompt Creation": "APC",
    "AI Quiz": "AIQ",
    "Tech-Connection": "TCN",
    "IPL Auction": "IPL",
    "Adzap": "ADZ",
    "Dumb Charades": "DMC",
    "Treasure Hunt": "TRH"
}

def generate_team_id(event_name):
    conn = get_db_connection()
    cur = conn.cursor()

    prefix = EVENT_PREFIX.get(event_name)
    year_code = "26"   # Symposium year

    if not prefix:
        conn.close()
        return None

    cur.execute("""
        SELECT COUNT(DISTINCT team_id)
        FROM event_registrations
        WHERE event_name = ?
    """, (event_name,))

    count = cur.fetchone()[0] or 0
    next_number = 101 + count

    conn.close()

    return f"{year_code}{prefix}{next_number}"

# ------------------ Create Tables ------------------
def create_tables():
    conn = get_db_connection()
    cur = conn.cursor()

    # Users table (students login)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        login_id TEXT UNIQUE NOT NULL,
        reg_no TEXT UNIQUE NOT NULL,
        email TEXT NOT NULL,
        mobile TEXT NOT NULL,
        password TEXT NOT NULL,
        department TEXT NOT NULL,
        college TEXT NOT NULL
    )
""")


    # Admins table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # Events table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS events (
            event_id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_name TEXT UNIQUE NOT NULL
        )
    """)

    # Event registrations
    cur.execute("""
        CREATE TABLE IF NOT EXISTS event_registrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_name TEXT NOT NULL,
            name TEXT NOT NULL,
            reg_no TEXT NOT NULL,
            department TEXT NOT NULL,
            college TEXT NOT NULL,
            class TEXT NOT NULL
        )
    """)

    # Insert default events
    events = [
    # Technical Events
    "De-Bugging",
    "AI Image Creation",
    "QUIZ",
    "Paper Presentation",

    # Non-Technical Events
    "IPL AUCTION",
    "AI-Based Reels Competition",
    "Guess the Song",
    "Lucky Draw"
]

    for e in events:
        cur.execute("INSERT OR IGNORE INTO events (event_name) VALUES (?)", (e,))

    conn.commit()
    conn.close()
    
# ------------------ Create Default Admin ------------------
def create_admin():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT OR IGNORE INTO admins (username, password) VALUES (?, ?)",
        ('admin', 'admin123')   # simple for now
    )
    conn.commit()
    conn.close()

# ------------------ Routes ------------------

@app.route('/')
def index():
    return render_template('landing.html')

# -------- Student Registration --------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        login_id = request.form['login_id']
        reg_no = request.form['reg_no']
        email = request.form['email']
        mobile = request.form['mobile']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        department = request.form['department']
        college = request.form['college']

        if password != confirm_password:
            flash("Passwords do not match!", "danger")
            return redirect('/register')

        hashed_password = generate_password_hash(password)

        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO users
                (login_id, reg_no, email, mobile, password, department, college)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (login_id, reg_no, email, mobile, hashed_password, department, college))

            conn.commit()

        except sqlite3.IntegrityError:
            flash("Login ID or Register Number already exists!", "danger")
            return redirect('/register')

        finally:
            conn.close()

        # ✅ THIS IS THE IMPORTANT PART
        flash("✅ Registration successful! Please login to continue.", "success")
        return redirect('/login')   # 🔥 Redirect to LOGIN, not events

    return render_template('register.html')

    
# -------- Student Register --------
@app.route('/login', methods=['GET', 'POST'])

# -------- Login ------------
def login():
    if request.method == 'POST':
        login_id = request.form['login_id']
        password = request.form['password']

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE login_id=?", (login_id,))
        user = cur.fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            return redirect('/home')

        return "Invalid login"

    return render_template('login.html')
#----- Forgot Password -----
import random
import string
from werkzeug.security import generate_password_hash

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        reg_no = request.form['reg_no']

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("SELECT * FROM users WHERE reg_no = ?", (reg_no,))
        user = cur.fetchone()

        if not user:
            conn.close()
            flash("Register Number not found", "danger")
            return redirect('/forgot_password')

        # 🔑 Generate temporary password
        new_password = ''.join(
            random.choices(string.ascii_letters + string.digits, k=8)
        )

        hashed_password = generate_password_hash(new_password)

        cur.execute("""
            UPDATE users
            SET password = ?
            WHERE reg_no = ?
        """, (hashed_password, reg_no))

        conn.commit()
        conn.close()

        flash(f"Your new password is: {new_password}", "success")
        return redirect('/login')

    return render_template('forgot_password.html')


#--------- Home Page --------
@app.route('/home')
def home():
    if 'user_id' not in session:
        return redirect('/login')

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT event_name FROM events")
    events = cur.fetchall()
    conn.close()

    technical_events = [
        'De-Bugging',
        'AI Image Creation',
        'QUIZ',
        'Paper Presentation'
    ]

    non_technical_events = [
        'IPL AUCTION',
        'AI-Based Reels Competition',
        'Guess the Song',
        'Lucky Draw'
    ]

    tech_count = 0
    non_tech_count = 0

    for e in events:
        if e['event_name'] in technical_events:
            tech_count += 1
        elif e['event_name'] in non_technical_events:
            non_tech_count += 1

    total_count = tech_count + non_tech_count

    return render_template(
        'home.html',
        tech_count=tech_count,
        non_tech_count=non_tech_count,
        total_count=total_count
    )

@app.route('/about')
def about():
    return render_template('about.html')


#-----for my_events-----
@app.route('/my_events')
def my_events():
    if 'user_id' not in session:
        return redirect('/login')

    conn = get_db_connection()
    cur = conn.cursor()

    # Fetch registrations created by this user
    cur.execute("""
        SELECT
            team_id,
            event_name,
            name,
            reg_no,
            class,
            department
        FROM event_registrations
        WHERE created_by = ?
        ORDER BY event_name
    """, (session['user_id'],))

    rows = cur.fetchall()
    conn.close()

    events = {}

    for r in rows:
        events.setdefault(r['event_name'], []).append(r)

    return render_template(
        'my_events.html',
        events=events
    )

# -------- Events List --------
@app.route('/events')
def events():
    if 'user_id' not in session:
        return redirect('/login')

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM events")
    events_list = cur.fetchall()
    conn.close()

    return render_template('events.html', events=events_list)

# -------- Event Registration --------
@app.route('/register_event/<int:event_id>', methods=['GET', 'POST'])
def register_event(event_id):
    # 🔐 Login check
    if 'user_id' not in session:
        return redirect('/login')

    conn = get_db_connection()
    cur = conn.cursor()

    # 🔹 Fetch event details (MUST include team_size)
    cur.execute("""
        SELECT event_id, event_name, team_size
        FROM events
        WHERE event_id = ?
    """, (event_id,))
    event = cur.fetchone()

    if not event:
        conn.close()
        return "Event not found"

    # ---------------- GET REQUEST ----------------
    if request.method == 'GET':
        conn.close()
        return render_template(
            'register_event.html',
            event=event
        )

    # ---------------- POST REQUEST ----------------
    try:
        # 🔐 Generate ONE team_id for the whole team
        team_id = generate_team_id(event['event_name'])

        team_size = event['team_size']

        # Common fields (entered once)
        department = request.form['department']
        college = request.form['college']

        # 🔁 Insert ALL participants under SAME team_id
        for i in range(1, team_size + 1):
            name = request.form.get(f"name_{i}")
            reg_no = request.form.get(f"reg_no_{i}")
            student_class = request.form.get(f"class_{i}")

            if not name or not reg_no or not student_class:
                raise ValueError("Missing participant details")

            cur.execute("""
                INSERT INTO event_registrations
                (
                    team_id,
                    event_name,
                    name,
                    reg_no,
                    class,
                    department,
                    college,
                    created_by
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                team_id,
                event['event_name'],
                name,
                reg_no,
                student_class,
                department,
                college,
                session['user_id']   # ⭐ CRITICAL FIX
            ))

        conn.commit()

        flash(
            f"✅ Registration successful! Your Team ID is {team_id}",
            "success"
        )
        return redirect('/events')

    except Exception as e:
        conn.rollback()
        flash("❌ Registration failed. Please try again.", "danger")
        print("Registration Error:", e)
        return redirect(f"/register_event/{event_id}")

    finally:
        conn.close()

#------ contact page ------
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')

        # For now just show success message
        flash("✅ Your message has been sent successfully!", "success")
        return redirect('/contact')

    return render_template('contact.html')

    # ---------------- GET REQUEST ----------------
    conn.close()
    return render_template(
        'register_event.html',
        event=event
    )

# -------- Logout --------
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# ------------------ ADMIN MODULE ------------------

@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM admins WHERE username=? AND password=?",
            (username, password)
        )
        admin = cur.fetchone()
        conn.close()

        if admin:
            session['admin'] = username
            return redirect('/admin/dashboard')

        return "Invalid Admin Login"

    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'admin' not in session:
        return redirect('/admin')

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, team_id, event_name, name, reg_no, class, department, college
        FROM event_registrations
        ORDER BY event_name, team_id
    """)
    rows = cur.fetchall()
    conn.close()

    dashboard_data = {}

    for r in rows:
        event = r['event_name']
        team = r['team_id'] or "NO_TEAM"

        dashboard_data.setdefault(event, {})
        dashboard_data[event].setdefault(team, [])

        dashboard_data[event][team].append({
            "id": r["id"],              # ✅ VERY IMPORTANT
            "name": r["name"],
            "reg_no": r["reg_no"],
            "class": r["class"],
            "department": r["department"],
            "college": r["college"]
        })

    return render_template(
        "admin_dashboard.html",
        dashboard_data=dashboard_data
    )
#-------- admin user and pasword ---------
@app.route('/admin/users')
def admin_users():
    if 'admin' not in session:
        return redirect('/admin')

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, login_id, reg_no, email, mobile, department, college, password
        FROM users
        ORDER BY id DESC
    """)
    users = cur.fetchall()

    conn.close()

    return render_template('admin_users.html', users=users)

#-------- Export all response CSV --------
@app.route('/admin/export/all')
def export_all_excel():
    if 'admin' not in session:
        return redirect('/admin')

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT team_id, event_name, name, reg_no, class, department, college
        FROM event_registrations
        ORDER BY event_name, team_id
    """)
    rows = cur.fetchall()
    conn.close()

    def generate():
        yield "Team ID,Event Name,Student Name,Register No,Class,Department,College\n"
        for r in rows:
            yield f"{r['team_id']},{r['event_name']},{r['name']},{r['reg_no']},{r['class']},{r['department']},{r['college']}\n"

    return Response(
        generate(),
        mimetype="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=all_registrations.csv"
        }
    )

#-------- Export Event wise registrations CSV --------
@app.route('/admin/export/event/<event_name>')
def export_event_excel(event_name):
    if 'admin' not in session:
        return redirect('/admin')

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT team_id, name, reg_no, class, department, college
        FROM event_registrations
        WHERE event_name = ?
        ORDER BY team_id
    """, (event_name,))
    rows = cur.fetchall()
    conn.close()

    def generate():
        yield "Team ID,Student Name,Register No,Class,Department,College\n"
        for r in rows:
            yield f"{r['team_id']},{r['name']},{r['reg_no']},{r['class']},{r['department']},{r['college']}\n"

    safe_name = event_name.replace(" ", "_")

    return Response(
        generate(),
        mimetype="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={safe_name}_registrations.csv"
        }
    )



@app.route('/admin/export_all')
def export_all_csv():
    if 'admin' not in session:
        return redirect('/admin')

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM event_registrations")
    rows = cur.fetchall()
    conn.close()

    def generate():
        yield "Event,Name,Register No,Department,College,Class\n"
        for r in rows:
            yield f"{r['event_name']},{r['name']},{r['reg_no']},{r['department']},{r['college']},{r['class']}\n"

    return Response(
        generate(),
        mimetype="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=all_registrations.csv"
        }
    )

@app.route('/admin/delete/<int:reg_id>')
def delete_registration(reg_id):
    if 'admin' not in session:
        return redirect('/admin')

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM event_registrations WHERE id=?", (reg_id,))
    conn.commit()
    conn.close()

    return redirect('/admin/dashboard')


@app.route('/admin/edit/<int:reg_id>', methods=['GET', 'POST'])
def edit_registration(reg_id):
    if 'admin' not in session:
        return redirect('/admin')

    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        cur.execute("""
            UPDATE event_registrations
            SET name=?, reg_no=?, class=?, department=?, college=?
            WHERE id=?
        """, (
            request.form['name'],
            request.form['reg_no'],
            request.form['class'],
            request.form['department'],
            request.form['college'],
            reg_id
        ))
        conn.commit()
        conn.close()
        return redirect('/admin/dashboard')

    cur.execute("SELECT * FROM event_registrations WHERE id=?", (reg_id,))
    r = cur.fetchone()
    conn.close()

    return render_template('edit_registration.html', r=r)


import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'static/gallery'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/admin/gallery', methods=['GET', 'POST'])
def admin_gallery():
    if 'admin' not in session:
        return redirect('/admin')

    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        file = request.files['image']
        caption = request.form['caption']

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            cur.execute(
                "INSERT INTO gallery (image_filename, caption) VALUES (?, ?)",
                (filename, caption)
            )
            conn.commit()
            flash("Image uploaded successfully!", "success")

    cur.execute("SELECT * FROM gallery ORDER BY id DESC")
    images = cur.fetchall()
    conn.close()

    return render_template('admin_gallery.html', images=images)

@app.route('/api/registration_count')
def registration_count():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM event_registrations")
    count = cur.fetchone()[0]
    conn.close()
    return {"count": count}

@app.route('/gallery')
def gallery():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM gallery ORDER BY id DESC")
    images = cur.fetchall()
    conn.close()
    return render_template('gallery.html', images=images)




conn = sqlite3.connect('symposium.db')
cur = conn.cursor()
cur.execute("SELECT event_name FROM events")
print(cur.fetchall())
conn.close()

# ------------------ Run App ------------------
if __name__ == '__main__':
    #create_tables()
    #create_admin()
    app.run(debug=True, use_reloader=False)