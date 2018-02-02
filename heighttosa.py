#******************************************************* 
# FILE: Height to Surface Area Relationship Finder
# AUTHOR: Thailynn Munroe
# EMAIL: tm0085@uah.edu
# MODIFIED BY: n/a
# ORGANIZATION: SERVIR 
# CREATION DATE: 01/13/18
# LAST MOD DATE: (Optional, add when modified)
# PURPOSE: To find the height to surface area of many bodies of water based on a given range of heights (bathtub fill)
# DEPENDENCIES: ArcGIS arcpy, export_to_csv, domainvalues
#********************************************************

import arcpy
from arcpy import env
arcpy.CheckOutExtension('Spatial')
from arcpy.sa import *
arcpy.env.overwriteOutput = True
arcpy.CheckOutExtension("Highways")
import csv
import os
import domainvalues
import numpy
import matplotlib.pyplot as plt

### Note: This could probably just be imported
def export_to_csv(dataset, output, dialect):
    """Output the data to a CSV file"""
    # create the output writer
    out_writer = csv.writer(open(output, 'wb'), dialect=dialect)
    # return the list of field names and field values
    header, rows = domainvalues.header_and_iterator(dataset)

    # write the field names and values to the csv file
    out_writer.writerow(map(domainvalues._encodeHeader, header))
    for row in rows:
        out_writer.writerow(map(domainvalues._encode, row))
###

DEM = '\\\\Mac\\Home\\Documents\\ArcGIS\\ESS508.gdb\\reservoirs_dem_lmb.tif'
dem = arcpy.Raster(DEM,meanCellHeight=30,meanCellWidth=30)
polygon = '\\\\Mac\\Home\\Documents\\ArcGIS\\ESS508.gdb\\reservoirs_buff.shp'
outTable = '\\\\Mac\\Home\\Documents\\Python_Scripts\\SA_height_tables\\'

for i in range(10,200,5):

    # Create a base name
    outName = outTable + 'table' + str(i)
    
    # Create a csv file
    outCSV = outName + '.csv'

    # Mask the elevation based on given height
    
    heightmask = Con(dem < i, 1)
    heightmask.save(outTable+'temp')

    # Count the number of pixels that were masked
    count = ZonalStatisticsAsTable(polygon,'Proj_Name',outTable + 'temp',outName,'NODATA','SUM')


    # Create a 'table view'
    fields= arcpy.ListFields(count)
    fieldinfo = arcpy.FieldInfo()
    arcpy.MakeTableView_management(count, outName + 'tv', "", "", fieldinfo)

    # Export the table to a csv
    open(outCSV, 'wb')
    export_to_csv(outName + 'tv', outCSV, 'excel')

# Create empty list for dam names
nameslist = []

# Fill in names of reservoirs from one of the CSVs
with open(outCSV, 'rb') as f:
    csvreader = csv.reader(f, delimiter=',')
    for row in csvreader:
        nameslist.append(row[1])

# Remove the table header
nameslist = [x for x in nameslist if x != 'PROJ_NAME']

## print(nameslist)

# Get a list of just the CSVs within the directory
filelist = os.listdir(outTable)
filelist = [x for x in filelist if x.endswith('.csv')]

## print(filelist)

# Create an empty dictionary
damdictionary = {}

# Loop through each reservoir to create a single dictionary entry with height and surface area values
for name in nameslist:
    x = []
    y = []
    # Loop through all the heights
    for i in range(10,200,5):
        # Make sure to check each file for values and the correct height
        for f in filelist:
            n = f[5:-4]
            if n == str(i):
                # Find the row in each file with the right reservoir
                with open(outTable+f, 'rb') as table:
                    csvreader2 = csv.reader(table, delimiter=',')
                    row = [row for row in csvreader2 if name in row]
                    try:
                        q = (int(float(row[0][5]))*900)
                        ## print(row[0][1])
                        if row[0][1] == name:

                            # Add the x,y values to the dictionary
                            y.append(q)
                            x.append(i)
                    except:
                        pass

                    
                    
    damdictionary[name] = [x,y]



#print(damdictionary)

# Create an empty dicitonary for the regression coefficients
damcoefficients = {}

for key, value in damdictionary.items():
        # Grab the values from the first dictionary
        x = value[0]
        y = value[1]
        if len(y) == len(x):

            # Perform a polynomial regression
            polyline = list(numpy.polyfit(x,y,3))
            polyline = [round(i,2) for i in polyline]
            #print(polyline)

            # Add coefficients to a new dictionary
            damcoefficients[key] = polyline

            # Leave room for mistakes
        else:
            print('Something is wrong here')
    
## print(damcoefficients)

longdict = {}
for key,value in damdictionary.items():
    if len(value[0]) > 5:
        longdict[key] = value


x = longdict['Huai Thom'][0]
y = longdict['Huai Thom'][1]

print(x,y)

plt.figure()
plt.plot(x,y)
plt.show()
