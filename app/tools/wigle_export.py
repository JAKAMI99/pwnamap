import requests, os, sys, sqlite3
import xml.etree.ElementTree as ET


def get_db_connection():
    conn = sqlite3.connect('app/data/pwnamap.db')
    conn.row_factory = sqlite3.Row
    return conn

raw_kml_path = "app/data/wigle/raw_kml/"




def sanitize_filename(filename):
    """Sanitize the filename by removing disallowed characters."""
    allowed_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-_')
    return ''.join(c for c in filename if c in allowed_chars)

def download(api_key, raw_kml_path):
    total_files = 0  # Counter for total files to be downloaded
    downloaded_files = 0  # Counter for downloaded files
    up_to_date = True

    url = "https://api.wigle.net/api/v2/file/transactions?pagestart=0"
    headers = {
        "accept": "application/json",
        "authorization": f"Basic {api_key}"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        data = response.json()

        if data.get("success", False):
            results = data.get("results", [])

            for result in results:
                transid = result.get("transid", "")
                file_name = result.get("fileName", "")

                # Check if the file is not present in the current directory
                # deepcode ignore PT: Not user controlled and trusted input
                if file_name and not os.path.isfile(os.path.join(raw_kml_path, f"{sanitize_filename(file_name).replace('.csv', '.kml')}")):
                    total_files += 1  # Increment the counter

        if total_files != 0:
            print(f"Total files to download from wigle: {total_files}")
            print("Starting download (this might take a while, wigle.org is painfully slow)")
            needs_processing = True  # Set to True only when there are missing uploads
        else:
            print("No missing uploads, nothing to download from wigle.org")
            needs_processing = False  # Set to False when there are no missing uploads

        for result in results:
            transid = result.get("transid", "")
            file_name = result.get("fileName", "")

            # Check if the file is not present in the current directory
            # deepcode ignore PT: Not user controlled and trusted input
            if file_name and not os.path.isfile(os.path.join(raw_kml_path, f"{sanitize_filename(file_name).replace('.csv', '.kml')}")):
                up_to_date = False
                kml_url = f"https://api.wigle.net/api/v2/file/kml/{transid}"

                # Make request for missing file with the correct accept header
                kml_headers = {
                    "accept": "application/vnd.google-earth.kml+xml",
                    "authorization": f"Basic {api_key}"
                }
                kml_response = requests.get(kml_url, headers=kml_headers)
                kml_response.raise_for_status()

                # Check if the response contains data
                if kml_response.text.strip():  
                    # deepcode ignore PT: Not user controlled and trusted input
                    with open(os.path.join(raw_kml_path, f"{sanitize_filename(file_name).replace('.csv', '.kml')}"), "wb") as kml_file:
                        kml_file.write(kml_response.text.encode('utf-8'))

                    downloaded_files += 1  # Increment the counter
                    print(f"KML file for id {transid} successfully saved.")
                else:
                    print(f"KML file for id {transid} is empty, skipping. (This happens when you download right after uploading to wigle, try it again in a few minutes)")

                if downloaded_files == total_files:
                    print("All missing uploads have been downloaded.")
                    break
        return needs_processing  # Return needs_processing only when there are missing uploads
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            print("Authentication error: Please check your API key.")
            raise  # Re-raise the exception to stop the script execution
        else:
            print("An error occurred:", str(e))



def process(directory):
    # Connect to SQLite database (create one if it doesn't exist)
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create a table to store the parsed data
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS wigle (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            network_id TEXT UNIQUE,  -- Add UNIQUE constraint to network_id
            encryption TEXT,
            time TEXT,
            signal REAL,
            accuracy REAL,
            network_type TEXT,
            latitude REAL,
            longitude REAL
        )
    ''')

    # Parse KML files in the given directory
    for filename in os.listdir(directory):
        if filename.endswith('.kml'):
            kml_file_path = os.path.join(directory, filename)

            # deepcode ignore InsecureXmlParser: Wigle is a trusted source
            tree = ET.parse(kml_file_path)
            root = tree.getroot()

            # Iterate through Placemark elements
            for placemark in root.findall('.//{http://www.opengis.net/kml/2.2}Placemark'):
                name = placemark.find('{http://www.opengis.net/kml/2.2}name').text
                description = placemark.find('{http://www.opengis.net/kml/2.2}description').text
                coordinates = placemark.find('.//{http://www.opengis.net/kml/2.2}coordinates').text.split(',')

                # Extract relevant information from the description
                network_id = description.split('Network ID: ')[1].split('\n')[0]

                # Check if a record with the same network_id already exists
                cursor.execute('SELECT network_id FROM wigle WHERE network_id = ?', (network_id,))
                existing_record = cursor.fetchone()

                if existing_record is None:
                    # If the record doesn't exist, proceed with insertion
                    encryption = description.split('Encryption: ')[1].split('\n')[0] if 'Encryption: ' in description else None
                    time = description.split('Time: ')[1].split('\n')[0]
                    signal = float(description.split('Signal: ')[1].split('\n')[0])
                    accuracy = float(description.split('Accuracy: ')[1].split('\n')[0])
                    network_type = description.split('Type: ')[1].split('\n')[0]

                    # Extract latitude and longitude
                    longitude, latitude = map(float, coordinates)

                    # Insert data into the SQLite database
                    cursor.execute('''
                        INSERT INTO wigle (
                            name, network_id, encryption, time, signal, accuracy, network_type, latitude, longitude
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (name, network_id, encryption, time, signal, accuracy, network_type, latitude, longitude))

    # Commit changes and close the connection
    conn.commit()
    conn.close()
    print("KML files have been imported into sqlite db")

def get_key(username):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT wigle FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    api_key = row[0] if row else None

    conn.close()

    return api_key

def main():
    print("Wigle Downloader: Starting")
    # Check for API key in creds.txt
    username = sys.argv[1]
    api_key = get_key(username)
    if api_key:  # Ensure API key exists before attempting download
        download(api_key, raw_kml_path)  # Pass raw_kml_path as an argument
        process(raw_kml_path)
    else:
        print("API key not found for the specified username.")
    print("Wigle Downloaded: Finished ✅")
    

if __name__ == '__main__':
    main()