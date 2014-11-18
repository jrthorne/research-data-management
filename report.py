#!/usr/local/bin/python

import csv
import time
import array
from time import strftime
from time import gmtime
from dateutil import parser
import os
import numpy
from numpy import genfromtxt
import datetime



def runReport(file,readfolder,writefolder):
    filename = readfolder + file
    emlFile = open(filename, 'r')
    for line in emlFile:
        if "RDS Storage Report Short run on " in line:
            #new1 = line.split("run on")
            theDate = line.replace("RDS Storage Report Short run on ","")
            theDate = theDate.strip("\r\n")
            theDate = theDate.replace("EST ", "")
            newDate = time.strptime(theDate,"%a %b %d %H:%M:%S %Y")
            fileDate = strftime("%Y%m%d%H%M%S", newDate)
            fname = writefolder + fileDate + '.csv'
            csvFile = open(fname, 'w')
            writefile = csv.writer(csvFile)
    
        if "DMP" in line:
            RDMP = line.strip('DMP # \r\n')
            cache = next(emlFile).strip('Cache used: ')
            cache = cache.strip("\r\n")
            space = next(emlFile).strip('Space used: ')
            files = next(emlFile).strip('Number of Files: \r\n')
            spaceLength = len(space)
            space.replace(" ", "")
            spaceNumber = float(space[:-3])
            spaceUnit = space[-3:-2]
            spaceUnit.strip(' ')
            spaceUnit.splitlines()
            if spaceUnit == 'K':
                    spaceNumber = spaceNumber / 1000000
            if spaceUnit == 'M':
                    spaceNumber = float(spaceNumber) / 1000
            if spaceUnit == 'T':
                    spaceNumber = float(spaceNumber) * 1000
            if spaceUnit == 'G':
                    spaceNumber = spaceNumber        
            writefile.writerow((RDMP, cache, spaceNumber, files))
                
    #print filename + ' complete'
    emlFile.close();
    csvFile.close();




def totalStorage(folder):
    print "Starting totalStorage"
    storageUsed = open('storageUsed.csv', 'w')
    writeStorageUsed = csv.writer(storageUsed)
    previousTotal = 0
    for file in os.listdir(folder):
        if file.endswith(".csv"):
            csvFile = open(folder+file, 'r')
            my_data = genfromtxt(csvFile, delimiter=',',usecols = (0,2))
            RDMPnumber = numpy.sort(my_data[:,0])
            b = numpy.diff(RDMPnumber)
            b = numpy.r_[1,b]
            RDMPs = len(RDMPnumber[b !=0])
            sumValue = numpy.sum(my_data[:,1])
            newUploadValue = sumValue - previousTotal
            previousTotal = sumValue
            dateName = file.strip('.csv')
            dateName = time.strptime(dateName,"%Y%m%d%H%M%S")
            date = strftime("%Y-%m-%d %H:%M", dateName)
            writeStorageUsed.writerow((date, sumValue/1000, newUploadValue/1000, RDMPs))
    storageUsed.close()
    print "Finishing totalStorage"


def RDMPstoreInfo(folder):
    print "Starting RDMPstoreInfo"
    RDMPstorageFile = open('RDMPstorageData.csv','w')
    writeRDMPstorage = csv.writer(RDMPstorageFile)
    RDMPnumber=[]
    RDMPstart=[]
    list = sorted(os.listdir(folder))
    for file in list:
        if file.endswith(".csv"):
            csvFile = open(folder+file, 'r')
            my_data = genfromtxt(csvFile, delimiter=',',usecols = (0,2))
            RDMPnumbers = numpy.sort(my_data[:,0])
            RDMPnumber = numpy.append(RDMPnumber,RDMPnumbers)
            RDMPnumber = numpy.unique(RDMPnumber)
    
    RDMPid=[]
    RDMPfileCount=n[0]*len(RDMPnumber) #mpy.zeros(shape=(len(RDMPnumber)))
    RDMPsize=[0]*len(RDMPnumber) #numpy.zeros(shape=(len(RDMPnumber)))
    RDMPlast =['']*len(RDMPnumber)
    #RDMPlast= numpy.zeros(shape=(len(RDMPnumber)),dtype = ('datetime64'))
    j = -1
    for ID in RDMPnumber:
        j=j+1
        string = "D%s%.0f" % ("0"*(7-len("%.0f" % (ID))),ID)
        RDMPid.append(RDMPid,string)
        print string
        for file in list:
            if file.endswith(".csv"):
                csvFile = open(folder+file, 'r')
                my_data = genfromtxt(csvFile, delimiter=',',usecols = (0,2,3))
                my_data_sort = numpy.sort(my_data[:,0])
                my_data_unique = numpy.unique(my_data_sort)
                if ID in my_data_unique:
                    startdate = file.strip('.csv')
                    dateName = time.strptime(startdate,"%Y%m%d%H%M%S")
                    date = strftime("%Y-%m-%d", dateName)
                    RDMPstart = numpy.append(RDMPstart,date)
                    #RDMPfileCount = numpy.append(RDMPfileCount,i)
                    break
        for file in list:
            if file.endswith(".csv"):
                csvFile = open(folder+file, 'r')
                my_data = genfromtxt(csvFile, delimiter=',',usecols = (0,2,3))
                my_data_sort = numpy.sort(my_data[:,0])
                my_data_unique = numpy.unique(my_data_sort)
                if ID in my_data_unique:
                    Rindex = numpy.where(my_data[:,0] == ID)
                    if  RDMPfileCount[j] != numpy.sum(my_data[Rindex,2]):
                        now = file.strip('.csv')
                        RDMPlast[j] = now        
                        
                    RDMPfileCount[j] = numpy.sum(my_data[Rindex,2])
                    RDMPsize[j] = numpy.sum(my_data[Rindex,1])
    writeRDMPstorage.writerow(RDMPid, RDMPstart, RDMPsize, RDMPfileCount, RDMPlast)
    
        
    print "Finishing RDMPstoreInfo"

            
readFolder = 'email/'
writeFolder = 'extracted/'

print 'Start Reading Files'
for file in os.listdir(readFolder):
    if file.endswith(".eml"):
        runReport(file,readFolder,writeFolder)
print 'Reading Files Complete'
totalStorage(writeFolder)
RDMPstoreInfo(writeFolder)

        
