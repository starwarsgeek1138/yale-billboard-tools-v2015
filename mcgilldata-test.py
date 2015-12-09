import mcgilldata, string, os, sys, collections, pprint, csv

mcgillPath = 'mcgill-billboard'

theCorpus = mcgilldata.mcgillCorpus(mcgillPath, testMode = False)

theCorpus.findLicks()
outputList = theCorpus.listLicks()


w = csv.writer(open('ngrams-entropyByProgression.csv', 'w'))
for row in outputList:
    w.writerow(row)
    