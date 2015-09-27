import mcgilldata, string, os, sys, collections, csv, music21

mcgillPath = 'mcgill-billboard'

#Determines distribution of chords (all tonics) by strength of beat position (metrical strength)
##Prints total # of chords organized by beat position and chordRoot (in mod12 SD)

theCorpus = mcgilldata.mcgillCorpus(mcgillPath, testMode = False)

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
				try:  #turn chordRoot into a pitch object 
					chordRoot = music21.pitch.Pitch(theChord.rootSD).pitchClass
				except: #assume rootSD is empty
					pass 
				beatStrength = theChord.beatStrength
				quality = theChord.quality
				outputColumns.add(chordRoot)
				if beatStrength == '':
					pass
				else: 
					chordTally[beatStrength][chordRoot] += 1
					
outputCsv = csv.writer(open('chordUnigrams-rootByBeatStrength.csv', 'wb'))
headerRow = list()
headerRow.append('Beat Strength')
headerRow.append('Chord Count')
for chordRoot in sorted(outputColumns):
	headerRow.append(chordRoot)
outputCsv.writerow(headerRow)

for beatStrength in chordTally:
	thisRow = list()
	thisRow.append(beatStrength)
	thisRow.append(sum(chordTally[beatStrength].values()))
	for chordRoot in range(12):
		try:    
			total = chordTally[beatStrength][chordRoot] * 1.0
		except: 
			total = 0
		thisRow.append(total)
	outputCsv.writerow(thisRow)