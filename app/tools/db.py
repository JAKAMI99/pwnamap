import sqlite3

def get_db_connection():
    conn = sqlite3.connect('app/data/pwnamap.db')
    conn.row_factory = sqlite3.Row
    return conn

def create_pwned_table():
    with get_db_connection() as conn:
        cursor = conn.cursor()
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
        conn.commit()

def format_bssid(bssid):
    return ':'.join(bssid[i:i + 2] for i in range(0, len(bssid), 2))

