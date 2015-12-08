import mcgilldata, string, os, sys, collections, csv, music21

mcgillPath = 'mcgill-billboard'

#Determines distribution of chords (all tonics) by strength of beat position (metrical strength), mode, in 4/4 meter
#Mode includes ambiguous, major, and minor
#Organized by song tonic (ALL tonics, divided into modes) and by metrical strength (1, 2, 3)
#Prints total number of chords, organized by mod-12 labels for their root scale degree

theCorpus = mcgilldata.mcgillCorpus(mcgillPath, testMode = False)

chordTally = dict() #Create dictionary of unigram distributions for diff beat strengths 
chordTally['major'] = dict() #creadt dictionary of unigram distributions for major keys
chordTally['minor'] = dict() #create dictionary of unigram distributions for minor keys
chordTally['ambiguous'] = dict()
outputColumns = set()

for theSongid, theSong in theCorpus.songs.iteritems():
    
    #build distribution dictionaries for major vs. minor phrases
    for thePhrase in theSong.phrases:
        mode = thePhrase.mode
        for theMeasure in thePhrase.measures:
            songTonic = theMeasure.tonic
            if theMeasure.meter != '4/4' and theMeasure.meter != '6/4' and theMeasure.meter != '9/4' and theMeasure.meter != '12/8':               
                for theChord in theMeasure.chords:
                    beatStrength = theChord.beatStrength
                    quality = theChord.quality
                    if beatStrength == '':
                        pass
                    else:
                        try: 
                            chordRoot = music21.pitch.Pitch(theChord.rootSD).pitchClass
                        except:
                            pass #assume rootSD is an empty string
                        if beatStrength not in chordTally[mode]:
                            chordTally[mode][beatStrength] = collections.Counter()
                        outputColumns.add(chordRoot)
                        chordTally[mode][beatStrength][chordRoot] += 1
            else:
                pass
                        
outputCsv = csv.writer(open('csv-results/chordUnigrams-rootByModeandBeatStrength-noBS2.csv', 'wb'))
headerRow = list()
headerRow.append('Mode')
headerRow.append('Beat Strength')
headerRow.append('Chord Count')
for chordRoot in sorted(outputColumns):
    headerRow.append(chordRoot)
outputCsv.writerow(headerRow)

for mode in chordTally:
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

