import mcgilldata, string, os, sys

os.chdir(os.path.dirname(sys.argv[0]))

mcgillPath = 'mcgill-billboard'

theCorpus = mcgilldata.mcgillCorpus(mcgillPath)

for theSongid, theSong in theCorpus.songs.iteritems():
    for thePhrase in theSong.phrases:
    	print thePhrase