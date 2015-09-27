import mcgilldata, string, os, sys, collections, csv, music21

mcgillPath = 'mcgill-billboard'

##This Code will find distribution of chord roots per tonic/mode of phrase in each song.
##Output is organized by tonic and by mode (major/minor/ambiguous)
##Chord roots are listed in mod12

theCorpus = mcgilldata.mcgillCorpus(mcgillPath)

ChordTally = dict() #Create dictionary of unigram distributions for all keys  
ChordTally['major'] = dict()
ChordTally['minor'] = dict()
ChordTally['ambiguous'] = dict()
outputColumns = set()

for theSongid, theSong in theCorpus.songs.iteritems():
	#build distribution dictionaries for major vs. minor phrases
	for thePhrase in theSong.phrases:
		mode = thePhrase.mode
		for theMeasure in thePhrase.measures:
			songTonic = theMeasure.tonic
			for theChord in theMeasure.chords:
				try: 
					chordRoot = music21.pitch.Pitch(theChord.rootSD).pitchClass
				except:
					pass #assume rootSD is an empty string
				quality = theChord.quality
				if songTonic not in ChordTally[mode]:
					ChordTally[mode][songTonic] = collections.Counter() 
				outputColumns.add(chordRoot)
				ChordTally[mode][songTonic][chordRoot] += 1
				
outputCsv = csv.writer(open('chordUnigrams-rootByMode.csv', 'wb'))
headerRow = list()
headerRow.append('Song Mode')
headerRow.append('Song Tonic')
headerRow.append('Chord Count')
for rootSD in sorted(outputColumns):
	headerRow.append(rootSD)
outputCsv.writerow(headerRow)

for mode in ChordTally:
	for tonic in ChordTally[mode]:
		thisRow = list()
		thisRow.append(mode)
		thisRow.append(tonic)
		thisRow.append(sum(ChordTally[mode][tonic].values()))
		for rootSD in range(12):
			try:	
				percent = ((ChordTally[mode][tonic][rootSD] * 1.0) / sum(ChordTally[mode][tonic].values())) * 100
			except: 
				percent = 0
			thisRow.append(percent)
		outputCsv.writerow(thisRow)