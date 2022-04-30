#!/usr/bin/env python3
#######################################################################
##                                                                   ##
## Script Name: KennaOwnerUpdate.py                                  ##
## Script Function: This script updates the owner information of     ##
##                  assets to KennaSecurity.                         ## 
##                                                                   ## 
## Script Version: 1.0                                               ##
## Script Writer: Shubham Tandlekar                                  ##
##                                                                   ##
#######################################################################


import requests
import csv
import os, sys
import time
from datetime import datetime
import json as simplejson
import pandas as pd
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import urllib3
from tqdm import tqdm
import colorama
import numpy as np

#ASCII Colors
Green = "\033[1;32;40m"
White = "\033[1;37;40m"
Red = "\033[1;41;40m" 

print("{}[+]{} Loading the Kenna Match File".format(Green, White))

#Accepting the first input argument as the KennaFile
kennaInputFileName = sys.argv[1]
kenna_df = pd.read_csv(kennaInputFileName,low_memory=False)
kenna_df["Current Owner"] = ""
kenna_df["Updated Owner"] = ""
kenna_df["Script DateStamp"] = ""

kenna_df["Current Owner"] = pd.Series(kenna_df["Current Owner"], dtype=np.dtype("O"))
kenna_df["Updated Owner"] = pd.Series(kenna_df["Updated Owner"], dtype=np.dtype("O"))
kenna_df["Script DateStamp"] = pd.Series(kenna_df["Script DateStamp"], dtype=np.dtype("O"))
kenna_df["ID"] = pd.Series(kenna_df["ID"], dtype=np.dtype('int64'))

kennaUpdated_df = pd.DataFrame(columns=kenna_df.columns)

#Kenna URL
KennaURL = "https://api.kennasecurity.com/assets/"

# HTTP Header
headers = {'Accept': 'application/json',
           'X-Risk-Token': 'Removed-Please-Change-This'
           }

print("{}[+]{} Requesting Sessions for Kenna".format(Green, White))

#Requesting the Session
session = requests.Session()

#SSL verification Off
session.verify = False
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


#Going over row by row on Kenna Match File
for Index, KennaRow in tqdm(kenna_df.iterrows(), total=kenna_df.shape[0], colour='green'):

    #Fetching ID, IPAddress and Owner information from the inputed Kenna File
    KennaAssetID = KennaRow["ID"]
    KennaRowIP = KennaRow["IP Address"]
    GraniteOwner = KennaRow["GraniteOwner"]
    
    #Making the request to search the asset based on the asset ID
    KennaRequest = requests.get("https://api.kennasecurity.com/assets/"+str(KennaAssetID), headers=headers, verify=False)
    JsonResponse = simplejson.loads(KennaRequest.content)
    
    #Sleeping for 1 sec before making a new request
    time.sleep(0.5)

    #print(JsonResponse)
    KennaCurrentOwner = JsonResponse["asset"]["owner"]
    KennaAPIIP = JsonResponse["asset"]["ip_address"]
	
	# Returns the current local date
    TimeStamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    
    #Adding Information to the respective Columns based on the API Response
    KennaRow["Updated Owner"] = KennaRow["GraniteOwner"]
    KennaRow["Current Owner"] = KennaCurrentOwner
    KennaRow["Script DateStamp"] = TimeStamp
    
    #Updating the DataFrame
    kennaUpdated_df = kennaUpdated_df.append(KennaRow)
    
    '''
    print("----------------")
    print("Kenna File IP: {}, Kenna API IP: {}".format(KennaRow, KennaAPIIP))
    print("Updated Owner: {}, Previous Kenna Owner - API: {}".format(KennaRow["Updated Owner"], KennaRow["Current Owner"]))
    print("TimeStamp: {}".format(KennaRow["Script DateStamp"]))
    print("----------------")
    '''
     
#kenna_df = kenna_df.drop_duplicates()
kennaUpdated_df.to_csv(kennaInputFileName+'_KennaOwnerUpdate.csv')
print("{}[+]{} File Created: {}".format(Green, White, kennaInputFileName+'_KennaOwnerUpdate.csv'))
