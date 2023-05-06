import subprocess
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

# Installieren Sie die erforderlichen Abhängigkeiten
subprocess.run(["pip", "install", "selenium"])
subprocess.run(["pip", "install", "requests"])

url = "https://www.onlinehashcrack.com/dashboard"
email = "example@email.com"

# Konfigurieren Sie den Chrome WebDriver, um headless ausgeführt zu werden
chrome_options = Options()
chrome_options.add_argument("--headless")

# Erstellen Sie eine Instanz des Browsers (Chrome in diesem Beispiel) mit den headless-Optionen
driver = webdriver.Chrome(options=chrome_options)

# Öffnen Sie die URL im Browser
driver.get(url)

# Warten Sie, bis die Seite vollständig geladen ist
time.sleep(5)

# Suchen Sie das E-Mail-Eingabefeld und geben Sie die E-Mail-Adresse ein
email_input = driver.find_element(By.NAME, "emailTasks")
email_input.send_keys(email)

# Senden Sie das Formular, indem Sie Enter drücken
email_input.send_keys(Keys.RETURN)

# Warten Sie, bis die Anmeldung abgeschlossen ist
time.sleep(5)

# Holen Sie sich den PHPSESSID-Cookie
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

# Schließen Sie den Browser
driver.quit()

# Funktion zum Herunterladen der CSV-Datei
def download_csv(phpsessid_cookie):
    csv_url = "https://www.onlinehashcrack.com/wpa-exportcsv"
    output_file = "output.csv"

    # Setzen Sie den PHPSESSID-Cookie für die Anfrage
    cookies = {"PHPSESSID": phpsessid_cookie}

    # Führen Sie die Anfrage aus und speichern Sie die Antwort als CSV-Datei
    response = requests.get(csv_url, cookies=cookies)
    with open(output_file, "wb") as f:
        f.write(response.content)

    print(f"CSV-Datei wurde erfolgreich als {output_file} gespeichert.")

# Verwenden Sie die Funktion, um die CSV-Datei herunterzuladen
if phpsessid_cookie:
    download_csv(phpsessid_cookie)
else:
    print("PHPSESSID-Cookie wurde nicht gefunden.")
