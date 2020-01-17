import math
import csv
import os
import json
import requests
import heapq
import operator
import datetime
import arcpy
from arcpy import env
import multiprocessing
from multiprocessing import Pool

class Address:
    #Initializes the address instance
    def __init__(self, latitude, longitude, tract,county,state,population):
        self.latitude = latitude
        self.longitude = longitude
        self.tract = tract
        self.county = county
        self.state = state
        self.population = population
        
    #This adds the closest OTP by driving time
    def closest_otp(self,otp):
        self.otp_latitude = otp.latitude
        self.otp_longitude = otp.longitude
        self.otp_driving_duration = otp.driving_duration
        self.otp_driving_distance = otp.driving_distance      
        self.otp_county=otp.county
        self.otp_state=otp.state
        self.otp_address_name=otp.address_name
    
    

class OTP:
    def __init__(self, latitude, longitude, county,state, address_name):
        self.latitude = latitude
        self.longitude = longitude
        self.county = county
        self.state = state
        self.address_name = address_name
        
    def add_driving(self,driving_duration,driving_distance):
        self.driving_duration = driving_duration
        self.driving_distance = driving_distance


arcpy.CheckOutExtension("Network")
env.workspace = "C:\StreetMapPremium_NA2019_release3\FGDB\StreetMap_Data\NorthAmerica.gdb"
env.overwriteOutput = True
inNetworkDataset = "\Routing\Routing_ND"
outNALayerName = "times"
impedanceAttribute = "Minutes"
outODResultObject = arcpy.na.MakeODCostMatrixLayer(inNetworkDataset, outNALayerName, impedanceAttribute,
                        "720", "#", "Miles", "ALLOW_UTURNS", "","NO_HIERARCHY","#","NO_LINES")
outNALayer = outODResultObject.getOutput(0)
subLayerNames = arcpy.na.GetNAClassNames(outNALayer)
originsLayerName = subLayerNames["Origins"]
destinationsLayerName = subLayerNames["Destinations"] 
address_file = csv.DictReader(open(r'C:\\Users\\rkleinma\\Desktop\\Buprenorphine_01_2020\\origins_wo_pr.csv'), delimiter =",") 
OTP_file=csv.DictReader(open(r'C:\\Users\\rkleinma\\Desktop\\Buprenorphine_01_2020\\\destinations_wo_duplicates.csv'))







#Function distance uses the Haversine formula to calculate the Great Circle distance between two points
def distance (Lat_1, Lon_1, Lat_2, Lon_2):
	Lat_diff=math.sin((Lat_1-Lat_2)/2)
	Lon_diff=math.sin((Lon_1-Lon_2)/2)
	a = Lat_diff**2 + math.cos(Lat_1) * math.cos(Lat_2) * Lon_diff**2
	c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
	return 6378.1 * c #Distance in km

#This function takes an instance of Address and finds the ten closest instances of OTP or Pharmacy 
#within the list "points_to_test"
def closest_ten(center_of_pop, points_to_test):
    calculated_distance = []
    nearest_ten = []
    for j in range(0,len(points_to_test)):
        calculated_distance.append(distance(center_of_pop.latitude,center_of_pop.longitude, points_to_test[j].latitude, points_to_test[j].longitude))
    indices = zip(*heapq.nsmallest(10, enumerate(calculated_distance), key= operator.itemgetter(1)))[0]
    for j in range(0,len(indices)):
        nearest_ten.append(points_to_test[indices[j]])
    return nearest_ten

addresses = []
otp_list = []
all_records_OTP = []

for a in address_file:
    temp1 = Address(math.radians(float(a["LATITUDE"])), math.radians(float(a["LONGITUDE"])), (a["TRACTCE"]),a["COUNTYFP"],a["STATEFP"],a["POPULATION"])
    addresses.append(temp1)

for row2 in OTP_file:
    temp2 = OTP(math.radians(float(row2["LATITUDE"])), math.radians(float(row2["LONGITUDE"])),row2["COUNTY"],row2["STATE"],row2["ADDRESS"])
    otp_list.append(temp2)



upper_bound = 500
#print(len(addresses))
lower_bound = 0
#addresses = addresses[lower_bound:upper_bound]

