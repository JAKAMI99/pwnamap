import requests, os, sys, sqlite3, shutil
import xml.etree.ElementTree as ET

from app.tools.db import get_db_connection

new_kml = "app/data/wigle/new_kml/"
old_kml = 'app/data/wigle/raw_kml'

def sanitize_filename(filename):
    """Sanitize the filename by removing disallowed characters."""
    allowed_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-_')
    return ''.join(c for c in filename if c in allowed_chars)

def download(api_key, old_kml, new_kml):
    total_files = 0  # Counter for total files to be downloaded
    downloaded_files = 0  # Counter for downloaded files

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
                if file_name and not os.path.isfile(os.path.join(old_kml, f"{sanitize_filename(file_name).replace('.csv', '.kml')}")):
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
            if file_name and not os.path.isfile(os.path.join(old_kml, f"{sanitize_filename(file_name).replace('.csv', '.kml')}")):
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
                    with open(os.path.join(new_kml, f"{sanitize_filename(file_name).replace('.csv', '.kml')}"), "wb") as kml_file:
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
            print(f"An error occurred:{e}")



def process(new_kml, old_kml):
    # Create a connection to the SQLite database
    conn = get_db_connection()
    cursor = conn.cursor()

    # Ensure the necessary table exists in the SQLite database
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS wigle (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            network_id TEXT UNIQUE,
            encryption TEXT,
            time TEXT,
            signal REAL,
            accuracy REAL,
            network_type TEXT,
            latitude REAL,
            longitude REAL
        )
    ''')

    # Process and move each KML file from new_kml to old_kml
    for filename in os.listdir(new_kml):
        if filename.endswith('.kml'):
            # Full source path of the file to process
            source_path = os.path.join(new_kml, filename)

            # Parse the KML file
            try:
                tree = ET.parse(source_path)
                root = tree.getroot()

                # Extract data from the KML file (details might vary depending on your structure)
                for placemark in root.findall('.//{http://www.opengis.net/kml/2.2}Placemark'):
                    name = placemark.find('{http://www.opengis.net/kml/2.2}name').text
                    description = placemark.find('{http://www.opengis.net/kml/2.2}description').text
                    coordinates = placemark.find('.//{http://www.opengis.net/kml/2.2}coordinates').text.split(',')

                    # Extract necessary information from the description
                    network_id = description.split('Network ID: ')[1].split('\n')[0]
                    encryption = description.split('Encryption: ')[1].split('\n')[0] if 'Encryption' in description else None
                    time = description.split('Time: ')[1].split('\n')[0]
                    signal = float(description.split('Signal: ')[1].split('\n')[0])
                    accuracy = float(description.split('Accuracy: ')[1].split('\n')[0])
                    network_type = description.split('Type: ')[1].split('\n')[0]

                    # Extract latitude and longitude
                    longitude, latitude = map(float, coordinates)

                    # Insert or replace data in the SQLite database
                    cursor.execute('''
                        INSERT OR REPLACE INTO wigle (
                            name, network_id, encryption, time, signal, accuracy, network_type, latitude, longitude
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (name, network_id, encryption, time, signal, accuracy, network_type, latitude, longitude))
                
                # Now move the processed file to the old_kml directory
                destination_path = os.path.join(old_kml, filename)  # Full destination path
                shutil.move(source_path, destination_path)  # Move the file

            except ET.ParseError:
                print(f"Error parsing the KML file '{filename}'. Skipping.")
            except FileNotFoundError:
                print(f"File '{filename}' not found. Skipping.")
            except PermissionError:
                print(f"Permission denied when trying to move '{filename}' to '{old_kml}'.")
            except Exception as e:
                print(f"Error occurred while processing '{filename}': {e}")

    # Commit the changes to the database and close the connection
    conn.commit()
    conn.close()

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
        if download(api_key, old_kml, new_kml): # Checks for new uploads and then checks if data was downloaded
            process(new_kml, old_kml) # Processes all new downloads
            print("Processing completed")
        else:
            print("No new files to process")
    else:
        print("API key not found for the specified username.")
    print("✅ Wigle Downloaded: Finished")
    

if __name__ == '__main__':
    main()