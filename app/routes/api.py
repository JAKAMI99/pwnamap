from flask import jsonify, request, Response, stream_with_context, Blueprint, session, send_file
import logging
import os
import re
import subprocess
from datetime import date

from app.db import get_db
from werkzeug.utils import secure_filename
from .auth import verify_api_key, login_required, api_key_or_login_required

api_bp = Blueprint('api', __name__)
log = logging.getLogger(__name__)


# vibecoded: normalize the wigle `time` column to a comparable string.
# wigle.time is TEXT, but the importer format varies (ISO-8601,
# "YYYY-MM-DD HH:MM:SS", epoch-as-string, ...). We compare by prefix
# substr on the first 10/19 chars which matches ISO-prefixed formats
# and gracefully skips non-matching rows (NULL fail-safe).
def _time_filter_clause(column: str, date_from: str | None, date_to: str | None) -> tuple[str, list]:
    """Build a SQL fragment + params for inclusive date-range filtering
    on a TEXT timestamp column.

    date_from / date_to are ISO 'YYYY-MM-DD' (from <input type="date">).
    Empty / None means 'no bound on that side'. date_to is extended to
    end-of-day (T23:59:59) so a single-day selection includes that day.
    """
    if not date_from and not date_to:
        return "", []

    def _iso(d: str | None, end_of_day: bool) -> str | None:
        if not d:
            return None
        try:
            dt = date.fromisoformat(d)
        except ValueError:
            log.warning("Ignoring malformed date filter: %r", d)
            return None
        return dt.strftime("%Y-%m-%d") + ("T23:59:59" if end_of_day else "T00:00:00")

    iso_from = _iso(date_from, end_of_day=False)
    iso_to = _iso(date_to, end_of_day=True)

    parts = []
    params: list = []
    if iso_from:
        parts.append(f"substr({column}, 1, {len(iso_from)}) >= ?")
        params.append(iso_from)
    if iso_to:
        parts.append(f"substr({column}, 1, {len(iso_to)}) <= ?")
        params.append(iso_to)

    if not parts:
        return "", []
    return " AND (" + " AND ".join(parts) + ")", params


POT_UPLOAD_FOLDER = 'app/data/potfile'
ALLOWED_EXTENSIONS = {'pot', '22000', 'potfile'}



def get_db_connection():
    conn = get_db()
    return conn



tools = {
    'wpasec': 'app/tools/wpasec.py',
    'wigle_export': 'app/tools/wigle_export.py',
    'geolocate_local': 'app/tools/geolocate_local.py',
    'geolocate_wigle': 'app/tools/geolocate_wigle.py',
    'manual_pot': 'app/tools/manual_pot.py',
}

@api_bp.route('/api/tools', methods=['POST'])
@login_required
def run_script():
    # Get script name and optional arguments from the POST request
    script_name = request.json.get('script_name')  # The script to be run
    
    if not script_name:
        log.warn(f"Request Path: {request.path} - No script was provided")
        return {"status": "error", "message": "Script name not provided."}, 400
    else:

        if script_name not in tools:
            # Error handling for unknown scripts
            log.error(f"Request Path: {request.path} - The script {script_name} was not found")
            return {"status": "error", "message": f"Script not found, available options are {', '.join(tools.keys())}"}, 404

        
        if script_name in ['geolocate_wigle', 'wigle_export', 'wpasec', 'manual_pot']:
            username = session.get("username")
            command = ["python", "-u", tools[script_name], username]
            log.debug("Tool command: %s", command)
            # deepcode ignore CommandInjection: There is no actual userinput that flows into the subprocess. The username gets retrieved trough the cookie which is serversite signed and can not be modified. The script_name gets checked against a dictionary
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)


        if script_name in ['geolocate_local']:
            command = ["python", "-u", tools[script_name]]  # -u for unbuffered output
            log.debug("Tool command: %s", command)
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)


        def generate_output():
            try:
                for line in iter(process.stdout.readline, ''):
                    yield line
            finally:
                process.stdout.close()
                process.wait()

    return Response(stream_with_context(generate_output()), content_type='text/plain')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@api_bp.route('/api/pot_upload', methods=['POST'])
