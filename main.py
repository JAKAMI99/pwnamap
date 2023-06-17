import csv_api
import map

##############################################################################################################
#Provide your mail used for onlinehashcrack.com (Pwnagotchi Plugin)                                         ##
mail = "CHANGEME"                                                                                           ##
#Wigle API Token (Sadly by default 10 requests/day)                                                         ##
api_token = "CHANGEME"                                                                                      ##
#Only lookup the geolocation of BSSIDs, that have a "password"-entry (Highly recommended)                   ##
onlypw = True #[True/False]                                                                                ##
##############################################################################################################








#Filenames
tmpcsv = "ohc-tmp.csv"
latestcsv = "ohc-latest.csv"
database = "database.csv"

csv_api.download(mail, tmpcsv) # download the csv from onlinehashcrack.com while providing usermail
csv_api.compare(tmpcsv, latestcsv) #compare new with old csv to check for changes
csv_api.wigle(api_token, latestcsv, database, onlypw) # Ask Wigle.net API for geolocations of the BSSIDs collected in out.csv

map.create(database)
