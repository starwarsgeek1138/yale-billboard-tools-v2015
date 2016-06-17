import mcgilldata, string, os, sys, collections, pprint, csv, json

#This code identifies the distinct chord classes extant in the corpus and lists them in alphabetical order
 

mcgillPath = 'mcgill-billboard'

theCorpus = mcgilldata.mcgillCorpus(mcgillPath, testMode = True)

chordClasses = collections.Counter() #Create dictionary of unigram chord classes
outputColumns = set()

for theSongid, theSong in theCorpus.songs.iteritems():
	for thePhrase in theSong.phrases:
		for theMeasure in thePhrase.measures:
			sameChord = str() #set dummy variable to track whether chord changed
			for theChord in theMeasure.chords:
				chord = str(theChord.rootPC) + str(theChord.quality)
				quality = theChord.quality
				if sameChord != chord:
					chordClasses[quality] += 1
					sameChord = quality
				else:
					continue

#Output file writing: organize classes alphabetically
outputCsv = csv.writer(open('csv-results/chordUnigrams-byClass.csv', 'wb'))
headerRow = list()
headerRow.append('Chord Quality')
headerRow.append('Quality Count')
headerRow.append('% of Total Classes')
outputCsv.writerow(headerRow)

for quality in sorted(chordClasses):
	thisRow = list()
	thisRow.append(quality)
	thisRow.append(chordClasses[quality])
	for c in sorted(chordClasses.iteritems()):
		try:	
			percent = ((chordClasses[quality] * 1.0) / sum(chordClasses.values())) * 100
		except: 
			percent = 0
	thisRow.append(percent)
	outputCsv.writerow(thisRow)