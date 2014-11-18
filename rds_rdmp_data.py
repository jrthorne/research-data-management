#!/usr/bin/env python
####################################################################
Filename            = 'rds_rdmp_data.py'# J1.2
# Written:          10-10-2014
# By:               Jason Thorne
# Description:      Information regarding the Research Data Management
# System is exported to .elm files on the server infplfs0XX (XX=04 to 10).
# This script runs on the server and performs three tasks:
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
####################################################################
Version             = 'J1.3'
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
from rds_data import *
from rdmp_lib_data import *
from user_access import *

# export did include transfer, as we need to know the name of the 
# export file to transfer it. instead we just transfer the latest
# file, but there is more of a window for error doing it this way
THECOMMANDS     = ['importinfo1', 'importlibinfo', 'importuser', 'export', 'transfer']
CMDIMPORT1      = 0
CMDIMPORT_LIB   = 1
CMDIMPORT_USR    = 2
CMDEXPORT       = 3
CMDTRANSFER     = 4



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
    
        print 'Start Reading Files'
        for file in os.listdir(RDS_FOLDER):
            runReport(file, myCursor)
            myCon.commit()
        print 'Reading Files Complete'
        
        myCon.close()
    # end if
    
    if THECOMMANDS[CMDIMPORT_LIB] in theCom:
    
        print 'Start Reading RDMP Files' 
        # copy files to a temporary place where we can rename thme
        walktree(LIB_DATA_FOLDER,RDMP_FOLDER)
        # rename the files to the rdmp_X
        renameRDMP(RDMP_FOLDER)
        
        myCon      = sqlite3.connect(DBFILE)
        myCursor   = myCon.cursor()
    
        # Read all these xml files, and get the data from them
        extractFromRDMP(RDMP_FOLDER, myCursor)
        myCon.commit()
        myCon.close()
        print 'Import data from RDMP Files Complete'
    # end info
    
    if THECOMMANDS[CMDIMPORT_USR] in theCom:
        pass
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
        osCom           += '\nselect * from %s;" | sqlite3 %s' %(RDS_TABLE, DBFILE)
        print osCom
        os.system(osCom)

    if THECOMMANDS[CMDTRANSFER] in theCom:
        # and transfer the file by email
        me              = FROMADDR
        you             = TOADDR

        # The file to transfer is the newst file preceded with rdslog_
        logFiles        = os.listdir(EXPORT_DIR)
        # find the newest log file
        exportFile      = None
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

        if exportFile == None:
            msg             = MIMEText('The cron job was run, but no log file found')
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
        msg['From']     = me
        msg['To']       = you

        s               = smtplib.SMTP('localhost')
        s.sendmail(me, [you], msg.as_string())
        s.quit()
    # endif
    
 # end if __main__   
