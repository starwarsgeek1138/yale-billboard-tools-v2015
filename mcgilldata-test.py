import mcgilldata, string, os, sys

mcgillPath = 'mcgill-billboard'

theCorpus = mcgilldata.mcgillCorpus(mcgillPath) #, testMode = True)

for theSongid, theSong in theCorpus.songs.iteritems():
    for thePhrase in theSong.phrases:
    	#print ">>> " + thePhrase.theLine, "    ", 
    	#print thePhrase
    	print ">>> " + thePhrase.theLine, "    ", 
    	for theMeasure in thePhrase.measures: 
    		print theMeasure.tonic
    		print theMeasure	
    		print theFolder