@api_key_or_login_required
def upload_pot():
    if 'file' not in request.files:
        return {"status": "error", "message": "No file part"}, 400
    file = request.files['file']
    if file.filename == '':
        return {"status": "error", "message": "No selected file"}, 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(POT_UPLOAD_FOLDER, filename))
        return {"status": "success", "message": "File uploaded successfully"}, 200
    else:
        return {"status": "error", "message": "File type not allowed"}, 400


@api_bp.route('/api/wardrive', methods=['GET'])
@login_required
def get_street_overlay():
    log.info(f"Current working directory: {os.getcwd()}")

    # Correct path to the GeoJSON file
    geojson_file = "app/data/wardrive/wardrive_overlay.json"
    log.debug(f"GeoJSON file path: {geojson_file}")

    # Check if the file exists before attempting to serve it
    if os.path.exists(geojson_file):
        # Serve the GeoJSON file with a custom download name
        return send_file(geojson_file, as_attachment=False, download_name="wardrive_overlay")
    else:
        # Return an error response if the file doesn't exist
        return {"error": "GeoJSON wardrive overlay not found"}, 404



@api_bp.route('/api/pwnamap')
@login_required
def pwnapi():
    # vibecoded: optional date filter via ?date_from=YYYY-MM-DD&date_to=YYYY-MM-DD.
    # pwned has no time column, so the filter joins wpasec.timestamp via network_id
    # (=ap_mac) when dates are present. Rows without a matching wpasec entry are
    # dropped from the dated view -- this is intentional: a "cracked" network
    # without a wpasec record is probably an old data import.
    log.debug("Request Path: %s  was called", request.path)

    date_from = request.args.get('date_from', '').strip() or None
    date_to = request.args.get('date_to', '').strip() or None

    conn = get_db_connection()
    cursor = conn.cursor()

    if date_from or date_to:
        # Date-filtered: only cracked networks with a wpasec row in range.
        clause, params = _time_filter_clause('wpasec.timestamp', date_from, date_to)
        cursor.execute(
            f"""SELECT pwned.* FROM pwned
               JOIN wpasec ON wpasec.ap_mac = pwned.network_id
               WHERE 1=1{clause}""",
            params,
        )
    else:
        cursor.execute('SELECT * FROM pwned')

    rows = cursor.fetchall()
    column_names = [description[0] for description in cursor.description]
    conn.close()

    pwned_data = [dict(zip(column_names, row)) for row in rows]
    return jsonify(pwned_data)


@api_bp.route('/api/explore')
@api_key_or_login_required
def exploreapi():
    # Connect to SQLite database
    log.debug(f"Request Path: {request.path} was called ")
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get search query and filters from request parameters
    name_query = request.args.get('name', '')
    network_id_filter = request.args.get('network_id', '')
    encryption_filter = request.args.get('encryption', '')
    network_type_filter = request.args.get('network_type', '')
    exclude_no_ssid = request.args.get('exclude_no_ssid', 'false')  # New filter to exclude "(no SSID)"
    
    # Construct base SQL query
    sql_query = 'SELECT * FROM wigle WHERE 1=1'
    
    # Construct parameterized query and parameters list
    parameters = []
    if name_query:
        sql_query += " AND UPPER(name) LIKE UPPER(?)"
        parameters.append(f'%{name_query}%')
    if network_id_filter:
        sql_query += " AND UPPER(network_id) = UPPER(?)"
        parameters.append(network_id_filter)
    if encryption_filter:
        if encryption_filter == "None":
            sql_query += " AND encryption IN ('None','Unknown')"
        else:
            sql_query += " AND encryption = ?"
            parameters.append(encryption_filter)
    if network_type_filter:
        sql_query += " AND network_type = ?"
        parameters.append(network_type_filter)

    # If "exclude_no_ssid" is true, add condition to exclude "(no SSID)"
    if exclude_no_ssid.lower() == 'true':  # Convert to lowercase for case-insensitive comparison
        sql_query += " AND name != '(no SSID)'"

    # vibecoded: optional date-range filter on wigle.time.
    date_from = request.args.get('date_from', '').strip() or None
    date_to = request.args.get('date_to', '').strip() or None
    time_clause, time_params = _time_filter_clause('time', date_from, date_to)
    sql_query += time_clause
    parameters.extend(time_params)

    # Execute parameterized SQL query
    cursor.execute(sql_query, parameters)
    rows = cursor.fetchall()
    
    # Get column names
    column_names = [description[0] for description in cursor.description]
    
    # Close database connection
    conn.close()
    
    # Construct list of dictionaries with column names as keys
    pwned_data = [dict(zip(column_names, row)) for row in rows]
    
    # Return data as JSON
    return jsonify(pwned_data)


