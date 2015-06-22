import mcgilldata, string

mcgillPath = 'mcgill-billboard'

theCorpus = mcgilldata.mcgillCorpus(mcgillPath)

for theSongid, theSong in theCorpus.songs.iteritems():
	for thePhrase in theSong.phrases:
			print thePhrase
	for theMeasure in theSong.measuresFlat:
			print theMeasure