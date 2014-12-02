from const import * 

import csv
import time
from time import strftime
from time import gmtime
import datetime
import os
from email.mime.text import MIMEText
import smtplib

##########################################
def populate_user_access_table(myCursor):
    zID_list=[]
    zid_time=[]
    zid_firsttime = []
    time3 = []
    
    # The log file to use is the one most recently modified.
    modTime = datetime.datetime(1970, 1, 1, 0, 0)
    logFileName = ZID_LOG_FOLDER + ZID_LOG_FILES[0]
    for file in ZID_LOG_FILES:
        try:
            print "%s last modified: %s" % (file, time.ctime(os.path.getmtime(ZID_LOG_FOLDER + file)))
            if datetime.datetime.fromtimestamp(os.path.getmtime(ZID_LOG_FOLDER + file)) > modTime:
                modTime = datetime.datetime.fromtimestamp(os.path.getmtime(ZID_LOG_FOLDER + file))
                logFileName = ZID_LOG_FOLDER + file
            # end if
        except: # if the file does not exist, send an email to alert, then return
            ermsg = 'An error occured reading ZID_LOG_FOLDER = %s' %(ZID_LOG_FOLDER + file)
            print ermsg
            msg    = MIMEText(ermsg)
            msg['subject']  = ermsg
            msg['From']     = FROMADDR
            msg['To']       = TOADDR

            s               = smtplib.SMTP('localhost')
            s.sendmail(FROMADDR, [TOADDR], msg.as_string())
            s.quit()
            return
    # next file
    
    print "Using %s" %logFileName
    
    logFile = open(logFileName, 'r')
    
    # start reading the logs from the maximum time recorded in the database.
    sqlCom = "select max(last_access) from %s;" %USER_ACC_TABLE
    myCursor.execute(sqlCom)
    # zid field is unique, so there should be at most one
    myRec           = myCursor.fetchone()
    print "Logs have been recorded up until %s" %myRec[0]
    
    try:
        log_recorded_upto = time.strptime(myRec[0],"%Y-%m-%d %H:%M:%S") 
    except:
        log_recorded_upto =  time.strptime("1970-01-01 00:00:00","%Y-%m-%d %H:%M:%S")
    # end try

    for line in logFile:
        # For each line find if there is a UNSW_RDS ID and add it to the list
        if "UNSW_RDS:z" in line:
            if "http:" in line:	
                time1 = line.split("http:")
                time2 = time1[1].split(":in")
                time2 = time2[0].split(":error")
                time3 = time2[0]
                try:
                    time4 = time.strptime(time3,"%d-%b-%Y %H:%M:%S.%f")
                except:
                    print "Oops! not a valid date", time3
                    continue
                # end try
            else:
                # if we can't get a time, don't record
                continue
                
            
            # Don't bother storing zIDs if we have already read them in
            if log_recorded_upto >= time4:
                continue
            # end if
            
            UserID = line.split("UNSW_RDS:z")[1]
            UserID_trimmed = UserID[:7]

            addUser =  UserID_trimmed not in zID_list
            if addUser:
                zID_list.append( UserID_trimmed)
            # end if
            # where is that user?
            i = zID_list.index(UserID_trimmed)
            
            #print UserID_trimmed
            
            #if we have added another unique user
            if addUser:
                zid_time.append(time4)
                zid_firsttime.append(time4)	
            else:
                if zid_time[i] < time4:
                    zid_time[i] = time4
                if zid_firsttime[i] > time4:
                    zid_firsttime[i] = time4
                
    # next line
    
    sqlFields = "zid, first_access, last_access"
     
    for j in range(len(zID_list)):
        # format for sqlite3 is yyyy-MM-dd HH:mm:ss
        first_access    = strftime("%Y-%m-%d %H:%M:%S", zid_firsttime[j]) 
        last_access     = strftime("%Y-%m-%d %H:%M:%S", zid_time[j])
        
        # is this zID in the database already
        sqlCom          = 'select last_access from %s where zid = ?' %USER_ACC_TABLE
        sqlValues       = (zID_list[j], )
        myCursor.execute(sqlCom, sqlValues)
        # zid field is unique, so there should be at most one
        myRec           = myCursor.fetchone()
        # if there is a record, and it's last access time is less than the one just 
        # obtained from the log file, replace it in the database.
        if myRec != None:
            try:
                if time.strptime(myRec[0],"%Y-%m-%d %H:%M:%S") < zid_time[j]:
                    sqlCom      = 'update %s set last_access = ? where zid = ?' %USER_ACC_TABLE
                    sqlValues   = (last_access, zID_list[j])
                    print sqlCom, sqlValues
                    myCursor.execute(sqlCom, sqlValues)  
                # end if
            except:
                print "An error occured with zID:%s", zID_list[j]
            # end try
        else:
            sqlCom          = 'insert into %s (%s) values (?,?,?)' % (USER_ACC_TABLE, sqlFields)
            sqlValues       = (zID_list[j], first_access, last_access)
            print sqlCom, sqlValues
            myCursor.execute(sqlCom, sqlValues)  
        # end if		
    # next j  
    
    
    
    print 'complete'
    return


