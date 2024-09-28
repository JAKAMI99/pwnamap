from flask import render_template, request, Blueprint, redirect, url_for
import logging
from ..tools.db import get_db_connection
import secrets, bcrypt

setup_bp = Blueprint('setup', __name__)
log = logging.getLogger(__name__)

def create_user(username, password):
    print("Creating new user")
    log.info(f"Creating new user {username}")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        api_key = secrets.token_hex(16) # Generate new API key
        # Insert username, hashed+salted password, and API Key into the database
        cursor.execute("INSERT INTO users (username, password, api_key) VALUES (?, ?, ?)", (username, hashed_password, api_key))
        
        # Commit changes and close connection
        conn.commit()
        conn.close()
        print(f"User {username} was created successfully.")
        print(f"Your new API-key is:{api_key}")
    except Exception as e:
        print("Error:", e)
        log.fatal(f"Request Path: {request.path} - Error when creating a user:{str(e)}")

@setup_bp.route('/setup', methods=['GET', 'POST'])
def setup():

    create_database()

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM users')
    user_count = cursor.fetchone()[0]
    conn.close()

    if user_count == 0:
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            create_user(username, password)
            log.debug(f"Request Path: {request.path} - Setup: User was created, redirecting to login")
            return redirect(url_for('dynamic.login'))
        return render_template('setup.html')
    else:
        print("Setup: Redirecting to login page because the users table is not empty.")
        log.debug(f"Request Path: {request.path} - Redirect to login page instead, since a registered user was found")
        return redirect(url_for('dynamic.login'))


def create_database():
    print("Function create_database running")
    log.debug(f"Setup: Creating the table users in the db.")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY,
                        username TEXT NOT NULL,
                        password TEXT NOT NULL,
                        api_key TEXT,
                        wigle TEXT,
                        wpasec TEXT)''')
    conn.commit()
    conn.close()