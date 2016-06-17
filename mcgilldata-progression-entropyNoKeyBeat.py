import mcgilldata, string, os, sys, collections, pprint, csv

#This script will output a table of all progressions above a certain entropy treshold (set in mcgilldata.py), 
#including chord beat and form information. No tonic key context is used (progressions are all transposed to that C M/m = the first chord.)
#(This will derive the most common progressions (> 10 occurrences), with ending H > 0.9, given reduced chord names (no inversions).
  

mcgillPath = 'mcgill-billboard'

theCorpus = mcgilldata.mcgillCorpus(mcgillPath, testMode = True)

theCorpus.findLicksNoKey()
outputList = theCorpus.listLicks()

w = csv.writer(open('csv-results/ngrams-entropyByProgressionNoKey_Beat&Form.csv', 'w'))
for row in outputList:
    w.writerow(row)
    