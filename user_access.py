from const import * 

import csv
import time
import array
from time import strftime
from time import gmtime
import os

def unique (items):
    found = set([])
    keep = []
    
    for item in items:
        if item not in found:
            found.add(item)
            keep.append(item)
    return keep

def populate_user_access_table(myCursor):
    zID_list=[]
    zid_time=[]
    zid_firsttime = []
    time3 = []
    
    # The log file to use is the one most recently modified.
    modTime = 0
    logFileName = ZID_LOG_FOLDER + ZID_LOG_FILES[0]
    for file in ZID_LOG_FILES:
        print "last modified: %s" % time.ctime(os.path.getmtime(ZID_LOG_FOLDER + file))
        if time.ctime(os.path.getmtime(ZID_LOG_FOLDER + file)) > modTime:
            modTime = time.ctime(os.path.getmtime(ZID_LOG_FOLDER + file))
            logFileName = ZID_LOG_FOLDER + file
        # end if
    # next file
    
    logFile = open(logFileName, 'r')

    for line in logFile:
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
    
    sqlFields = "zid, first_access, last_access"
     
    for j in range(len(zID_list)):
        sqlCom = 'insert into %s (%s) values (?,?,?)' % (USER_ACC_TABLE, sqlFields)
        # format for sqlite3 is yyyy-MM-dd HH:mm:ss
        first_access = strftime("%Y-%m-%d %H:%M:%S", zid_time[j])
        last_access = strftime("%Y-%m-%d %H:%M:%S", zid_firsttime[j])
        sqlValues = (zID_list[j], first_access, last_access)
        myCursor.execute(sqlCom, sqlValues)    		
    # next j  
    
    print sqlCom, sqlValues
    
    print 'complete'


