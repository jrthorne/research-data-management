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
                    a = removeTags(start,end,line)
                    #print f,     a
                    os.rename(folder+f, folder+a)
        else:
            os.remove(folder+f)

def unique (items):
    found = set([])
    keep = []
    
    for item in items:
        if item not in found:
            found.add(item)
            keep.append(item)
    return keep
                    
def extractFromRDMP(folder):
        zids = []
        csvFile = open('RDMP_zids.csv', 'w')
        writefile = csv.writer(csvFile)
        writefile.writerow(['zID'])
        for f in os.listdir(folder):
            rdmpFile = open(folder+f, 'r')
            for line in rdmpFile:
                #<dc:subject>pid: 
                if '<ms21:researchPlanManager>'    in line:
                    zid = removeTags('<ms21:researchPlanManager>','</ms21:researchPlanManager>',line)
                    zids = zids + [zid]
                    #<dc:subject>pid: 
                if '<ms21:reader>'    in line:
                    zid = removeTags('<ms21:reader>','</ms21:reader>',line)
                    zids = zids + [zid]
                #<dc:subject>pid: 
                if '<ms21:principalInvestigator>'    in line:
                    zid = removeTags('<ms21:principalInvestigator>','</ms21:principalInvestigator>',line)
                    zids = zids + [zid]
                #<dc:subject>pid: 
                if '<ms21:contributor>'    in line:
                    zid = removeTags('<ms21:contributor>','</ms21:contributor>',line)
                    #convertID(RDMPid)
                    zids = zids + [zid]
                zids = unique(zids)
                    
        print len(zids)
        #print zids
        for j in range(len(zids)):
            writefile.writerow(([zids[j]]))
        print "complete!"
        

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
#walktree(readFolder,writeFolder)
#renameRDMP(writeFolder)
extractFromRDMP(writeFolder)

    
    
    
    