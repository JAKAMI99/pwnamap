import sqlite3, sys, requests

def get_db_connection():
    conn = sqlite3.connect('app/data/pwnamap.db')
    conn.row_factory = sqlite3.Row
    return conn

def create_pwned_table(sqlite_file):
    # Connect to SQLite database
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create the 'pwned' table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pwned (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            network_id TEXT,
            encryption TEXT,
            latitude REAL,
            longitude REAL,
            password TEXT,
            UNIQUE (network_id)
        )
    ''')

    # Commit changes and close the connection
    conn.commit()
    conn.close()


def populate_pwned_data(api_key):
    new_networks = 0  # Counter for new networks with geolocation
    no_geolocation_networks = 0  # Counter for networks with no geolocation
    total_networks = 0  # Counter for total processed Networks

    # Connect to SQLite database
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Query wpasec table
        cursor.execute('SELECT ap_mac, password FROM wpasec')
        wpasec_data = cursor.fetchall()

        # Query pwned table to get existing network_ids
        cursor.execute('SELECT network_id FROM pwned')
        existing_network_ids = {row[0] for row in cursor.fetchall()}

        # Query WiGLE API and populate pwned table
        for row in wpasec_data:
            ap_mac = row[0]
            password = row[1]

            # Convert ap_mac to the format used in the WiGLE API

            # Check if the entry already exists in pwned table
            if ap_mac not in existing_network_ids:
                total_networks += 1  # Increment total processed Networks counter


                # Call WiGLE API to retrieve network information
                response = requests.get(
                    f"https://api.wigle.net/api/v2/network/search?netid={ap_mac}",
                    headers={"Authorization": f"Basic {api_key}"})
                if response.status_code == 401:
                    print(f"The Wigle API {api_key} Key is not authorized. Validate it in the Settings")
                    sys.exit
                if response.status_code == 200:
                    wigle_data = response.json()
                    if 'results' in wigle_data and len(wigle_data['results']) > 0:

                        result = wigle_data['results'][0]
                        name = result.get('ssid')
                        network_id = result.get('netid')
                        encryption = result.get('encryption')
                        latitude = result.get('trilat')
                        longitude = result.get('trilong')
                        network_type = "WIFI" #Static value since only WIFI is expected (For local db)
                        time = result('lasttime')

                        print(f"✅📌 Found geolocation for {name}({ap_mac}).")


                        try:
                            cursor.execute('''
                                INSERT INTO pwned (name, network_id, encryption, latitude, longitude, password)
                                VALUES (?, ?, ?, ?, ?, ?)
                            ''', (name, network_id, encryption, latitude, longitude, password))
                            new_networks += 1
                        except sqlite3.Error as e:
                            print(f"Got error {e}")
                            print(f"Got error {e} when inserting  entry for network_id: {network_id}")

                        try:
                            cursor.execute('''
                                INSERT INTO wigle (name, network_id, encryption, latitude, longitude, network_type, time)
                                VALUES (?, ?, ?, ?, ?, ?, ?)
                            ''', (name, network_id, encryption, latitude, longitude, network_type, time))
                            new_networks += 1
                        except sqlite3.Error as e:
                            print(f"Got error {e} when inserting  entry for network_id: {network_id}")
                            print(f"Error ")

                    else:
                        no_geolocation_networks += 1
                        print(f"❌ No geolocation for {ap_mac} found...")
                else:
                    print(f"Error retrieving data for {ap_mac}. Status code: {response.status_code}")

    except Exception as e:
        print("An error occurred:", str(e))
    finally:
        # Commit changes and close the connection
        conn.commit()
        conn.close()

    return new_networks, no_geolocation_networks, total_networks

def get_key(username):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT wigle FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    api_key = row[0] if row else None

    conn.close()

    return api_key


def main():
    if len(sys.argv) < 2:
        print("Usage: python script_name.py <username>")
        return
    # Check for API key in creds.txt
    print("Geolocate Wigle: Starting")
    username = sys.argv[1]
    api_key = get_key(username)
    if api_key:  # Ensure API key exists before attempting download
        new_networks, no_geolocation_networks, total_networks = populate_pwned_data(api_key)
        print(f"Processed {total_networks} Networks in total. {new_networks} were new and {no_geolocation_networks} had no geolocation in the WiGLE API ")
    else:
        print("API key not found for the specified username. Set it up in the Settings")
    print(" Geolocate Wigle: Finished")

if __name__ == '__main__':
    main()
