import multiprocessing
from multiprocessing import Pool, TimeoutError
import time
import os
import datetime
import arcpy
import csv
import numpy as np
from numpy import genfromtxt
import datetime
import random
import unidecode

arcpy.CheckOutExtension("Network")
arcpy.env.workspace="C:\\StreetMapPremium_NA2019_release3\\ClassicLocators"
arcpy.env.overwriteOutput = True

memory_table = arcpy.CreateTable_management("in_memory","tempfc2")




class Geo_address:
    def __init__(self, name, address, city, county, state, zip_code, longitude,latitude, match_status, match_score, match_type):
        try:
            self.name = unidecode.unidecode(name)
        except AttributeError:
            self.name = name
            
        try:
            self.address = unidecode.unidecode(address)
        except AttributeError:
            self.address = address

        try:
            self.city = unidecode.unidecode(city)
        except AttributeError:
            self.city = city

        try:
            self.county = unidecode.unidecode(county)
        except AttributeError:
            self.county = county

        self.state = state
        self.zip_code = zip_code
        self.latitude = latitude
        self.longitude = longitude
        self.match_status = match_status
        self.match_score = match_score
        self.match_type = match_type
        self.round = 0



def geocode(input_file, output_file, in_locator,field_mapping, round_num):
    
    tableOrigins = arcpy.CreateFeatureclass_management("in_memory","tempfc3")
    t = datetime.datetime.now()
    print("Flag0")
    print(input_file)
    print(in_locator)
    print(field_mapping)
    geocoded = arcpy.geocoding.GeocodeAddresses(input_file, in_locator, field_mapping, tableOrigins)
    print("Flage1")
    t1 = datetime.datetime.now()
    print(str(t1 - t))
    cursor = arcpy.SearchCursor(geocoded)
    
    field_names = [f.name for f in arcpy.ListFields(geocoded)]
    print(field_names)
    address_list = []
    address_list_temp = []
    index = 0
    cursor = arcpy.SearchCursor(geocoded)
    
    for row in cursor:
        index = index + 1
        if (in_locator == "USA_StreetAddress"):
            a = row.getValue("First")+" "+row.getValue("NAME")
        else:
            a = row.getValue("NAME")
        b = row.getValue("ADDRESS")
        c = row.getValue("CITY_1")
        
        e = row.getValue("STATE")
        f = row.getValue("ZIP")
        
        x = row.getValue("X")
        y= row.getValue("Y")
        g = row.getValue("Status")
        h= row.getValue("Score")
        i= row.getValue("Match_type")
        if in_locator == "USA_StreetAddress":
            if (str(g) == "M"):
                d = row.getValue("Subregion")
            elif (str(g) == "T") & (float(h) == 100):
                d = row.getValue("Subregion")
            else:
                d = row.getValue("COUNTY") 
        else:
            d = row.getValue("COUNTY")
        address = Geo_address(a,b,c,d,e,f,x,y,g,h,i)
        address_list_temp.append(address)
        
    recoding_address = []
    
    for i in range(0,len(address_list_temp)):
        if (str(address_list_temp[i].match_status) == "U") | (str(address_list_temp[i].match_status) == "M") & (float(address_list_temp[i].match_score) < 85) | (str(address_list_temp[i].match_status) == "T") & (float(address_list_temp[i].match_score) < 100):
            recoding_address.append(address_list_temp[i])
        else:
            address_list_temp[i].round = round_num
            address_list.append(address_list_temp[i])

    del cursor

    
    
    #Create CSV file
    f= open(output_file, "wb+")
    writer = csv.writer(f)
    fheaders = ["NAME","ADDRESS", "CITY", "STATE","ZIP","COUNTY", "MATCH_STATUS","MATCH_SCORE"]
    
    writer.writerow(fheaders)
    #print(len(recoding_address))
    for i in range(0,len(recoding_address)):
        b = [recoding_address[i].name, recoding_address[i].address, recoding_address[i].city, recoding_address[i].state,recoding_address[i].zip_code,recoding_address[i].county,recoding_address[i].match_status, recoding_address[i].match_score]
        

        writer.writerow(b)
    f.close()    
    return address_list





address_list_main = []
folder = "C:\\Users\\rkleinma\\Desktop\\Buprenorphine_01_2020\\"

#Geocoding round 1; StreetAddresses
output_file = "geocoded_1.csv"
output_name = folder +output_file
input_file = "buprenorphine_locations_wo_territories_reformatted_address.csv"
input_name = folder+input_file
in_locator = "USA_StreetAddress"
field_mapping = "Street ADDRESS;City CITY;State STATE;ZIP ZIP"
temp = geocode(input_name,output_name,in_locator, field_mapping,1)
address_list_main.append(temp)



#Geocoding round 2; ZIP5
input_file = output_file
input_name = folder+input_file
output_file = "geocoded_2.csv"
output_name = folder+output_file
in_locator = "USA_Postal" 
field_mapping = "ZIP ZIP"
temp = geocode(input_name,output_name,in_locator,field_mapping,2)
address_list_main.append(temp)


f = open(folder+"geocoded_output.csv", "wb+")
writer = csv.writer(f)
fheaders = ["ROW","NAME","ADDRESS", "CITY","COUNTY", "STATE","ZIP","LONGITUDE","LATITUDE","MATCH_STATUS","MATCH_SCORE","MATCH_TYPE","MATCH_ROUND"]

row_counter = 1

writer.writerow(fheaders)

for j in range(0,len(address_list_main)):
    for i in range(0,len(address_list_main[j])):
        address_list = address_list_main[j]
        b = [row_counter, address_list[i].name,address_list[i].address, address_list[i].city, address_list[i].county, address_list[i].state, address_list[i].zip_code,
        address_list[i].longitude, address_list[i].latitude, address_list[i].match_status, address_list[i].match_score, address_list[i].match_type, address_list[i].round]
        
        writer.writerow(b)
        row_counter = row_counter + 1
        
        
f.close()



