from flask import Blueprint, session, redirect, url_for, request, jsonify
import sqlite3, bcrypt, os, re, logging
from functools import wraps
from contextlib import closing

auth_bp = Blueprint('auth', __name__)
log = logging.getLogger(__name__)

def get_db_connection():
    db_path = 'app/data/'

    # Check for write permissions on the database directory
    check_permissions(db_path)  # Ensure the path is writable

    if not os.path.exists(db_path):
        os.makedirs(db_path, exist_ok=True)  # Create the directory if it doesn't exist
        log.info(f"Database was not present and was created at {db_path}")

    conn = sqlite3.connect(os.path.join(db_path, 'pwnamap.db'))
    conn.row_factory = sqlite3.Row
    return conn

def check_permissions(db_path):
    if not os.access(db_path, os.W_OK):
        log.fatal(f"Cannot write to the database at {db_path}")
        raise PermissionError(f"Cannot write to {db_path}")


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            if not any_users_exist():
                log.info("No user was found in db. Redirecting to setup")
                return redirect(url_for('setup.setup'))  # Redirect to setup if no users exist
            else:
                log.debug("User was not authenticated. Redirecting to the loginpage")                
                return redirect(url_for('dynamic.login'))  # Redirect to login page if not authenticated

        return f(*args, **kwargs)
    return decorated_function

def any_users_exist():
    try:
        with closing(get_db_connection()) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM users')
            count = cursor.fetchone()[0]
            return count > 0
    except Exception as e:
        log.error("Error checking user existence: %s", str(e))
        return False

def authenticate_user(username, password):
    try:
        with closing(get_db_connection()) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
            user = cursor.fetchone()
            log.debug(f"Checking DB for the password of user {username}")

            if user:
                stored_password = user['password']
                if bcrypt.checkpw(password.encode('utf-8'), stored_password):
                    session['username'] = username  # Set session cookie upon successful login
                    log.debug("Password for the user was correct")
                    return True

        return False

    except Exception as e:
        log.error("Error authenticating user: %s", e)
        return False

def sanitize_api_key(api_key):
    hex_pattern = re.compile(r'^[0-9a-fA-F]+$')
    if not hex_pattern.match(api_key):
        log.warning("Invalid API Key. It was not hexadecimal as expected")
        raise ValueError("Invalid API key. Only hexadecimal characters are allowed.")

    return api_key

def verify_api_key(api_key):
    try:
        sanitize_api_key(api_key)  # Validate the API key format
        log.debug("Verifying submitted API key")
        with closing(get_db_connection()) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM users WHERE api_key=?", (api_key,))
            result = cursor.fetchone()

        return result is not None

    except ValueError as ve:
        log.error("API key verification failed: %s", ve)
        return False

    except Exception as e:
        log.error("Error in verifying API key: %s", e)
        return False


def api_key_or_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if the session is valid
        if 'username' in session:
            return f(*args, **kwargs)  # Session is valid, proceed with the request
        log.debug("User authenticated by @api_key_or_login_required")
        # Otherwise, check if there's a valid API key
        api_key = request.headers.get("X-API-KEY") or request.args.get("api_key")
        if api_key and verify_api_key(api_key):
            log.debug("API Key authenticated by @api_key_or_login_required")
            return f(*args, **kwargs)  # Valid API key, allow access

        # If neither is valid, return 401 Unauthorized
        response = {
            "error": "Unauthorized. Please log in or provide a valid API key."
            
        }
        log.debug("API Key was not valid. by @api_key_or_login_required")
        return jsonify(response), 401  # Return JSON response with HTTP 401 status
        
    return decorated_function