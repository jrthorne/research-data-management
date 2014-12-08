ONEMONTH                = 30

# to allow searching of xml keys, the prefexis need to have reference in the namespaces
NAMESPACES              = {}
NAMESPACES['foxml']     = 'info:fedora/fedora-system:def/foxml#'
NAMESPACES['dc']        = "http://purl.org/dc/elements/1.1/"
NAMESPACES['ms21']      = "http://www.unsw.edu.au/lrs/ms21/ontology/"

# The keys we are looking for
KEYS                    = ['dc:subject' ,'dc:description','ms21:estimatedVolume',
'ms21:estimatedVolumeUnit','ms21:storageNamespace','ms21:storageStatus','ms21:status',
'ms21:dataStorageRequired','ms21:dataStorageAffiliation','ms21:dataStorageAffiliationSchool',
'ms21:hasAward']
EXTRATAGS               = ['pid:','status:', 'storageStatus:storageStatus:']

# the mapping of the keys to database values. If this is a list, the first element is the KEYS
# index, the second is the EXTRATAGS index
rdmp_id 				= [0,0]
dc_status				= [1,1]
dc_storage_status		= [1,2]
estimated_volume		= 2
storage_namespace		= 4
ms21_storage_status     = 5
ms21_status             = 6
data_storage_required   = 7
affiliation             = 8
school                  = 9
has_award               = 10
# used to get the estimated volume size in bytes
volume_unit             = 3

# to store the values found by recursively traversing the XML tree
VALUES                  = {}

#1 Kilobyte = 1,024 Bytes
#1 Megabyte = 1,048,576 Bytes
#1 Gigabyte = 1,073,741,824 Bytes
#1 Terabyte = 1,099,511,627,776 Bytes
# update. Store as gigabytes
KILOBYTE        = 9.5367e-7
MEGABYTE        = 9.7656e-4
GIGABYTE        = 1.0000
TERABYTE        = 1024.0

ZID_LOG_FILES     = ['http.1.log', 'http.2.log']
##### folders begin
# server
# ZID_LOG_FOLDER  = '/livearc/volatile/logs/'
# LIB_DATA_FOLDER  = '/livearc/volatile/logs/'
# RDMP_FOLDER      = '/home/nfs/z3007136_sa/rdmp_files/'
# EXPORT_DIR      = '/home/nfs/z3007136_sa/rdscsv/'
# RDS_FOLDER      = '/Data/maint/Reporting/prd/reports/'
# DBFILE          = '/home/nfs/z3007136_sa/db.sqlite3'

# local
ZID_LOG_FOLDER  = '/Volumes/daddy2/Users/jason/Documents/outsideWork/LTRDS/Data/LiveArcLogs/'
LIB_DATA_FOLDER = '/Volumes/daddy2/Users/jason/Documents/outsideWork/LTRDS/Data/rdmp/'
RDMP_FOLDER      = '/Volumes/daddy2/Users/jason/Documents/outsideWork/LTRDS/Output/rdmp_files/'
EXPORT_DIR       = '/Volumes/daddy2/Users/jason/Documents/outsideWork/LTRDS/Output/rdscsv/'
RDS_FOLDER       = '/Volumes/daddy2/Users/jason/Documents/outsideWork/LTRDS/Data/email/'
DBFILE          = "/Volumes/daddy2/Users/jason/public_html/LTRDS/db.sqlite3"
##### folders end

STATS_CSV       = 'stats.csv'
EXPORT_PREFIX    = 'rdslog_'
# J1.3, but not the prefix above
RDS_TABLE        = 'serverstatus_rds_log'
RDS_STATS_TABLE  = 'serverstatus_rds_stat'
RDMP_TABLE       = 'serverstatus_rdmp_info'
USER_ACC_TABLE   = 'serverstatus_user_access'
FROMADDR        = 'root@infplfs010.sc.it.unsw.edu.au'
TOADDR          = 'research.manager@unsw.edu.au'
#TOADDR          = 'j.thorne@unsw.edu.au'

# SK stands for statistics keys
SK              = ['RDMPCompleted', 'RDMPStorage', 'RDMPData', 'StorageUsed', \
                'Storage30Days', 'Storage60Days', 'StorageDailyMax', 'UsersRDMP', \
                'UsersTotal', 'Users30Days'] #, 'newPlans30Days', 'activePlans30Days']
# indexes for SK
RDMPCompleted   = 0 # Not Available Yet
RDMPStorage     = 1 #5
RDMPData        = 2 #6
StorageUsed     = 3 #1
Storage30Days   = 4 #3
Storage60Days   = 5 #4
StorageDailyMax = 6 #2
UsersRDMP       = 7 # Not Available Yet
UsersTotal      = 8 # Not Available Yet
Users30Days     = 9 # Not Available Yet
newPlans30Days  = 10 #7 Not in Shane's list
activePlans30Days = 11 #8 Not in Shane's list

RDMP_MIN_DATA   = 10.0

import time, datetime
##########################################
def dateFromString(dateString, format, useTime=False):
    strippedTime    = time.strptime(dateString, format)
    myTime            = time.mktime(strippedTime)
    if useTime:
        retVal        = datetime.datetime.fromtimestamp(myTime)
    else:
        retVal        = datetime.date.fromtimestamp(myTime)
    # end if
    
    return retVal
# end dateFromString
