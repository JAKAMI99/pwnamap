import requests

email = "example@email.com"

# Log in
url_login = "https://www.onlinehashcrack.com/dashboard"
headers_login = {}
data_login = {"emailTasks": email, "submit": ""}
session = requests.Session()
response_login = session.post(url_login, headers=headers_login, data=data_login)

# Check if the login was successful
if response_login.status_code == 200:
    print("Login successful!")

    # Download CSV file
    url_csv = "https://www.onlinehashcrack.com/wpa-exportcsv"
    response_csv = session.get(url_csv)

    if response_csv.status_code == 200:
        with open("output.csv", "wb") as file:
            file.write(response_csv.content)
        print("CSV file successfully downloaded!")
    else:
        print("Error downloading the CSV file.")
else:
    print("Login failed.")
