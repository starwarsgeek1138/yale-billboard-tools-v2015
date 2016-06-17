import mcgilldata, string, os, sys, collections, pprint, csv

mcgillPath = 'mcgill-billboard'

theCorpus = mcgilldata.mcgillCorpus(mcgillPath, testMode = False)

theCorpus.findLicksNoKey()
outputList = theCorpus.listLicks()


w = csv.writer(open('ngrams-entropyByProgressionNoKeySimplest.csv', 'w'))
for row in outputList:
    w.writerow(row)
    