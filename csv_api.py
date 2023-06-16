import requests, filecmp, os, pandas, shutil, html



# Variables for file operations (comparing/download/rename)

def download(mail, output):
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
            with open(output, "wb") as file:
                file.write(response_csv.content)
            print(" Newest CSV file successfully downloaded!")
        else:
            print("Error downloading the CSV file.")
    else:
        print("Login failed.")

def compare(tmpcsv, latestcsv):
    try:
        if filecmp.cmp(tmpcsv, latestcsv): 
            print("CSV doesn't changed since last pull. Ignoring")
            os.remove(tmpcsv)
        else:
            print("CSV has changed. Replacing old one")
            os.rename(tmpcsv, latestcsv)
    except FileNotFoundError:
        print(f"Asuming first pull since no old CSV was found.")
        os.rename(tmpcsv, latestcsv)

def wigle(api_token, latestcsv, onlypw):
    try:
        shutil.copyfile(latestcsv, "database.csv")  # keep original for future comparing for new entries in "compare"
    except FileNotFoundError:
        print(f"File '{latestcsv}' not found")
        return

    API_URL = 'https://api.wigle.net/api/v2/network/search'

    data = pandas.read_csv("database.csv", delimiter=',', encoding='unicode_escape')
    latitudes = []  # Create an empty list to store latitudes
    longitudes = []  # Create an empty list to store longitudes

    # Iterate over each row in the DataFrame
    for _, row in data.iterrows():
        # Decode HTML entities for the entire content of each field
        decoded_row = [html.unescape(str(field)) for field in row]

        # Check if onlypw is False or the entry has a password
        if not onlypw or decoded_row[4]:
            # Extract the BSSID value
            bssid = decoded_row[2]

            # Create the request URL for the WIGLE API
            print(f"Requesting geolocation for {bssid}")
            request_url = f"{API_URL}?netid={bssid}"

            # Send GET request to the WIGLE API
            headers = {'Authorization': f'Basic {api_token}'}
            response = requests.get(request_url, headers=headers)
            # Process the API response
            if response.status_code == 200:
                response_data = response.json()
                if 'results' in response_data and response_data['results']:
                    result = response_data['results'][0]
                    latitude = result['trilat']
                    longitude = result['trilong']
                    latitudes.append(latitude)  # Add latitude to the list
                    longitudes.append(longitude)  # Add longitude to the list
                else:
                    print(f"Result from Wigle was unvalid")
                    continue
                    
            elif response.status_code == 429:
                print(f"Statuscode was 429 Too many request - API Rate limited... Try again later)")
                return
            elif response.status_code == 401:
                print(f"Statuscode was 401 Unauthorized - Validate your API Key)")
            else:
                print(f"Statuscode was {response.status_code}")
                continue
            print(f"{decoded_row[2]} contained no password. Skipping due to onlypw = True")
        else:
            continue

    # Add latitude and longitude columns to the DataFrame
    data['Latitude'] = latitudes
    data['Longitude'] = longitudes

    # Save the updated DataFrame back to the CSV file
    data.to_csv("database.csv", index=False)
