#!/usr/bin/env python
####################################################################
Filename            = 'rds_rdmp_data.py'# J1.2
# Written:          10-10-2014
# By:               Jason Thorne
# Description:      Information regarding the Research Data Management
# System is exported to .elm files on the server infplfs0XX (XX=04 to 10).
# This script runs on the server and performs three taSKs:
# import: read the eml files, parses the
# text to extract information, dumps the informatino in to an sqlite3
# database file.
# export:  uses the sqlite3 database to extract the information to CSV
# transfer: email the latest csv file to the email address in TOADDR
####################################################################
# updates: 
# JX.X|dd-mm-yyyy|who| Description
# J1.1|08-11-2014|JRT| Import the info table
# J1.2|11-11-2014|JRT| Renamed from mv csvFromElmLogger.py to
# rds_rdmp_data.py
# J1.3|18-11-2014|JRT| changed RDSlog to rds_log for the table name.
# also creating new file to accept the RDMP zID user info.
# J1.4|02-12-2014|JRT| fault tolerance and user stats
####################################################################
Version             = 'J1.4'
####################################################################
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
import rds_data, rdmp_lib_data, user_access

# export did include transfer, as we need to know the name of the 
# export file to transfer it. instead we just transfer the latest
# file, but there is more of a window for error doing it this way
THECOMMANDS     = ['importrdsinfo', 'importlibinfo', 'importuser', 'export',\
                'transfer', 'stats']
CMDIMPORT1      = 0
CMDIMPORT_LIB   = 1
CMDIMPORT_USR   = 2
CMDEXPORT       = 3
CMDTRANSFER     = 4
CMDSTATS        = 5



