import sqlite3
import sys
import time
import os
import datetime
import smtplib
from email.mime.text import MIMEText
import smtplib
import os, sys
from stat import *
import shutil
from xml.etree import ElementTree as ET

from const import *

##########################################
def runReport(file, myCursor):
    # only log files with .elm extension
    if file[0] == '.':
        print "ERROR - Not an eml file: %s" %file
        return
    # end if

    filename = RDS_FOLDER + file
    
    # How many times has this file been logged before?
    sqlCom = 'select count(*) from %s where import_file_name=?' %RDS_TABLE
    
    myCursor.execute(sqlCom, (file,))
    myRec = myCursor.fetchone()
    noTimesRecorded = int(myRec[0])
    
    # if more than 0 times, then don't log it again
    if noTimesRecorded > 0:
        #print "%s has been recorded %s times" %(filename, noTimesRecorded)
        return
    # end if 
    
    emlFile = open(filename, 'r')
    # the fields to insert
    sqlFields = "run_date, plan, cache, space, number_of_files, import_file_name"
    
    for line in emlFile:      
        if "RDS Storage Report Short run on " in line:
            theDate = line.replace("RDS Storage Report Short run on ","")
            theDate = theDate.strip("\r\n")
            theDate = theDate.replace("EST ", "")
        elif "RDS Storage Report -Long run on " in line:
            theDate = line.replace("RDS Storage Report -Long run on ","")
            theDate = theDate.strip("\r\n")
            theDate = theDate.replace("EST ", "")
        elif "DMP" in line:
            RDMP = line.strip('DMP # \r\n')
            cache = next(emlFile).strip('Cache used: ')
            cache = cache.strip("\r\n")
            spaceLine =  next(emlFile)
            space = spaceLine.strip('Space used: ')
            files = next(emlFile).strip('Number of Files: \r\n')
            space = space.replace(" ", "")
            space = space.strip()
            spaceNumber = float(space[:-1])
            spaceUnit = space[-1]
            spaceUnit = spaceUnit.strip()
            
            spaceUnit.splitlines()
            try:
                if spaceUnit == 'K':
                        spaceNumber = spaceNumber * KILOBYTE
                elif spaceUnit == 'M':
                        spaceNumber = float(spaceNumber) * MEGABYTE
                elif spaceUnit == 'T':
                        spaceNumber = float(spaceNumber) * TERABYTE
                elif spaceUnit == 'G':
                        spaceNumber = spaceNumber * GIGABYTE
                else:
                    spaceNumber = 0
            except:
                spaceNumber = 0
            
            run_date         = dateFromString(theDate,"%a %b %d %H:%M:%S %Y", True)
            sqlValues = (run_date, RDMP, cache, float(spaceNumber), int(files), file)
            
            sqlCom = 'insert into %s (%s) values (?,?,?,?,?,?)' % (RDS_TABLE, sqlFields)
            myCursor.execute(sqlCom, sqlValues)
        # end if search term in line
    # next line
    
    # print how many logs recorded for this file
    sqlCom = 'select count(*) from %s where import_file_name=?' %RDS_TABLE
    
    myCursor.execute(sqlCom, (filename,))
    myRec = myCursor.fetchone()
    noTimesRecorded = int(myRec[0])
    
        
    emlFile.close();
    return

##########################################
def recordStats(myCursor):
    # record statistics for each day from the last time this was done
    myToday     = datetime.date.today()
    oneDay      = datetime.timedelta(days=1)
    
    # when was this last run?
    sqlCom      = "select max(run_date) from %s;" %RDS_STATS_TABLE
    
    myCursor.execute(sqlCom)
    myRec       = myCursor.fetchone()
    lastDate    = myRec[0] or 0
    
    # if there is no data recorded, then go from the first day RDS logs were recorded
    if lastDate == 0:
        sqlCom      = "select min(run_date) from %s;" %RDS_TABLE
        myCursor.execute(sqlCom)
        myRec       = myCursor.fetchone()
        lastDate    = myRec[0] or 0
        # if the date is still zero, there are no stats to record
        if lastDate == 0:
            print "Nothing is in %s, so no stats to record" %RDS_TABLE
            return
        else:
            # we only want the date here, not the time
            lastDate = lastDate[:10]
            lastDate = dateFromString(lastDate, "%Y-%m-%d", False) - oneDay
        # end if
    else:
        # we only want the date here
        lastDate = dateFromString(lastDate, "%Y-%m-%d", False)
    # end if
    
    sqlFields   = "run_date, total_space, number_of_files, number_of_plans, "
    sqlFields   += "space_lag, files_lag, plans_lag"
    thisDay     = lastDate
    
    # sqlCondition limits the querie to data for thisDay
    sqlCondition = "where run_date < '%s' " %(thisDay+oneDay).strftime('%Y-%m-%d')
    sqlCondition += "and run_date > '%s';" %thisDay.strftime('%Y-%m-%d')
    sqlCom      = "select sum(space)/%f from %s " %(TERABYTE, RDS_TABLE)  + sqlCondition
           
    myCursor.execute(sqlCom)
    myRec       = myCursor.fetchone()
    lastStorage = float(myRec[0] or 0)
    
    sqlCom      = "select count(distinct(plan)) from %s " %RDS_TABLE + sqlCondition
    
    myCursor.execute(sqlCom)
    myRec       = myCursor.fetchone()
    lastPlans     = int(myRec[0] or 0)
    
    # get the total number of files for this day (sqlCondition)
    sqlCom      = "select sum(number_of_files) from %s " %RDS_TABLE + sqlCondition
    
    myCursor.execute(sqlCom)
    myRec       = myCursor.fetchone()
    lastFiles     = int(myRec[0] or 0)

    while thisDay <= myToday:
        thisDay += oneDay
        # sqlCondition limits the querie to data for thisDay
        sqlCondition = "where run_date < '%s' " %(thisDay+oneDay).strftime('%Y-%m-%d')
        sqlCondition += "and run_date > '%s';" %thisDay.strftime('%Y-%m-%d')
        sqlCom      = "select sum(space)/%f from %s " %(TERABYTE, RDS_TABLE)  + sqlCondition
               
        myCursor.execute(sqlCom)
        myRec       = myCursor.fetchone()
        totStorageToday = float(myRec[0] or 0)
        
        sqlCom      = "select count(distinct(plan)) from %s " %RDS_TABLE + sqlCondition
        
        myCursor.execute(sqlCom)
        myRec       = myCursor.fetchone()
        noPlans     = int(myRec[0] or 0)
        
        # get the total number of files for this day (sqlCondition)
        sqlCom      = "select sum(number_of_files) from %s " %RDS_TABLE + sqlCondition
        
        myCursor.execute(sqlCom)
        myRec       = myCursor.fetchone()
        noFiles     = int(myRec[0] or 0)
        
        # now insert the statistics for this day if there was anything recorded
        if noFiles or noPlans or totStorageToday:
            lagStorage  = (totStorageToday - lastStorage)*TERABYTE # back in Gigabytes
            lagFiles    = noFiles - lastFiles
            lagPlans    = noPlans - lastPlans
            sqlCom      = 'insert into %s (%s) values (?,?,?,?,?,?,?)' %(RDS_STATS_TABLE, sqlFields)
            sqlValues   = (thisDay, totStorageToday, noFiles, noPlans, lagStorage, lagFiles, lagPlans)
            myCursor.execute(sqlCom, sqlValues)
            lastStorage = totStorageToday
            lastFiles = noFiles
            lastPlans = noPlans
        # end if
    # end while
# end recordStats
