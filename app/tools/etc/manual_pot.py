import sys
import sqlite3
import csv


#################################################################
#Takes the output from "hashcat -m 22000 example.hc22000 --show"#
#for manual inserting self cracked handshakes into the db       #
#################################################################


# Check if the CSV file path is provided as an argument
if len(sys.argv) != 2:
    print("Usage: python script_name.py <csv_file_path>")
    sys.exit(1)

csv_file_path = sys.argv[1]

conn = sqlite3.connect('data/pwnamap.db')
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS "wpasec" (
                    "ap_mac" TEXT,
                    "sta_mac" TEXT,
                    "ssid" TEXT,
                    "password" TEXT,
                    PRIMARY KEY ("ap_mac", "sta_mac", "ssid")
                )''')

# Open the CSV file and parse its content
with open(csv_file_path, 'r', newline='', encoding='utf-8') as csvfile:
    csv_reader = csv.reader(csvfile, delimiter=':')
    for row in csv_reader:
        # Ignore characters until the first ":" and remove the ":" itself
        line = ':'.join(row).split(':', 1)[1]
        # Split the line into its components
        ap_mac, sta_mac, ssid, password = line.split(':')
        # Convert mac addresses to uppercase and format them
        ap_mac = ':'.join(ap_mac[i:i+2].upper() for i in range(0, len(ap_mac), 2))
        sta_mac = ':'.join(sta_mac[i:i+2].upper() for i in range(0, len(sta_mac), 2))
        cursor.execute('''SELECT COUNT(*) FROM "wpasec"
                            WHERE ap_mac=? AND sta_mac=? AND ssid=?''',
                        (ap_mac, sta_mac, ssid))
        if cursor.fetchone()[0] == 0:
            cursor.execute('''INSERT INTO "wpasec" (ap_mac, sta_mac, ssid, password)
                                VALUES (?, ?, ?, ?)''',
                            (ap_mac, sta_mac, ssid, password))

conn.commit()
conn.close()
print("Successfully parsed all new PWNED Networks")
