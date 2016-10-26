import mcgilldata, string, os, sys, collections, csv, music21

mcgillPath = 'mcgill-billboard'

##This Code will find distribution of chord roots per tonic/mode of phrase in each song.
##Mode is determined by: 
##	1) Identifying tonic of each song 
##  2) Identifying normal form of each chord within a phrase *using external Rockpop-NSF list*
##  3) Identify if chord tones are b3, b6, and b7 in tonic key (add to a minor-key counter)
##  4) If the minor-key counter outweighs the counter for major key, codify phrase as minor


theCorpus = mcgilldata.mcgillCorpus(mcgillPath)

ChordTally = dict() #Create dictionary of unigram distributions for all keys  
ChordTally['major'] = dict()
ChordTally['minor'] = dict()
outputColumns = set()

for theSongid, theSong in theCorpus.songs.iteritems():
	
	#Determine if the phrase is major or minor based on appearance of b3, b6, b7 scale degrees in chords
	for thePhrase in theSong.phrases:
		minorScore = 0
		majorScore = 0
		for theMeasure in thePhrase.measures:
			for theChord in theMeasure.chords:
				try:  #turn chordRoot into a pitch object 
					chordRoot = music21.pitch.Pitch(theChord.rootSD).pitchClass
				except: #assume rootSD is empty
					pass 
				quality = theChord.qualityNormalForm #turn the quality of the chord into a normalForm	
				for theNote in quality: #find if the notes of the chord include b3, b6, b7 in the home tonic
					if (theNote + chordRoot) % 12 in [3,8,10]:
						minorScore += 1 #if b3, b6, b7 are present, add 1 to minorScore
					elif (theNote + chordRoot) % 12 in [9,10,11]:
						majorScore += 1 #if 6, b7, 7 are present, add 1 to majorScore
		if minorScore >= majorScore: #identify whether majorScore or minorScore prevails in phrase
			#if minorScore prevails, phrase encoded as minor, chords added to minor dictionary tally
			thePhrase.mode = 'minor'
		else:
			thePhrase.mode = 'major'
	
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
				
outputCsv = csv.writer(open('chordUnigrams-mode.csv', 'wb'))
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
		for rootSD in sorted(outputColumns):
			percent = ((ChordTally[mode][tonic][rootSD] * 1.0) / sum(ChordTally[mode][tonic].values())) * 100
			thisRow.append(percent)
		outputCsv.writerow(thisRow)