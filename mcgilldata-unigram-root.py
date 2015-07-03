import mcgilldata, string, os, sys, collections, csv

mcgillPath = 'mcgill-billboard'

theCorpus = mcgilldata.mcgillCorpus(mcgillPath, testMode = True)

ChordTally = dict() #Create dictionary of unigram distributions for all keys  
outputColumns = set()

for theSongid, theSong in theCorpus.songs.iteritems():
	
	for thePhrase in theSong.phrases:
		for theMeasure in thePhrase.measures:
			songTonic = theMeasure.tonic
			if songTonic not in ChordTally:
				ChordTally[songTonic] = collections.Counter()	
			for theChord in theMeasure.chords:
				chordRoot = theChord.rootSD
				outputColumns.add(chordRoot)
				ChordTally[songTonic][chordRoot] += 1
outputCsv = csv.writer(open('chordUnigrams.csv', 'wb'))
headerRow = list()
headerRow.append('Song Tonic', 'Chord Count')
for rootSD in sorted(outputColumns):
	headerRow.append(rootSD)
outputCsv.writerow(headerRow)

for tonic in ChordTally:
	thisRow = list()
	thisRow.append(tonic)
	thisRow.append(sum(ChordTally[tonic].values()))
	for rootSD in sorted(outputColumns):
		percent = ((ChordTally[tonic][rootSD] * 1.0) / sum(ChordTally[tonic].values())) * 100
		thisRow.append(percent)
	outputCsv.writerow(thisRow)
	


