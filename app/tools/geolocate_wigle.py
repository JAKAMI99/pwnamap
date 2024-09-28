import sqlite3
import sys
import requests
import random
from app.tools.db import get_db_connection, create_pwned_table


def populate_pwned_data(api_key):
    new_networks = no_geolocation_networks = total_networks = 0

    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT DISTINCT ap_mac, password FROM wpasec')
            wpasec_data = cursor.fetchall()

            cursor.execute('SELECT network_id FROM pwned')
            existing_network_ids = {row[0] for row in cursor.fetchall()}

            random.shuffle(wpasec_data) #shuffle data to increase chance for hits for the next day when running into the API Limit 

            for row in wpasec_data:
                ap_mac, password = row

                if ap_mac not in existing_network_ids:
                    total_networks += 1

                    response = requests.get(
                        f"https://api.wigle.net/api/v2/network/search?netid={ap_mac}",
                        headers={"Authorization": f"Basic {api_key}"}
                    )

                    if response.status_code == 401:
                        print(f"The Wigle API {api_key} Key is not authorized. Validate it in the Settings")
                        sys.exit(1)
                    elif response.status_code == 429:
                        print("❌ Received status code 429: API Limit reached.")
                        sys.exit(1)
                    elif response.status_code == 200:
                        wigle_data = response.json()
                        if 'results' in wigle_data and len(wigle_data['results']) > 0:
                            result = wigle_data['results'][0]
                            name = result.get('ssid')
                            network_id = result.get('netid')
                            encryption = result.get('encryption')
                            latitude = result.get('trilat')
                            longitude = result.get('trilong')
                            network_type = "WIFI"
                            time = result.get('lasttime')

                            print(f"✅📌 Found geolocation for {name}({ap_mac}).")

                            try:
                                cursor.execute('''
                                    INSERT INTO pwned (name, network_id, encryption, latitude, longitude, password)
                                    VALUES (?, ?, ?, ?, ?, ?)
                                ''', (name, network_id, encryption, latitude, longitude, password))
                                new_networks += 1
                            except sqlite3.Error as e:
                                print(f"[PWNED] Got error {e} when inserting entry for network_id: {network_id}")

                            try:
                                cursor.execute('''
                                    INSERT INTO wigle (name, network_id, encryption, latitude, longitude, network_type, time)
                                    VALUES (?, ?, ?, ?, ?, ?, ?)
                                ''', (name, network_id, encryption, latitude, longitude, network_type, time))
                                new_networks += 1
                            except sqlite3.Error as e:
                                print(f"[WIGLE] Got error {e} when inserting entry for network_id: {network_id}")
                        else:
                            no_geolocation_networks += 1
                            print(f"❌ No geolocation for {ap_mac} found...")
                    else:
                        print(f"Error retrieving data for {ap_mac}. Status code: {response.status_code}")
        except Exception as e:
            print("An error occurred:", str(e))
        finally:
            conn.commit()

    return new_networks, no_geolocation_networks, total_networks

def get_key(username):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT wigle FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        return row[0] if row else None

def main():
    if len(sys.argv) < 2:
        print("Usage: python script_name.py <username>")
        return

    print("Geolocate Wigle: Starting")
    username = sys.argv[1]
    api_key = get_key(username)
    create_pwned_table()

    if api_key:
        new_networks, no_geolocation_networks, total_networks = populate_pwned_data(api_key)
        print(f"Processed {total_networks} Networks in total. {new_networks} were new and {no_geolocation_networks} had no geolocation in the WiGLE API.")
    else:
        print("API key not found for the specified username. Set it up in the Settings.")
    
    print("✅ Geolocate Wigle: Finished")

if __name__ == '__main__':
    main()
