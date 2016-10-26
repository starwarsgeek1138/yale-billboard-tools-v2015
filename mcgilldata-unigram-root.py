import mcgilldata, string, os, sys, collections, csv, music21
##Code to find distribution of roots for all chords for all tonics within the McGill Corpus
##Output gives percentages and total counts per chord root for all tonics

mcgillPath = 'mcgill-billboard'

theCorpus = mcgilldata.mcgillCorpus(mcgillPath, testMode = True)

ChordTally = dict() #Create dictionary of unigram distributions for all tonics (by SD of chord root)
outputColumns = set()

for theSongid, theSong in theCorpus.songs.iteritems():
	
	for thePhrase in theSong.phrases:
		for theMeasure in thePhrase.measures:
			songTonic = theMeasure.tonic

			#determine song tonic for each measure: if the tonic exists, add chordRoot to dictionary, otherwise add tonic to dict		
			for theChord in theMeasure.chords:
				try: #turn chordRoot into pitch object
					chordRoot = music21.pitch.Pitch(theChord.rootSD).pitchClass
				except: #option for blank chordRoot
					pass
				outputColumns.add(chordRoot)
				if songTonic not in ChordTally:
					ChordTally[songTonic] = collections.Counter()
				ChordTally[songTonic][chordRoot] += 1

#Output file writing: organize by song tonic/chord root
outputCsv = csv.writer(open('csv-results/chordUnigrams-byRoot.csv', 'wb'))
headerRow = list()
headerRow.append('Song Tonic')
headerRow.append('Chord Count')
for chordRoot in sorted(outputColumns):
	headerRow.append(chordRoot)
outputCsv.writerow(headerRow)

for songTonic in ChordTally:
	thisRow = list()
	thisRow.append(songTonic)
	thisRow.append(sum(ChordTally[songTonic].values()))
	for chordRoot in range(12):
		try:	
			percent = ((ChordTally[songTonic][chordRoot] * 1.0) / sum(ChordTally[songTonic].values())) * 100
		except: 
			percent = 0
		thisRow.append(percent)
	outputCsv.writerow(thisRow)

for songTonic in ChordTally:
	thisRow = list()
	thisRow.append(songTonic)
	thisRow.append(sum(ChordTally[songTonic].values()))
	for chordRoot in range(12):
		try:	
			total = ChordTally[songTonic][chordRoot] * 1.0
		except: 
			total = 0
		thisRow.append(total)
	outputCsv.writerow(thisRow)
		
