import sys, os, time
import csv_api as csvapi

##############################################################################################################
#Provide your mail used for onlinehashcrack.com (Pwnagotchi Plugin)                                         ##
mail = "mail@example.com"                                                                                   ##
#Wigle API Token (Sadly by default 10 requests/day)                                                         ##
api_token = ""                                                                                              ##
#Only lookup the geolocation of BSSIDs, that have a "password"-entry (Highly recommend)                     ##
onlypw = True # Only request geolocation of password is found in CSV (True/False)                           ##
##############################################################################################################


tmpcsv = "ohc-tmp.csv"
latestcsv = "ohc-latest.csv"


csvapi.download(mail, tmpcsv) # download the csv from onlinehashcrack.com while providing usermail
csvapi.compare(tmpcsv, latestcsv) #compare new with old csv to check for changes
csvapi.wigle(api_token, latestcsv, onlypw) # Ask Wigle.net API for geolocations of the BSSIDs collected in out.csv
