import mcgilldata, string, os, sys, collections, csv

mcgillPath = 'mcgill-billboard'

theCorpus = mcgilldata.mcgillCorpus(mcgillPath, testMode = True)

#determines given # of most common chords for all keys

majorChordTally = dict() #Create dictionary of unigram distributions for all keys  
outputColumns = collections.Counter()

for theSongid, theSong in theCorpus.songs.iteritems():
	
	for thePhrase in theSong.phrases:
		for theMeasure in thePhrase.measures:
			songTonic = theMeasure.tonic
			if songTonic not in ChordTally:
				ChordTally[songTonic] = collections.Counter()	
			for theChord in theMeasure.chords:
				chordRoot = theChord.rootSD
				quality = theChord.quality
				outputColumns[chordRoot + quality] += 1
				ChordTally[songTonic][chordRoot + quality] += 1
				
outputCsv = csv.writer(open('chordUnigrams-quality.csv', 'wb'))
headerRow = list()
headerRow.append('Song Tonic')
headerRow.append('Chord Count')
#Will output sorted list of most common (##) of chords (listed by quality)
for (chordType,count) in sorted(outputColumns.most_common(25)):
	headerRow.append(chordType)
outputCsv.writerow(headerRow)

for tonic in ChordTally:
	thisRow = list()
	thisRow.append(tonic)
	thisRow.append(sum(ChordTally[tonic].values()))
	for (chordType, count) in sorted(outputColumns.most_common(25)):
		percent = ((ChordTally[tonic][chordType] * 1.0) / sum(ChordTally[tonic].values())) * 100
		thisRow.append(percent)
	outputCsv.writerow(thisRow)

	


