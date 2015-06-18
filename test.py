import mcgilldata, string

mcgillPath = 'mcgill-billboard'

theCorpus = mcgilldata.mcgillCorpus(mcgillPath)

for theSongid, theSong in theCorpus.songs.iteritems():
	for theMeasure in theSong.measuresFlat:
			print theMeasure
						