@api_bp.route('/api/credentials', methods=['GET', 'POST'])
@login_required
def credentials():
    conn = get_db_connection()
    cursor = conn.cursor()
    username = session['username']
    if request.method == 'GET':
        log.debug(f"Request Path: {request.path} - Credentials API was called with a GET request")
        try:

            # Retrieve credentials for the current user from the SQLite database
            cursor.execute("SELECT wigle, wpasec, api_key FROM users WHERE username = ?", (username,))
            row = cursor.fetchone()
            if row:
                credentials = {'wigle': row[0], 'wpasec': row[1], 'pwnamap': row[2]}
                return jsonify(credentials)
            else:
                return jsonify({'error': 'User credentials not found'}), 404
        except Exception as e:
            log.error(f"Request Path: {request.path} - the following error occured: {e}")
            return jsonify({'error': str(e)}), 500

            
    
    elif request.method == 'POST':
        log.info(f"Credentials API was called with a POST request")
        try:
            
            # Retrieve the new values of the fields from the request
            new_wigle = request.json.get('wigle')
            new_wpasec = request.json.get('wpasec')
            
            # Update the credentials for the current user
            if new_wigle is not None:
                cursor.execute("UPDATE users SET wigle = ? WHERE username = ?", (new_wigle, username))
            if new_wpasec is not None:
                cursor.execute("UPDATE users SET wpasec = ? WHERE username = ?", (new_wpasec, username))
            
            conn.commit()
            conn.close()
            log.info("Request Path: {request.path} - Credentials (API Keys) were updated successfully")
            return jsonify({'message': 'Credentials updated successfully'})
        
        except Exception as e:
            log.error(f"Request Path: {request.path} - When setting up new credentials (API Keys) the following error occured: {e}")
            return jsonify({'error': str(e)}), 500


def sanitize_filename(filename):
    # Remove any characters that are not alphanumeric, underscore, or hyphen
    sanitized_filename = re.sub(r'[^\w\-\.]', '_', filename)
    log.debug(f"Santizied a filename to {sanitize_filename}")
    return sanitized_filename

@api_bp.route('/api/upload', methods=['POST'])
def upload_file():
    # Verify API key
    api_key = request.headers.get('X-API-KEY')
    if api_key is None:
        log.error("Request Path: {request_path} - API key not found in request headers")
    else:
        log.info(f"API key retrieved: {api_key}")
    if not verify_api_key(api_key):
        log.info(f"Request Path: {request.path} - Could not verify the following API-key {api_key}")
        return jsonify({'error': 'Invalid API key'}), 401
        
    
    # Check for file in request
    if 'file' not in request.files:
        log.warn("Request Path: {request.path} - No file in request ")
        return jsonify({'error': 'No file part in the request'}), 400
    
    file = request.files['file']
    
    # Check if file name is empty
    if file.filename == '':
        log.warn("Request Path: {request.path} - No filename in request ")
        return jsonify({'error': 'No file selected for uploading'}), 400
    
    # Sanitize file name
    filename = sanitize_filename(file.filename)
    
    # Directory where files are stored
    data_dir = "app/data/handshakes/"
    file_path = os.path.join(data_dir, filename)
    
    # Check if file already exists
    if os.path.exists(file_path):
        log.info("Request Path: {request.path} - File already submitted ")        
        return jsonify({'message': 'Already submitted'}), 200  # Return a success status code with a custom message

    
    # Save file securely
    file.save(file_path)
    
    return jsonify({'message': 'File uploaded successfully', 'filename': filename}), 200
