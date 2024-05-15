import sqlite3, logging

log = logging.getLogger(__name__)

def get_db_connection():
    conn = sqlite3.connect('app/data/pwnamap.db')
    conn.row_factory = sqlite3.Row
    return conn



def create_pwned_table():
    try:
        # Connect to SQLite database
        conn = get_db_connection()
        cursor = conn.cursor()

        # Create the 'pwned' table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pwned (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                network_id TEXT UNIQUE,
                encryption TEXT,
                accuracy REAL,
                latitude REAL,
                longitude REAL,
                password TEXT
            )
        ''')

        # Commit changes
        conn.commit()

    except sqlite3.Error as e:
        # Log the error with a descriptive message
        print(f"Error creating 'pwned' table: {e}")
        raise  # Re-raise the exception if you want the caller to handle it

    finally:
        # Ensure the connection is closed even if an error occurs
        if conn:
            conn.close()


def populate_pwned_data():
    new_networks = 0  # Counter for new networks with geolocation
    no_geolocation_networks = 0  # Counter for networks with no geolocation
    total_networks = 0 # Counter for total processed Networks

    # Connect to SQLite database
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Query wpasec table
        cursor.execute('SELECT ap_mac, password FROM wpasec')
        wpasec_data = cursor.fetchall()

        # Query wigle table and populate pwned table
        for row in wpasec_data:
            ap_mac = row[0]
            password = row[1]

            total_networks += 1 # Counter for total proccessed Networks

            # Convert ap_mac to the format used in the wigle table

            # Query wigle table for the corresponding network_id (case-insensitive matching)
            cursor.execute('SELECT name, network_id, encryption, accuracy, latitude, longitude FROM wigle WHERE lower(network_id) = lower(?)', (ap_mac,))
            wigle_data = cursor.fetchone()

            # If data is found in the wigle table, insert into pwned table
            if wigle_data:
                name, network_id, encryption, accuracy, latitude, longitude = wigle_data
                # Check if the name already exists in pwned table (to avoid duplicates based on 'name')
                cursor.execute('SELECT name FROM pwned WHERE name = ?', (name,))
                existing_record = cursor.fetchone()
                if not existing_record:
                    new_networks += 1
                    cursor.execute('''
                        INSERT INTO pwned (name, network_id, encryption, accuracy, latitude, longitude, password)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (name, network_id, encryption, accuracy, latitude, longitude, password))
            else:
                no_geolocation_networks += 1

    except Exception as e:
        print("An error occurred:", str(e))
    finally:
        # Commit changes and close the connection
        conn.commit()
        conn.close()

    return new_networks, no_geolocation_networks, total_networks


def main():
    # Create the 'pwned' table if it doesn't exist
    create_pwned_table()
    # Populate data into the 'pwned' table
    print("Local Geolocate: Starting")
    new_networks, no_geolocation_networks, total_networks = populate_pwned_data()
    print(f"Processed {total_networks} Networks in total. {new_networks} were new and {no_geolocation_networks} had no geolocation in the local DB ")
    print("✅Local Geolocate: Finished")

if __name__ == "__main__":
    main()  # Ensure this is at the end of the script
