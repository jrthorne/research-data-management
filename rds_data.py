import sqlite3
import sys
import time
import os
import datetime
import smtplib
from email.mime.text import MIMEText
import os, sys
from stat import *
import shutil
from xml.etree import ElementTree as ET

from const import *

##########################################
def dateFromString(dateString, format, useTime):
    strippedTime    = time.strptime(dateString, format)
    myTime            = time.mktime(strippedTime)
    if useTime:
        retVal        = datetime.datetime.fromtimestamp(myTime)
    else:
        retVal        = datetime.date.fromtimestamp(myTime)
    # end if
    
    return retVal
# end dateFromString

##########################################
def runReport(file, myCursor):
    # only log files with .elm extension
    if file[-4:] != '.eml':
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
    print "processing %s" %filename
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
            space = next(emlFile).strip('Space used: ')
            files = next(emlFile).strip('Number of Files: \r\n')
            spaceLength = len(space)
            space.replace(" ", "")
            spaceNumber = float(space[:-3])
            spaceUnit = space[-2:-1]
            spaceUnit.strip(' ')
            
            spaceUnit.splitlines()
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
            
            run_date         = dateFromString(theDate,"%a %b %d %H:%M:%S %Y", True)
            sqlValues = (run_date, RDMP, cache, str(int(spaceNumber)), int(files), file)
            
            sqlCom = 'insert into %s (%s) values (?,?,?,?,?,?)' % (RDS_TABLE, sqlFields)
            myCursor.execute(sqlCom, sqlValues)
        # end if search term in line
    # next line
    
    # print how many logs recorded for this file
    sqlCom = 'select count(*) from %s where import_file_name=?' %RDS_TABLE
    
    myCursor.execute(sqlCom, (filename,))
    myRec = myCursor.fetchone()
    noTimesRecorded = int(myRec[0])
    
    print "%d logs were recorded for %s" %(noTimesRecorded, filename)
        
    emlFile.close();
    return
