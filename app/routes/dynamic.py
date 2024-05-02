from flask import render_template, jsonify, request, Blueprint, redirect, session, url_for, send_from_directory
import sqlite3, os, logging
from .auth import login_required, authenticate_user

handshake_path = "app/data/handshakes/"
handshake_path_abs = os.path.abspath(handshake_path)
log = logging.getLogger(__name__)
dynamic_bp = Blueprint('dynamic', __name__)

def get_db_connection():
    conn = sqlite3.connect('app/data/pwnamap.db')
    conn.row_factory = sqlite3.Row
    return conn


@dynamic_bp.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        # Handle POST request for authentication
        username = request.form['username']
        password = request.form['password']
        
        if authenticate_user(username, password):
            log.debug(f"Request Path: {request.path} - Authenticated user: {username}")
            return redirect('/')
        
        else:
            error = "Invalid username or password"
            log.warn(f"User {username} could not be authenticated.")
    
    # Render the login template with the error message
    return render_template('login.html', error=error)

@dynamic_bp.route('/stats')
@login_required
def stats():
    # Initialize counts with default values
    bt_count = 0
    ble_count = 0
    wifi_count = 0
    gsm_count = 0
    lte_count = 0
    pwned_count = 0
    cracked_count = 0
    total_handshakes = 0

    # Connect to the SQLite database
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if a table exists in SQLite
    def table_exists(table_name):
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
        return cursor.fetchone() is not None

    try:
        # Check if the 'wigle' table exists before executing queries
        if table_exists('wigle'):
            # Define SQL queries to count records for each condition
            bt_count_query = "SELECT COUNT(*) FROM wigle WHERE network_type = 'BT'"
            ble_count_query = "SELECT COUNT(*) FROM wigle WHERE network_type = 'BLE'"
            wifi_count_query = "SELECT COUNT(*) FROM wigle WHERE network_type = 'WIFI'"
            gsm_count_query = "SELECT COUNT(*) FROM wigle WHERE network_type = 'GSM'"
            lte_count_query = "SELECT COUNT(*) FROM wigle WHERE network_type = 'LTE'"

            # Execute the queries and retrieve results
            cursor.execute(bt_count_query)
            bt_count = cursor.fetchone()[0]

            cursor.execute(ble_count_query)
            ble_count = cursor.fetchone()[0]

            cursor.execute(wifi_count_query)
            wifi_count = cursor.fetchone()[0]

            cursor.execute(gsm_count_query)
            gsm_count = cursor.fetchone()[0]

            cursor.execute(lte_count_query)
            lte_count = cursor.fetchone()[0]                        


        # Check if the 'wpasec' table exists
        if table_exists('wpasec'):
            cracked_count_query = "SELECT COUNT(*) FROM wpasec"
            cursor.execute(cracked_count_query)
            cracked_count = cursor.fetchone()[0]

        # Check if the 'pwned' table exists
        if table_exists('pwned'):
            pwned_count_query = "SELECT COUNT(*) FROM pwned"
            cursor.execute(pwned_count_query)
            pwned_count = cursor.fetchone()[0]

    except sqlite3.Error as e:
        # Log the error with the detailed message
        log.error(f"Request Path: {request.path} - SQLite Error: {str(e)}")

    # Get the total number of files in the handshakes directory
    handshake_dir = "app/data/handshakes/"
    if os.path.exists(handshake_dir):
        total_handshakes = len([f for f in os.listdir(handshake_dir) if os.path.isfile(os.path.join(handshake_dir, f))])
    else:
        total_handshakes = 0
    
    # Close the database connection
    conn.close()

    # Render the template with counts
    return render_template(
        'stats.html',
        bt_count=bt_count,
        ble_count=ble_count,
        wifi_count=wifi_count,
        pwned_count=pwned_count,
        cracked_count=cracked_count,
        total_handshakes=total_handshakes,
        gsm_count=gsm_count,
        lte_count=lte_count
    )

    
@dynamic_bp.route('/logout')
def logout():
    # Clear the session
    session.clear()
    log.debug(f"Request Path: {request.path} - User was successfully logged out ")
    # Redirect to the home page or any other desired page
    return redirect("login")

@dynamic_bp.route('/handshakes')
@login_required
def list_handshakes():
    files = os.listdir(handshake_path_abs)
    return render_template("handshakes.html", files=files)

# Route to download a specific file by its filename
@dynamic_bp.route("/handshakes/<filename>")
@login_required
def download_handshake(filename):
    try:
        # Check if the file exists in the specified absolute folder
        if filename in os.listdir(handshake_path_abs):
            return send_from_directory(handshake_path_abs, filename, as_attachment=True)
        else:
            log.error(f"Request Path: {request.path} - The filename {filename} was not found")
            return "File not found", 404
    except Exception as e:
        log.error(f"Request Path: {request.path} - An error occured: {str(e)} ")
        return "Error accessing file", 500
