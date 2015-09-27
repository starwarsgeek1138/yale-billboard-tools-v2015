import mcgilldata, string, os, sys, collections, csv

#This code gives the most common chord for each root-type
#Chords are organized by chordRoot

mcgillPath = 'mcgill-billboard'

theCorpus = mcgilldata.mcgillCorpus(mcgillPath, testMode = True)

ChordTally = collections.Counter() #Create dictionary of unigram distributions for all keys  

for theSongid, theSong in theCorpus.songs.iteritems():
	
	for thePhrase in theSong.phrases:
		for theMeasure in thePhrase.measures:
			for theChord in theMeasure.chords:
				chordRoot = theChord.rootPC
				ChordTally[chordRoot] += 1
				#create chord tally for specific root

for (chordRoot, count) in ChordTally.most_common():
	frequency = ((count * 1.0) / sum(ChordTally.values()))
	#determines frequency for a specific chordRoot
	print '{:>4}: {:.1%} ({})'.format(chordRoot,frequency,count)	
	#prints most common chords for specific root, based on given parameters 


