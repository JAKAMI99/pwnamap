import requests
import filecmp
import os

def download(mail):
    # Log in
    url_login = "https://www.onlinehashcrack.com/dashboard"
    headers_login = {}
    data_login = {"emailTasks": mail, "submit": ""}
    session = requests.Session()
    response_login = session.post(url_login, headers=headers_login, data=data_login)

    # Check if the login was successful
    if response_login.status_code == 200: # Has to be fixed because server always responds with code 200, even if login was unsuccessful
        print("Login successful!")
        
        # Download CSV file
        url_csv = "https://www.onlinehashcrack.com/wpa-exportcsv"
        response_csv = session.get(url_csv)

        if response_csv.status_code == 200:
            with open("tmp.csv", "wb") as file:
                file.write(response_csv.content)
            print("CSV file successfully downloaded!")
        else:
            print("Error downloading the CSV file.")
    else:
        print("Login failed.")


def compare(file1, file2):
    try:
        if filecmp.cmp(file1, file2): 
            print("CSV doesn't changed since last pull. Ignoring")
        else:
            print("CSV has changed. New information ready for parsing")
    except FileNotFoundError:
        print(f"Asuming first pull since no CSV was found.")
