import os, sys
from stat import *
import shutil
import csv

def walktree(top, writeto):
    '''recursively descend the directory tree rooted at top,
       calling the callback function for each regular file'''

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
                    a = removeTags(start,end,line).replace(':', '_')
                    #print f,     a
                    os.rename(folder+f, folder+a)
                    
        else:
            os.remove(folder+f)
                    
def extractFromRDMP(folder):
        csvFile = open('RDMP_details.csv', 'w')
        writefile = csv.writer(csvFile)
        writefile.writerow(('<dc:subject>pid: ', 
                                                '<dc:description>status: ', 
                                                '<dc:description>storageStatus:storageStatus: ',
                                                '<ms21:estimatedVolume>',
                                                '<ms21:estimatedVolumeUnit>',
                                                '<ms21:storageNamespace>',
                                                '<ms21:storageStatus>',
                                                '<ms21:status>',
                                                '<ms21:dataStorageRequired>',
                                                '<ms21:dataStorageAffiliation>',
                                                '<ms21:dataStorageAffiliationSchool>'))
        for f in os.listdir(folder):
            rdmpFile = open(folder+f, 'r')
            hasAward = 'NO'
            for line in rdmpFile:
                #<dc:subject>pid: 
                if '<dc:subject>pid: '    in line:
                    RDMPid = removeTags('<dc:subject>pid: ','</dc:subject>',line)
                    convertID(RDMPid)
                #<dc:description>status: 
                start = '<dc:description>status: '
                end = '</dc:description>' 
                if start    in line:
                    RDMPstatus = removeTags(start,end,line)
                #<dc:description>storageStatus:storageStatus:
                start = '<dc:description>storageStatus:storageStatus: '
                end = '</dc:description>'
                if start    in line:
                    RDMPstoragestatus = removeTags(start,end,line)
                #<ms21:estimatedVolume>
                start = '<ms21:estimatedVolume>'
                end = '</ms21:estimatedVolume>'
                if start    in line:
                    RDMPvolume = removeTags(start,end,line)
                #<ms21:estimatedVolumeUnit>
                start = '<ms21:estimatedVolumeUnit>'
                end = '</ms21:estimatedVolumeUnit>'
                if start    in line:
                    RDMPvolumeUnit = removeTags(start,end,line)
                #<ms21:storageNamespace>
                start = '<ms21:storageNamespace>'
                end = '</ms21:storageNamespace>'
                if start    in line:
                    RDMPstoragenamespace = removeTags(start,end,line)
                #<ms21:storageStatus>
                start = '<ms21:storageStatus>'
                end = '</ms21:storageStatus>'
                if start    in line:
                    RDMPstorageStatus2 = removeTags(start,end,line)
                #<ms21:status>
                start = '<ms21:status>'
                end = '</ms21:status>'
                if start    in line:
                    RDMPstatus2 = removeTags(start,end,line)
                #<ms21:dataStorageRequired>
                start = '<ms21:dataStorageRequired>'
                end = '</ms21:dataStorageRequired>'
                if start    in line:
                    storageRequired = removeTags(start,end,line)
                # <ms21:dataStorageAffiliation>
                start = '<ms21:dataStorageAffiliation>'
                end = '</ms21:dataStorageAffiliation>'
                if start    in line:
                    dataStorageAffiliation = removeTags(start,end,line)
                #<ms21:dataStorageAffiliationSchool>
                start = '<ms21:dataStorageAffiliationSchool>'
                end = '</ms21:dataStorageAffiliationSchool>'
                if start    in line:
                    dataStorageAffiliationSchool = removeTags(start,end,line)
                #<ms21:dataStorageAffiliationSchool>
                start = '<ms21:hasAward'
                if start    in line:
                    hasAward = 'YES'
                
            writefile.writerow((RDMPid, hasAward, RDMPstoragestatus,RDMPvolume,RDMPvolumeUnit,RDMPstoragenamespace,RDMPstorageStatus2,RDMPstatus2,storageRequired,dataStorageAffiliation,dataStorageAffiliationSchool))

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
    RDMPID = 'D'+padding+numberID
    print RDMPID                
                    
                
def removeTags(start,end,line):
    a =  (line.split(start))[1].split(end)[0]
    return a

def removeTags2(start,end,line):
    if start    in line:
        a =  (line.split(start))[1].split(end)[0]
        return a
    else:
        return 'a'
        

readFolder = 'rdmp/'
writeFolder = 'rdmp_files/'
walktree(readFolder,writeFolder)
renameRDMP(writeFolder)
extractFromRDMP(writeFolder)

    
    
    
    