def f(x):

    tableOrigins = arcpy.CreateFeatureclass_management("in_memory", "tempfc1", "POINT")
    arcpy.AddField_management(tableOrigins, "Name", "TEXT")
    arcpy.AddField_management(tableOrigins, "ObjectID", "TEXT")
    cursor = arcpy.da.InsertCursor(tableOrigins, ["Name","ObjectID", "SHAPE@XY"])
    cursor.insertRow(["Hello","1",(1,1),])
    del cursor

    coordinates_init_dest = [(0,0), 
                    (0, 0),
                    (0, 0),
                    (0, 0),
                    (0, 0),
                    (0, 0),
                    (0, 0),
                    (0, 0),
                    (0, 0),
                    (0, 0)]

    tableDestinations = arcpy.CreateFeatureclass_management("in_memory", "tempfc", "POINT")
    arcpy.AddField_management(tableDestinations , "Name", "TEXT")
    arcpy.AddField_management(tableDestinations , "DID", "TEXT")
    cursor = arcpy.da.InsertCursor(tableDestinations , ["Name","DID", "SHAPE@XY"])
    for i in range (0,len(coordinates_init_dest)):
        cursor.insertRow(["A","ID",coordinates_init_dest[i]])
    del cursor

    def origins(lat, lon):
        coordinates = [("1","Hello1", (math.degrees(lon), math.degrees(lat)),)]
        cursor = arcpy.da.UpdateCursor(tableOrigins, ["Name","ObjectID", "SHAPE@XY"])
        for row in cursor:
            row = ["0", "ID-0",(math.degrees(lon), math.degrees(lat)),]
            cursor.updateRow(row)
        del cursor
        return tableOrigins

    def destinations(dest_objects):
    #Take list of destinations and create coordinates list
        coordinates = []
        for x in range (0,len(dest_objects)):
            coordinates.append((math.degrees(dest_objects[x].longitude),math.degrees(dest_objects[x].latitude)))
       
        cursor = arcpy.da.UpdateCursor(tableDestinations , ["Name","DID", "SHAPE@XY"])
        j = 0
        for row in cursor:
            #print(str(j))
            row = [str(j), str(j),coordinates[j]]
            cursor.updateRow(row)
            j += 1
        del cursor
        return tableDestinations 





    def arc_time(origin1,destinations1, treatment_facility):
        if (treatment_facility == "otp"):
            inOrigins = origins(origin1.latitude, origin1.longitude)
            arcpy.na.AddLocations(outNALayer, originsLayerName, inOrigins, "", search_tolerance = "3 miles",
                                 append = "CLEAR",exclude_restricted_elements = "EXCLUDE" )
        
        inDestinations = destinations(destinations1)
        arcpy.na.AddLocations(outNALayer, destinationsLayerName, inDestinations,
                                 "",search_tolerance = "3 miles", append = "CLEAR",exclude_restricted_elements = "EXCLUDE", )
        field_names = arcpy.na.GetNAClassNames(outNALayer, nalocation_type = "LOCATION",)
        #Solve the OD layer
        try:
            arcpy.na.Solve(outNALayer)
        except(arcpy.ExecuteError):
            unsolved = OTP(0,0,"-1","-1","-1")
            unsolved.add_driving(-1,-1)
            origin1.closest_otp(unsolved)
            return origin1
        
        subLayers = dict((lyr.datasetName, lyr) for lyr in arcpy.mapping.ListLayers(outNALayer)[1:])
        LinesSubLayer = subLayers["ODLines"]
        cursor = arcpy.SearchCursor(LinesSubLayer)

       
        destination_index = 0
        total_meters = 0
        total_minutes= 0
        for row in cursor:
            destination_index = int(row.getValue("Name").split()[2])
            total_minutes = row.getValue("Total_Minutes")
            total_meters = (row.getValue("Total_Miles"))
            break    
        destinations1[destination_index].add_driving(total_minutes,total_meters)
        origin1.closest_otp(destinations1[destination_index]) #index changes between list and arcpy output

        return origin1

    otp_close_ten = closest_ten(x,otp_list)	
    
    x = arc_time(x,otp_close_ten, "otp")
    return x
    

if __name__ == '__main__':


    print ("start")
    print(str(datetime.datetime.now())) 
    #Find the nearest ten OTPs and Pharmacies by point-to-point distance
    #This also stores the distance from the current point of interest to all instances in the otp_list and pharmacy_list
    pool = Pool(processes=8)             
    t1 = datetime.datetime.now()
    a = pool.map(f, addresses)
    print(str(datetime.datetime.now()-t1))
    pool.terminate()
    addresses = a
    print ("ending")
    print(str(datetime.datetime.now()))



    #This file contains the main data output for analysis
    f= open('C:\\Users\\rkleinma\\Desktop\\Buprenorphine_01_2020\\bup_1_15_2020.csv', "wb+")
    writer = csv.writer(f)
    fheaders = ["TRACTCE", "COUNTYFP", "STATEFP", "MCOP_LAT","MCOP_LON", "POPULATION",
                "FACILITY_LAT", "FACILITY_LON", "FACILITY_ADDRESS",
                'FACILITY_DURATION','FACILITY_DRIVING_DISTANCE', "FACILITY_COUNTY", "FACILITY_STATE"]

    writer.writerow(fheaders)
    #print(len(addresses))
    #Time is in minutes
    #Distance is in miles
    for i in range(0,len(addresses)):
        b = [addresses[i].tract, addresses[i].county,addresses[i].state, math.degrees(addresses[i].latitude),math.degrees(addresses[i].longitude),addresses[i].population,
            math.degrees(addresses[i].otp_latitude), math.degrees(addresses[i].otp_longitude),
            addresses[i].otp_address_name,
            addresses[i].otp_driving_duration, addresses[i].otp_driving_distance, addresses[i].otp_county, addresses[i].otp_state,       
            ]
        writer.writerow(b)
 

