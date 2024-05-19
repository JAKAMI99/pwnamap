import os
import sqlite3
import csv
import datetime

print("Manual Potfile: Starting")

conn = sqlite3.connect('app/data/pwnamap.db')
cursor = conn.cursor()

directory = 'app/data/potfile/'

total_networks = 0
new_networks = 0  # Counter for new networks
duplicate_networks = 0  # Counter for duplicates

timestamp = datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")


cursor.execute('''CREATE TABLE IF NOT EXISTS "wpasec" (
                    "ap_mac" TEXT,
                    "sta_mac" TEXT,
                    "ssid" TEXT,
                    "password" TEXT,
                    "timestamp" TEXT,
                    UNIQUE ("ap_mac", "sta_mac", "ssid")
                )''')

# Loop through files in the directory
for filename in os.listdir(directory):
    filepath = os.path.join(directory, filename)
    # Open the CSV file and parse its content
    with open(filepath, 'r') as file:
        print(f"Processing potfile {filename}")
        csv_reader = csv.reader(file, delimiter=':')
        for row in csv_reader:
            total_networks += 1
            # Check if the row contains exactly three colons
            if len(row) == 4 or len(row) == 5: # Check if the row is format either like the legacy format or the new 22000 format
                if len(row) == 5: # For new 22000 format which contains 5 field with a total of 4 ":"
                    line = ':'.join(row).split(':', 1)[1] #remove the first datafield
                if len(row) == 4:
                    line = ':'.join(row) # For legacy format, keep the line as is
                # Split the line into its components
                ap_mac, sta_mac, ssid, password = line.split(':')
                # Format MAC from abcdefhgij to ab:cd:ef:gh:ij
                ap_mac = ':'.join(ap_mac[i:i+2].upper() for i in range(0, len(ap_mac), 2))
                sta_mac = ':'.join(sta_mac[i:i+2].upper() for i in range(0, len(sta_mac), 2))
                cursor.execute('''SELECT COUNT(*) FROM "wpasec"
                                    WHERE ap_mac=? AND sta_mac=? AND ssid=?''',
                                (ap_mac, sta_mac, ssid))
                if cursor.fetchone()[0] == 0:
                    cursor.execute('''INSERT INTO "wpasec" (ap_mac, sta_mac, ssid, password, timestamp)
                                        VALUES (?, ?, ?, ?, ?)''',
                                    (ap_mac, sta_mac, ssid, password, timestamp))
                    new_networks += 1
                else:
                    print (f"Network {ssid} has already an entry, skipping")
                    duplicate_networks += 1
            else:
                print(f"Row was not in the expected format for a mode 22000 potfile: {row}")

# Commit changes and close connection
conn.commit()
conn.close()

print("Successfully parsed all new PWNED Networks")
