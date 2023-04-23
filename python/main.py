###NOT WORKING RIGHT NOW###


import requests
import sys


#######Provide your Mail adress:######
mail = "example@mail.com"
######################################

cookieURL = "https://www.onlinehashcrack.com/dashboard"
csvURL = "https://www.onlinehashcrack.com/wpa-exportcsv"

#Get a valid PHPSESSID
payload = {
    "emailTasks": (mail),
    "submit": ""
}
response = requests.post(cookieURL, data=payload)
cookie = response.cookies.get('PHPSESSID')
csvpayload = {
    "PHPSESSID": (cookie)
}
print(csvpayload)

responsecsv = requests.post(csvURL, data= csvpayload)
print(responsecsv.text)

###NOT WORKING RIGHT NOW###