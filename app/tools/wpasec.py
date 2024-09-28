import requests
import sqlite3
import csv
import datetime
import sys
from app.tools.db import get_db_connection, format_bssid


# Function to create the "wpasec" table if it doesn't exist
def create_wpasec_table():
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS "wpasec" (
                            "ap_mac" TEXT,
                            "sta_mac" TEXT,
                            "ssid" TEXT,
                            "password" TEXT,
                            "timestamp" TEXT,
                            UNIQUE ("ap_mac", "sta_mac", "ssid")
                        )''')
        conn.commit()
    finally:
        conn.close()

# Function to parse CSV content and insert results into the database
def parse_csv(csv_content):
    create_wpasec_table()  # Ensure the table exists
    total_networks = 0
    new_networks = 0  # Counter for new networks
    duplicate_networks = 0  # Counter for duplicates

    csv_reader = csv.reader(csv_content.decode('utf-8').splitlines(), delimiter=':')

    for row in csv_reader:
        if len(row) == 4:
            total_networks += 1
            ap_mac, sta_mac, ssid, password = row

            # Format MAC from abcdefhgij to ab:cd:ef:gh:ij
            ap_mac = format_bssid(ap_mac)
            sta_mac = format_bssid(sta_mac)

            timestamp = datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")

            conn = get_db_connection()
            try:
                cursor = conn.cursor()
                cursor.execute('''INSERT INTO "wpasec" (ap_mac, sta_mac, ssid, password, timestamp)
                                  VALUES (?, ?, ?, ?, ?)''', (ap_mac, sta_mac, ssid, password, timestamp))
                conn.commit()
                new_networks += 1
                print(f"Added new network: {ssid}")
            except sqlite3.IntegrityError:
                duplicate_networks += 1
            finally:
                conn.close()
        else:
            # If there's an incorrect number of columns, raise an error
            raise ValueError(f"Invalid CSV row: {row}")

    print(f"Processed a total of {total_networks} networks, {new_networks} were new networks, {duplicate_networks} were already known or duplicates.")

# Function to download the potfile and return CSV content
def download_potfile(api_key):
    api_url = "https://wpa-sec.stanev.org/?api&dl=1"
    cookies = {'key': api_key}

    try:
        response = requests.get(api_url, cookies=cookies)
        response.raise_for_status()
        return response.content  # Return the CSV content for further processing
    except requests.exceptions.RequestException as e:
        raise Exception(f"HTTP Error: {e}")

# Function to get the API key based on username
def get_key(username):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT wpasec FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        return row[0] if row else None  # Return the API key if found, else None
    finally:
        conn.close()

def main():
    print("WPA-SEC: Starting")
    username = sys.argv[1]  # Assuming you're getting the username as an argument
    api_key = get_key(username)

    if not api_key:
        print(f"No API key found for {username}")
        return

    try:
        csv_content = download_potfile(api_key)
        # Parse the CSV content into the database
        parse_csv(csv_content)
    except Exception as e:
        print(f"An error occurred: {e}")
    print("✅ WPA-SEC: Finished")

if __name__ == "__main__":
    main()
