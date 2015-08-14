import mcgilldata, string, os, sys, collections, csv

mcgillPath = 'mcgill-billboard'

theCorpus = mcgilldata.mcgillCorpus(mcgillPath, testMode = True)

chordTally = dict() #Create dictionary of unigram distributions for diff beat strengths 
chordTally[3] = collections.Counter()  
chordTally[2] = collections.Counter()
chordTally[1] = collections.Counter()
outputColumns = set()

for theSongid, theSong in theCorpus.songs.iteritems():
	
	for thePhrase in theSong.phrases:
		for theMeasure in thePhrase.measures:
			songTonic = theMeasure.tonic
			for theChord in theMeasure.chords:
				beatStrength = theChord.beatStrength
				chordRoot = theChord.rootSD
				quality = theChord.quality
				outputColumns.add(chordRoot)
				if beatStrength == '':
					print theSongid
					print theMeasure
				else: 
					chordTally[beatStrength][chordRoot] += 1
outputCsv = csv.writer(open('chordUnigrams-rootByBeatStrength.csv', 'wb'))
headerRow = list()
headerRow.append('Beat Strength')
headerRow.append('Chord Count')
for rootSD in sorted(outputColumns):
	headerRow.append(rootSD)
outputCsv.writerow(headerRow)

for beatStrength in chordTally:
	thisRow = list()
	thisRow.append(beatStrength)
	thisRow.append(sum(chordTally[beatStrength].values()))
	for rootSD in sorted(outputColumns):
		percent = ((chordTally[beatStrength][rootSD] * 1.0) / sum(chordTally[beatStrength].values())) * 100
		thisRow.append(percent)
	outputCsv.writerow(thisRow)

