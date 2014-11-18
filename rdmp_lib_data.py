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
def walktree(top, writeto):
    '''recursively descend the directory tree rooted at top,
       calling the callback function for each regular file
       and copy the files where they can be renamed for convenience'''

    for f in os.listdir(top):
        pathname = os.path.join(top, f)
        mode = os.stat(pathname)[ST_MODE]
        if S_ISDIR(mode):
            # It's a directory, recurse into it
            walktree(pathname, writeto)
        elif S_ISREG(mode):
            # It's a file, call the callback function
            #callback(pathname)
            dst = os.path.join(writeto, f)
            #print dst
            shutil.copy2(pathname,dst)
                        
        else:
            # Unknown file type, print a message
            print 'Skipping %s' % pathname

def visitfile(file):
    print 'visiting', file
    #shutil.copy2(file,"rdmp/info1")

''' Rename the files that I copied to rdmp_files to have sensible names'''
def renameRDMP(folder):
    start = '<dc:subject>pid: '
    end = '</dc:subject>'
    for f in os.listdir(folder):
        if 'rdmp' in f:
            #print f
            rdmpFile = open(folder+f, 'r')
            for line in rdmpFile:
                if start in line:
                    #print line
                    # Don't have colons in the filename. Causes problems.
                    a = removeTags(start,end,line).replace(':', '_') + '.xml'
                    #print f,     a
                    os.rename(folder+f, folder+a)
        else:
            os.remove(folder+f)
            
def findelements(elem, level=0):
    #print "Finding Elements at level %d" %(level) 
    #print elem.tag
    
    i = 0
    if len(elem): # check all of elem's children
        for k in KEYS:
            values = elem.findall(k, NAMESPACES)
            i += 1
            #print "A", i
            for v in values:
                vk  = k
                i += 1
                print "B", i
                for et in EXTRATAGS:
                    if et in (v.text or ''):
                        vk = k + et
                        print "C", i
                        i += 1
                       
                VALUES[vk]       = v.text or ''
                #print "Finding Elements at level %d with value %s" %(level, VALUES[vk]) 
        
        for child in elem:
            findelements(child, level+1)
    
    return
# end findelements  

def extractFromRDMP(folder, myCursor):
        
        for f in os.listdir(folder):
            print "READING: " + folder+f
            # only read xml files
            if f[-4:] != ".xml":
                continue
  
            #parser = ET.XMLParser(encoding="utf-8")
            #tree = ET.fromstring(fp.read(), parser=parser)
            tree = ET.parse(folder+f)
            root = tree.getroot()
            findelements(root)
            
            # convert estimated volume to bytes
            RDMPvolume      = VALUES[KEYS[estimated_volume]] 
            RDMPvolumeUnit  = VALUES[KEYS[volume_unit]] 
            try:
                spaceUnit 	= RDMPvolumeUnit[0].upper()
            except IndexError:
                spaceUnit   = ''
                
            # is RDMP a number?
            if len(RDMPvolume) < 15:
            	try:
            		RDMPvolume = float(RDMPvolume)
            	except ValueError:
            		RDMPvolume = 0
            	# end try
            else:
            	RDMPvolume = 0
            	
            if spaceUnit == 'K':
                    volumeSpace = int(RDMPvolume * KILOBYTE)
            elif spaceUnit == 'M':
                    volumeSpace = int(RDMPvolume * MEGABYTE)
            elif spaceUnit == 'T':
                    volumeSpace = int(RDMPvolume * TERABYTE)
            elif spaceUnit == 'G':
                    volumeSpace = int(RDMPvolume * GIGABYTE)
            else:
                volumeSpace = 0
            storageRequired = VALUES[KEYS[data_storage_required]]
            if storageRequired == 'yes':
                boolStorageRequired = True
            elif storageRequired == 'no':
                boolStorageRequired = False
            else:
                boolStorageRequired = None
            
            try:
                boolHasAward = (VALUES[KEYS[has_award]].upper() == "YES")
            except KeyError:
                boolHasAward = False
                
            rdmpID           = convertID(VALUES[\
                                KEYS[rdmp_id[0]]+EXTRATAGS[rdmp_id[1]]])
            dcStorageStatus  = VALUES[\
                                KEYS[dc_storage_status[0]]+EXTRATAGS[dc_storage_status[1]]]
            
            
            """newLog            = Rdmp_info(rdmp_id   = rdmpID, 
                            dc_status               =  
                            dc_storage_status       = 
                            estimated_volume        = 
                            storage_namespace       = 
                            ms21_storage_status     = 
                            ms21_status             = 
                            data_storage_required   = 
                            affiliation             = 
                            school                  = 
                            has_award               = )
            newLog.save() """
            sqlFields = "rdmp_id, dc_status, dc_storage_status, estimated_volume, storage_namespace, "
            sqlFields += "ms21_storage_status, ms21_status, data_storage_required, "
            sqlFields += "affiliation, school, has_award"
            sqlCom = 'insert into %s (%s) values (?,?,?,?,?,?,?,?,?,?,?)' % (RDMP_TABLE, sqlFields)
            sqlValues = (rdmpID, 
                        VALUES[KEYS[dc_status[0]]+EXTRATAGS[dc_status[1]]],
                        dcStorageStatus[len('storageStatus:storageStatus: '):],
                        str(volumeSpace),
                        VALUES[KEYS[storage_namespace]],
                        VALUES[KEYS[ms21_storage_status]],
                        VALUES[KEYS[ms21_status]],
                        boolStorageRequired,
                        VALUES[KEYS[affiliation]],
                        VALUES[KEYS[school]],
                        boolHasAward)
            myCursor.execute(sqlCom, sqlValues)

# end  extractFromRDMP      

def convertID(rdmpID):
    numberID = rdmpID.strip('rdmp:')
    digits = len(numberID)
    padding = ''
    #print digits
    if digits == 1:
        padding = '000000'
    if digits == 2:
        padding = '00000'
    if digits == 3:
        padding = '0000'
    if digits == 4:
        padding = '000'
    retval = 'D'+padding+numberID
    return retval
                    
                
def removeTags(start,end,line):
    a =  (line.split(start))[1].split(end)[0]
    return a

def removeTags2(start,end,line):
    if start    in line:
        a =  (line.split(start))[1].split(end)[0]
        return a
    else:
        return 'a'