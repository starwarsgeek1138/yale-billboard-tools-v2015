import mcgilldata, string, os, sys, collections, csv, music21

mcgillPath = 'mcgill-billboard'

#Determines average phrase length per mode
#Determines where each beat strength of chord begins through a phrase

theCorpus = mcgilldata.mcgillCorpus(mcgillPath, testMode = False)

phraseTally = dict() #Create dictionary of phrase lengths 
phraseTally['major'] = list() #create list of phrase lengths for major keys
phraseTally['minor'] = list() #create list of phrase lengths for minor keys
phraseTally['ambiguous'] = list() #create list of phrases for ambiguous modes
chordTally['major']= dict() #create dictionary of chord types (by beat strength) for major keys
chordTally['minor']= dict() #create dictionary of chord types (by beat strength) for minor keys
chordTally['ambiguous']= dict() #create dictionary of chord types (by beat strength) for ambiguous keys

outputColumns = set()

for theSongid, theSong in theCorpus.songs.iteritems():
    
    #build dictionaries for length of phrases by mode
    for thePhrase in theSong.phrases:
        mode = thePhrase.mode
        phraselength = thePhrase.measureLength
        phraseTally[mode].append('phraselength')
        for theMeasure in thePhrase.measures:
            measurenumber = theMeasure.measureNumber
            for theChord in theMeasure.chords:
                beatStrength = theChord.beatStrength
                length = theChord.beatDuration
                if beatStrength == '':
                    pass
                else:
                    if beatStrength not in chordTally[mode]:
                        chordTally[mode][beatStrength] = list()
                    chordTally[mode][beatStrength].append('measurenumber')
                        
outputCsv = csv.writer(open('csv-results/chordUnigrams-beatStrengthByDurationByPhrase.csv', 'wb'))
headerRow = list()
headerRow.append('Mode')
headerRow.append('Phrase Length')
headerRow.append('Beat Strength')
headerRow.append('% of Phrase')
outputCsv.writerow(headerRow)

for mode in phraseTally:
    for beatStrength in chordTally[mode]:
        thisRow = list()
        thisRow.append(mode)
        thisRow.append(beatStrength)
        thisRow.append(sum(chordTally[mode][beatStrength].values()))
        for chordRoot in range(12):
            try:    
                total = chordTally[mode][beatStrength][chordRoot] * 1.0
            except: 
                total = 0
            thisRow.append(total)
        outputCsv.writerow(thisRow)