##########################################
if __name__ == "__main__":
    # get the command line argument
    if len(sys.argv) <= 1:
        print "Usage:>%s %s" %(Filename, str(THECOMMANDS))
        exit(1)
    # end if
    
    theCom = sys.argv[1:]
    
    if THECOMMANDS[CMDIMPORT1] in theCom:
        myCon      = sqlite3.connect(DBFILE)
        myCursor   = myCon.cursor()
    
        print 'Start Reading RDS log Files'
        try:
            for file in os.listdir(RDS_FOLDER):
                rds_data.runReport(file, myCursor)
                myCon.commit()
            print 'Reading Files Complete'
        except:
            ermsg = 'Some error occured DBFILE= %s RDS_FOLDER = %s' \
                    %(DBFILE, RDS_FOLDER)
            print ermsg
            msg    = MIMEText(ermsg)
            msg['subject']  = ermsg
            msg['From']     = FROMADDR
            msg['To']       = TOADDR

            s               = smtplib.SMTP('localhost')
            s.sendmail(FROMADDR, [TOADDR], msg.as_string())
            s.quit()
        # end try
        
        # now sum the statistics
        print "Recording RDS statistics"
        rds_data.recordStats(myCursor)
        myCon.commit()
        
        myCon.close()
    # end if
    
    if THECOMMANDS[CMDIMPORT_LIB] in theCom:
        myCon      = sqlite3.connect(DBFILE)
        myCursor   = myCon.cursor()
        
        print 'Start Reading RDMP Files' 
        try:
            # copy files to a temporary place where we can rename thme
            rdmp_lib_data.walktree(LIB_DATA_FOLDER,RDMP_FOLDER)
            # rename the files to the rdmp_X
            rdmp_lib_data.renameRDMP(RDMP_FOLDER)
            
            # Read all these xml files, and get the data from them
            rdmp_lib_data.extractFromRDMP(RDMP_FOLDER, myCursor)
            myCon.commit()
            
            print 'Import data from RDMP Files Complete'
        except:
            ermsg = 'line113: Something is wrong. Command %s did not work' %THECOMMANDS[CMDIMPORT_LIB]
            ermsg += ". Check RDMP_FOLDER = %s and LIB_DATA_FOLDER = %s." %(RDMP_FOLDER, LIB_DATA_FOLDER)
            print ermsg
            msg    = MIMEText(ermsg)
            msg['subject']  = ermsg
            msg['From']     = FROMADDR
            msg['To']       = TOADDR

            s               = smtplib.SMTP('localhost')
            s.sendmail(FROMADDR, [TOADDR], msg.as_string())
            s.quit()
        # end try
        myCon.close()
    # end info
    
    if THECOMMANDS[CMDIMPORT_USR] in theCom:
        myCon      = sqlite3.connect(DBFILE)
        myCursor   = myCon.cursor()
        user_access.populate_user_access_table(myCursor)
        myCon.commit()
        myCon.close()
    # end if
    
    
    if THECOMMANDS[CMDEXPORT] in theCom:
        # name the exported csv file with the date
        myNow           = datetime.datetime.now()
        myNowStr        = myNow.strftime("%Y%m%d%H%M%S")
        exportFile      = EXPORT_PREFIX + myNowStr + ".csv"

        # now use the command line for the sqlite3 export. I would prefer
        # to use the python interface, but I can't get the slqite mode
        # specific commands to execute
        # -e option causes a syntax error on my mac
        #osCom           = 'echo -e ".mode csv\n.header on\n.out ' + EXPORT_DIR + exportFile
        osCom           = 'echo ".mode csv\n.header on\n.out ' + EXPORT_DIR + exportFile
        osCom           += '\nselect * from %s;" | sqlite3 %s' %(RDS_STATS_TABLE, DBFILE)
        print osCom
        os.system(osCom)

    if THECOMMANDS[CMDTRANSFER] in theCom:
        exportFile      = None
        # and transfer the file by email
        # The file to transfer is the newst file preceded with rdslog_
        try:
            logFiles        = os.listdir(EXPORT_DIR)
        except:
            pass
        else:
            # find the newest log file
            logTime         = 0
            for i in logFiles:
                # exportprefix is at the beginning of log files
                if i.find(EXPORT_PREFIX) == 0:
                    # The position of the time in the filename
                    timpos  = len(EXPORT_PREFIX) + 1
                    thisLogTime = int(i[timpos:-4])
                    if thisLogTime > logTime:
                        exportFile = i
                        logTime = thisLogTime
                    # end if
                # end if
            # next i
        # end try

        if exportFile == None:
            msg             = MIMEText('The cron job was run, but no log file found in ' + EXPORT_DIR)
            msg['Subject']  = 'No log file found'
        else:
            fp              = open(EXPORT_DIR + exportFile, 'rb')
            # create a plain text message attachment
            msg             = MIMEText(fp.read())
            fp.close()
            lt              = str(logTime)
            niceTime        = lt[4:6] + '/' + lt[2:4] + '/20' + lt[:2]
            niceTime        += ' ' + lt[6:8] + ':' + lt[8:10] + ':' + lt[-2:]
            msg['Subject']  = 'RDS Report csv file made %s' %niceTime
        # end if
        msg['From']     = FROMADDR
        msg['To']       = TOADDR

        s               = smtplib.SMTP('localhost')
        s.sendmail(FROMADDR, [TOADDR], msg.as_string())
        s.quit()
    # endif
    
    if THECOMMANDS[CMDSTATS] in theCom:
        myCon      = sqlite3.connect(DBFILE)
        myCursor   = myCon.cursor()
        
        # get the statistics
        myToday = datetime.date.today()
        #myToday = datetime.date(year=2014, month=10, day=10)
        oneDay  = datetime.timedelta(days=1)
        # NOTE: The scripts run at 4am, so best to consider the logs from the ]
        # previous day.
        myToday         = myToday - oneDay
        
        myTomorrow      = myToday + oneDay
        myStats         = {}
        
        # initialise
        for k in SK:
            myStats[k]  = "Not available"
        # next k

        ####################
        # *1 Get the total storage today from rds_logs
        sqlCom      = "select total_space from %s " %RDS_STATS_TABLE
        sqlCom      += "where run_date == '%s';" %myToday.strftime('%Y-%m-%d')
        print "*1 Get the total storage today from rds_logs"
        print sqlCom
        myCursor.execute(sqlCom)
        myRec       = myCursor.fetchone()
        myStats[SK[StorageUsed]] = float(myRec[0] or 0)
        ####################
        # *2 what is the largest difference in storage between consecutive days over all time
        sqlCom      = "select max(space_lag)/%d from %s " %(TERABYTE, RDS_STATS_TABLE)
        
        print "*2 what is the largest difference in storage between consecutive days over all time"
        print sqlCom
        myCursor.execute(sqlCom)
        myRec       = myCursor.fetchone()
        myStats[SK[StorageDailyMax]] = float(myRec[0] or 0)
        
        ####################
        # *3 Previous 30 days storage (rdslogs space) 
        monthAgo    = myToday - ONEMONTH*oneDay
        
        print "*3 Previous 30 days storage (rdslogs space) "
        print sqlCom
        sqlCom      = "select sum(space_lag) from %s " %RDS_STATS_TABLE
        sqlCom      += "where run_date >= '%s' and run_date <= '%s'" %(monthAgo.strftime('%Y-%m-%d'), \
                            myToday.strftime('%Y-%m-%d'))
        #print sqlCom
        
        myCursor.execute(sqlCom)
        myRec       = myCursor.fetchone()
        myStats[SK[Storage30Days]] = float(myRec[0] or 0) / TERABYTE
        
        
        ####################
        # *4 Previous from 60 to 30 days
        twoMonthsAgo = monthAgo - ONEMONTH*oneDay
        
        print "*4 Previous from 60 to 30 days"
        print sqlCom
        sqlCom      = "select sum(space_lag) from %s " %RDS_STATS_TABLE
        sqlCom      += "where run_date >= '%s' and run_date <= '%s' order by run_date desc  limit 1;" \
                        %(twoMonthsAgo.strftime('%Y-%m-%d'), myToday.strftime('%Y-%m-%d'))
        #print sqlCom
        
        myCursor.execute(sqlCom)
        myRec       = myCursor.fetchone()
        myStats[SK[Storage60Days]] = float(myRec[0] or 0) / TERABYTE
        
        ####################
        # *5 The number of plans with allocated storage.  anything that exists in RDSLogs
        sqlCom      = "select count(distinct(plan)) from %s" %RDS_TABLE
        
        print "*5 The number of plans with allocated storage.  anything that exists in RDSLogs"
        print sqlCom
        
        myCursor.execute(sqlCom)
        myRec       = myCursor.fetchone()
        myStats[SK[RDMPStorage]] = int(myRec[0] or 0)
        
        ####################
        # *6 The number of plans with data, that is where the RDS logs space > 10MB
        sqlCom = 'select plan, max(space) from %s group by plan' %RDS_TABLE
        myCursor.execute(sqlCom)
        myRecs      = myCursor.fetchall()
        
        print "*6 The number of plans with data, that is where the RDS logs space > 10MB"
        print sqlCom
        
        myStats[SK[RDMPData]]  = 0
        for rec in myRecs:
            space = float(rec[1]) * TERABYTE / MEGABYTE
            myStats[SK[RDMPData]] +=  int(space > RDMP_MIN_DATA)
        # next rec
        
        
        ####################
        # 7* New in the last 30 days
        """
        sqlCom = 'select plan, min(run_date) from %s group by plan' %RDS_TABLE
        myCursor.execute(sqlCom)
        myRecs      = myCursor.fetchall()
        
        myStats[SK[newPlans30Days]] = 0
        
        for rec in myRecs:
            datePlanNew     = dateFromString(rec[1], '%Y-%m-%d %H:%M:%S', False)
            myStats[SK[newPlans30Days]] = int(datePlanNew <= monthAgo)
        # next rec
        """
        
        ####################
        # 8* Active in the last 30 days =>  the file count has changed in the last 30 days.
        sqlCom = 'select plan, number_of_files from %s ' %RDS_TABLE
        """
        sqlCom += 'where run_date > "%s" order by plan;' %monthAgo.strftime('%Y-%m-%d')
        #print sqlCom
        myCursor.execute(sqlCom)
        myRecs      = myCursor.fetchall()
        
        myStats[SK[activePlans30Days]] = 0
        
        nextPlan = False
        comPlan = None
        for rec in myRecs:
            plan = rec[0]
            noFiles = rec[1]
            
            if nextPlan:
                if comPlan == plan:
                    continue
                else:
                    nextPlan = False
            
            # order n squared, not too good
            for comRec in myRecs:
                comPlan = comRec[0]
                comNoFiles = comRec[1]
                if comPlan != plan:
                    break
                elif noFiles != comNoFiles:
                    myStats[SK[activePlans30Days]] += 1
                    nextPlan = True
                    break
        
        """
        #######################
        # 'UsersRDMP', UsersTotal', 'Users30Days'
        #sqlCom          = "select count(*) from %s" %USER_ACC_TABLE
        #print sqlCom
        #myCursor.execute(sqlCom)
        #myStats[SK[UsersRDMP]]       = myCursor.fetchone()[0]
        sqlCom          = "select count(*) from %s where first_access >= '%s'" \
                        %(USER_ACC_TABLE, (str(myToday.year) + '-01-01'))
        myCursor.execute(sqlCom)
        myStats[SK[UsersTotal]]       = myCursor.fetchone()[0]
        
        
        sqlCom = sqlCom          = "select count(*) from %s where last_access >= '%s' " \
                                    %(USER_ACC_TABLE, monthAgo.strftime('%Y-%m-%d'))
        #print sqlCom
        myCursor.execute(sqlCom)
        myStats[SK[Users30Days]]       = myCursor.fetchone()[0]
        
        myCon.close()
        
        ####################
        csvdata         = ''
        for k in SK:
            csvdata += ','.join((k, str(myStats[k]))) + '\n'
        print csvdata
            
        # create a plain text message attachment
        msg             = MIMEText(csvdata)
        msg['subject']  = "RDM statistics"
        msg['From']     = FROMADDR
        msg['To']       = TOADDR

        s               = smtplib.SMTP('localhost')
        s.sendmail(FROMADDR, [TOADDR], msg.as_string())
        s.quit()
        
        
    
 # end if __main__   
