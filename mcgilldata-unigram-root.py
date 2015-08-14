import mcgilldata, string, os, sys, collections, csv

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
			if songTonic not in ChordTally:
				ChordTally[songTonic] = collections.Counter()	
			for theChord in theMeasure.chords:
				chordRoot = theChord.rootSD
				outputColumns.add(chordRoot)
				ChordTally[songTonic][chordRoot] += 1

#Output file writing: organize by song tonic/chord root
outputCsv = csv.writer(open('chordUnigrams.csv', 'wb'))
headerRow = list()
headerRow.append('Song Tonic')
headerRow.append('Chord Count')
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

for tonic in ChordTally:
	thisRow = list()
	thisRow.append(tonic)
	thisRow.append(sum(ChordTally[tonic].values()))
	for rootSD in sorted(outputColumns):
		thisRow.append(ChordTally[tonic][rootSD])
	outputCsv.writerow(thisRow)
		
	
	


