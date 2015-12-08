import mcgilldata, string, os, sys

mcgillPath = 'mcgill-billboard'

theCorpus = mcgilldata.mcgillCorpus(mcgillPath, testMode = False)

for theSongid, theSong in theCorpus.songs.iteritems():
    for thePhrase in theSong.phrases:
        print ">>> " + thePhrase.theLine, "    ", 
        print thePhrase
        print 'Phrase Length: ' + str(thePhrase.measureLength)
        print thePhrase.formLetter 
        print thePhrase.formFunction
        
        