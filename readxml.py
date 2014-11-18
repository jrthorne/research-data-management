#!/Volumes/daddy2/Users/jason/.virtualenvs/rds/bin/python
from xml.etree import ElementTree
# to allow searching of xml keys, the prefexis need to have reference in the namespaces
NAMESPACES              = {}
NAMESPACES['foxml']     = 'info:fedora/fedora-system:def/foxml#'
NAMESPACES['dc']        = "http://purl.org/dc/elements/1.1/"
NAMESPACES['ms21']      = "http://www.unsw.edu.au/lrs/ms21/ontology/"

# The keys we are looking for
KEYS                    = ['dc:subject' ,'ms21:hasAward','dc:description','ms21:estimatedVolume',
'ms21:estimatedVolumeUnit','ms21:storageNamespace','ms21:storageStatus','ms21:status',
'ms21:dataStorageRequired','ms21:dataStorageAffiliation','ms21:dataStorageAffiliationSchool']

# First parameter is the index in KEYS to which the tag relates, second is the tag
EXTRATAGS               = ['pid:','status:', 'storageStatus:storageStatus:']

"""
'dc:subject'pid: ,'dc:description'status: ,'dc:description'storageStatus:storageStatus: ,'ms21:estimatedVolume','ms21:estimatedVolumeUnit','ms21:storageNamespace','ms21:storageStatus','ms21:status','ms21:dataStorageRequired','ms21:dataStorageAffiliation','ms21:dataStorageAffiliationSchool'
"""
# to store the values found by recursively traversing the XML tree
VALUES                  = {}



def findelements(elem, level=0):
    if len(elem): # check all of elem's children
        for k in KEYS:
            values = elem.findall(k, NAMESPACES)
            for v in values:
                for et in EXTRATAGS:
                    if et in (v.text or ''):
                        k = k + et
                VALUES[k]       = v.text or ''
                
        for child in elem:
            findelements(child, level+1)
    
    return
# end findelements


root = ElementTree.parse('rdmp_files/rdmp_5').getroot()
findelements(root)

for k in VALUES.keys():
    print "Key -%s- %s" %(k, VALUES[k])

