import sys
import csv_api as csvapi
import os 
import time





###Provide your mail used for onlinehashcrack.com (Pwnagotchi Plugin)
mail = "user@example.com" 
######################################################################

# Get current directory
current_dir = os.getcwd()


csvapi.download(mail) # download the csv from onlinehashcrack.com while providing usermail
csvapi.compare("tmp.csv", "out.csv") #compare new with old csv to check for changes
