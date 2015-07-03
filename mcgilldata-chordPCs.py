import mcgilldata, string, os, sys, collections, csv

mcgillPath = 'mcgill-billboard'

theCorpus = mcgilldata.mcgillCorpus(mcgillPath, testMode = True)

ChordTally = collections.Counter() #Create dictionary of unigram distributions for all keys  

for theSongid, theSong in theCorpus.songs.iteritems():
	
	for thePhrase in theSong.phrases:
		for theMeasure in thePhrase.measures:
			for theChord in theMeasure.chords:
				chordRoot = theChord.rootPC
				ChordTally[chordRoot] += 1

for (chordRoot, count) in ChordTally.most_common():
	frequency = ((count * 1.0) / sum(ChordTally.values()))
	print '{:>4}: {:.1%} ({})'.format(chordRoot,frequency,count)	
	


