import subprocess
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

url = "https://www.onlinehashcrack.com/dashboard"
email = "example@email.com"

# configure Chrome WebDriver, to run in headless mode
chrome_options = Options()
chrome_options.add_argument("--headless")

# Run instance of headless chrome
driver = webdriver.Chrome(options=chrome_options)

# open url
driver.get(url)

# Wait until fully loaded (Highly WIP)
time.sleep(5)

# Search for the mail form an enter mail adress
email_input = driver.find_element(By.NAME, "emailTasks")
email_input.send_keys(email)

# Press enter to sent the requests
email_input.send_keys(Keys.RETURN)

# wait for successfull login
time.sleep(5)

# save the current PHPSESSID Cookie
cookies = driver.get_cookies()
phpsessid_cookie = None

for cookie in cookies:
    if cookie["name"] == "PHPSESSID":
        phpsessid_cookie = cookie["value"]
        break

if phpsessid_cookie:
    print("PHPSESSID Cookie:", phpsessid_cookie)
else:
    print("PHPSESSID-Cookie wurde nicht gefunden.")

# Kill browser instance
driver.quit()

# function to export the csv which holds all hashes
def download_csv(phpsessid_cookie):
    csv_url = "https://www.onlinehashcrack.com/wpa-exportcsv"
    output_file = "output.csv"

    # setup PHPSESSID cookie
    cookies = {"PHPSESSID": phpsessid_cookie}

    # Request the csv while providing the saved cookie
    response = requests.get(csv_url, cookies=cookies)
    with open(output_file, "wb") as f:
        f.write(response.content)

    print(f"CSV-Datei was created as {output_file} .")

# if cookie is present, call the download_csv function
if phpsessid_cookie:
    download_csv(phpsessid_cookie)
else:
    print("PHPSESSID-Cookie was not found.")
