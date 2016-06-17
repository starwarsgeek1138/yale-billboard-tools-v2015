import mcgilldata, string, os, sys, collections, pprint, csv

#This code will list the most common n-grams (>10 occurrences), with reduced chord names, and no key or beat information. 
#Ngrams are listed by n-length (ascending order) and # of occurrences (descending order).

mcgillPath = 'mcgill-billboard'

pitchClassTranslate = {
	'C' : 0,
	'B#' : 0,
	'C#' : 1,
	'D-' : 1,
	'D' : 2,
	'E--': 2,
	'D#' : 3,
	'E-' : 3,
	'E' : 4,
	'F-' : 4,
	'E#' : 5, 
	'F' : 5,
	'F#' : 6,
	'G-' : 6,
	'F##' : 7,
	'G' : 7,
	'A--': 7,
	'G#' : 8,
	'A-' : 8,
	'A' : 9,
	'B--' : 9,
	'A#' : 10,
	'B-' : 10,
	'B' : 11,
	'C-' : 11 }

def transToC(ngram):
	transposedNgram = list()
	def chordSplit(chord):
		n = chord.rfind('-')
		p = chord.rfind('#')
		if n == -1 and p == -1:
			y = 2	  ##INCLUDES CHORD FORM AND BEAT AS 1st/2nd CHARACTER INFO - y=1 if no beat info included
		else:
			y = max(n,p)
		chordRoot = chord[2:y+1] ##INCLUDES CHORD BEAT/Form - [0:y+1] if no beat info included
		chordQuality = chord[y+1:]
		#chordForm = chord[0]
		#chordBeat = chord[1] ##COMMENT OUT IF NO BEAT INFO INCLUDED IN CHORD SYMBOL
		return (chordRoot, chordQuality)
	first = True
	for chord in ngram:
		if chord == '>S' or chord == '>E' or chord[0] == ' ':
			newChord = chord
		else:
			chordParts = chordSplit(chord) 
			if first:
				firstChordRoot = chordParts[0]
				transInterval = pitchClassTranslate[firstChordRoot]
				first = False
			newRoot = pitchClassTranslate[chordParts[0]] - transInterval
			newChordRoot = ['C','D-','D','E-','E','F','F#','G','A-','A','B-','B'][newRoot]
			newChord = newChordRoot + chordParts[1] 
		transposedNgram.append(newChord)
	return tuple(transposedNgram)

theCorpus = mcgilldata.mcgillCorpus(mcgillPath, testMode = True)

nGramDict = dict()
longNGram = list()

for theSongid, theSong in theCorpus.songs.iteritems():
	mList = theSong.chordsFlat
	print mList
	for n in range(2, 10):	 #Set chord list
		for loc in range(len(mList)):
			if loc >= (len(mList) - n + 1): 
				break #n is length of unit (ngram); must start n-gram with enough room to account for all
			print mList[loc:loc+n]
			longNgram = transToC(mList[loc:loc+n]) #make an ngram, transposes to C based on first chord of progression
			chordList = list()
			for i in longNgram:
			    chord = i
			    chordList.append(chord)
			ngram = tuple(chordList)
		if n not in nGramDict: #create ngram entry if not in dictionary
			nGramDict[n] = dict()
			nGramDict[n]['total'] = 0
		else:
			if ngram in nGramDict[n]:
				nGramDict[n][ngram] += 1
			else:	  
				nGramDict[n][ngram] = 1
			nGramDict[n]['total'] += 1
			nGramDict['total'] += 1

w = csv.writer(open('csv-results/ngrams-countsByLength.csv', 'w'))
headerRow = list()
headerRow.append('Count')
headerRow.append('Length')
headerRow.append('% of Total Count')
headerRow.append('Chords')
outputCsv.writerow(headerRow)

for n in sorted(nGramDict):
	thisRow = list()
	for ngram in sorted(nGramDict[n]):
		thisRow = list()
		thisRow.append(nGramDict[n][ngram])
		thisRow.append(len(nGramDict[n][ngram]))
		try:	
			percent = ((nGramDict[n][ngram] * 1.0) / nGramDict['total']) * 100
		except: 
			percent = 0
		thisRow.append(percent)
		thisRow.append[n][gram]
		outputCsv.writerow(thisRow)