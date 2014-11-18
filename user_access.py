#!/usr/local/bin/pythonEPD

import csv
import time
import array
from time import strftime
from time import gmtime
import os
import numpy

readFolder = '/Users/jason/Documents/outsideWork/LTRDS/Data/LiveArcLogs/'
#readFolder = '/Volumes/Data/Users/z2231967/Dropbox/_UNSW_IT/PythonScripting/Logins/LiveArcLogs/'
#readFolder = '/Users/shane/Dropbox/IFTTT/PythonScripting/Logins/LiveArcLogs/'
#readFolder = '/Users/shane/Dropbox/_UNSW_IT/BusinessIntelligence/logs/'


#file = 'http.1.log'
#filename = readFolder + file
openFile = [] #= open(filename, 'r')
userListFile = open('UserList.csv','w')
writeUserList = csv.writer(userListFile)
zID_list=[]
zid_time=[]
zid_firsttime = []
time3 = []

def unique (items):
    found = set([])
    keep = []
    
    for item in items:
        if item not in found:
            found.add(item)
            keep.append(item)
    return keep

list = sorted(os.listdir(readFolder))
for file in list:
	if file.startswith("http."):
		openFile = open(readFolder+file, 'r')
		print file
    	for line in openFile:
    		# For each line find if there is a UNSW_RDS ID and add it to the list
        	if "UNSW_RDS:z" in line:
        		UserID = line.split("UNSW_RDS:z")[1]
        		UserID_trimmed = [UserID[:7]]
        		noOfUsers = len(zID_list)
        		zID_list = zID_list + UserID_trimmed
        		zID_list = unique (zID_list)
        		
        		#print len(zID_list), noOfUsers
        		if len(zID_list) > noOfUsers:
        			print len(zID_list)
        		# if the zID list is longer than the zID login time list, then add a row
        		#if len(zID_list) > len(zid_time):
        			#zid_firsttime.append(0)
        			#zid_time.append(0)
        		if "http:" in line:	
        			i = zID_list.index(UserID_trimmed[0])
        			time1 = line.split("http:")
        			time2 = time1[1].split(":in")
        			time2 = time2[0].split(":error")
        			time3 = time2[0]
        			try:
        				time4 = time.strptime(time3,"%d-%b-%Y %H:%M:%S.%f")
        				if len(zID_list) > len(zid_time):
        					zid_time.append(time4)
        					zid_firsttime.append(time4)	
        				else:
        					if zid_time[i] < time4:
        						zid_time[i] = time4
        					if zid_firsttime[i] > time4:
        						zid_firsttime[i] = time4
        			except:
        				print "Oops! not a valid date", time3
#print zid_time, 
#print zid_firsttime
for j in range(len(zID_list)):
	#writeUserList.writerow((zID_list[j],strftime("%d-%m-%Y %H:%M:%S", zid_time[j])))
	writeUserList.writerow((zID_list[j],strftime("%d-%m-%Y %H:%M:%S", zid_time[j]),strftime("%d-%m-%Y %H:%M:%S", zid_firsttime[j])))      		
        			
#print len(zid)
#print zid
#print zid_time
print 'complete'


