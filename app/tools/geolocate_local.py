import sqlite3
import logging

log = logging.getLogger(__name__)

DB_PATH = 'app/data/pwnamap.db'

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def create_pwned_table():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pwned (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                network_id TEXT UNIQUE,
                encryption TEXT,
                accuracy REAL,
                latitude REAL,
                longitude REAL,
                password TEXT,
                timestamp TEXT
            )
        ''')

        # Optional index for speed if you run this multiple times
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_wigle_network_id ON wigle(lower(network_id))')

        conn.commit()

    except sqlite3.Error as e:
        print(f"Error creating 'pwned' table: {e}")
        raise
    finally:
        if conn:
            conn.close()


def populate_pwned_data():
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Speed optimization: reduce disk writes
        cursor.execute('PRAGMA synchronous = OFF')
        cursor.execute('PRAGMA journal_mode = MEMORY')

        # Count total networks to process
        cursor.execute('SELECT COUNT(*) FROM wpasec')
        total_networks = cursor.fetchone()[0]

        # Perform the join + insert in one fast SQL statement
        cursor.execute('''
            INSERT OR IGNORE INTO pwned (name, network_id, encryption, accuracy, latitude, longitude, password)
            SELECT 
                w.name, w.network_id, w.encryption, w.accuracy, w.latitude, w.longitude, wp.password
            FROM wpasec AS wp
            JOIN wigle AS w
                ON lower(w.network_id) = lower(wp.ap_mac)
        ''')
        new_networks = cursor.rowcount

        # Count how many had no matching geolocation
        cursor.execute('''
            SELECT COUNT(*) 
            FROM wpasec 
            WHERE lower(ap_mac) NOT IN (SELECT lower(network_id) FROM wigle)
        ''')
        no_geolocation_networks = cursor.fetchone()[0]

        conn.commit()

    except Exception as e:
        print("An error occurred:", str(e))
        new_networks = no_geolocation_networks = total_networks = 0
    finally:
        conn.close()

    return new_networks, no_geolocation_networks, total_networks


def main():
    create_pwned_table()

    print("Local Geolocate: Starting")
    new_networks, no_geolocation_networks, total_networks = populate_pwned_data()
    print(f"Processed {total_networks} networks in total. {new_networks} were new and {no_geolocation_networks} had no geolocation in the local DB.")
    print("✅ Local Geolocate: Finished")


if __name__ == "__main__":
    main()
