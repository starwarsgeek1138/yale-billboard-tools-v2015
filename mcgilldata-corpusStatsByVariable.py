import mcgilldata, string, os, sys, collections, csv, music21

mcgillPath = 'mcgill-billboard'

#Gives spreadsheet of information by song:
    #Each song's tonic, mode, meter, instrumentation (including tonic/mode/meter change
#Mode includes ambiguous, major, and minor

theCorpus = mcgilldata.mcgillCorpus(mcgillPath, testMode = False)

#create spreadsheet with basic song information metadata
outputCsv = csv.writer(open('csv-results/corpusStatsByVariable.csv', 'wb'))
headerRow = list()
headerRow.append('SongID')
headerRow.append('Title')
headerRow.append('Artist')
headerRow.append('Song Length (in mm.)')
headerRow.append('Song Length in Phrases')
headerRow.append('Beg. Tonic') 
headerRow.append('Beg. Meter')
headerRow.append('Meter Change?')
headerRow.append('Tonic Change?')
headerRow.append('Beg. Mode')
headerRow.append('Mode Change?')
outputCsv.writerow(headerRow)

#create dictionaries to keep information for statistics of corpus
songMetaData = dict() #create dictionary of song metadata
songTallyMode = dict() #create dictionary of song modes
#songTallyMode[songID] = dict() #create dictionary of meters within each song
songTallyTonic = dict() #create dictionary of song tonics
#songTallyTonic[songID] = dict() #create dictionary of meters within each song
songTallyMeter = dict() #create dictionary of song meters
#songTallyMeter[songID] = dict() #create dictionary of meters within each song

####CODE INFORMATION

for theSongid, theSong in theCorpus.songs.iteritems():
#Build metadata spreadsheet
    thisRow = list()
    thisRow.append(theSongid)
    thisRow.append(theSong.title)
    thisRow.append(theSong.artist)
    thisRow.append(theSong.songLength)
    thisRow.append(theSong.numPhrases)
    thisRow.append(theSong.begTonic)
    thisRow.append(theSong.begMeter)
    meterChange = 0
    tonicChange = 0
    for thePhrase in theSong.phrases:
        for theMeasure in thePhrase.measures:
            if theMeasure.changeMeter == True:
                meterChange = 1
            if theMeasure.changeTonic == True:
                tonicChange = 1
    thisRow.append(meterChange)
    thisRow.append(tonicChange)
    outputCsv.writerow(thisRow)  
    
    # for thePhrase in theSong.phrases:
#         #POPULATE REMAINDER OF VALUES     
#         phraseMode = thePhrase.mode
#         if phraseMode not in songTallyMode:
#             songTallyMode[phraseMode] = dict()
#         if songID not in songTallyMode[phraseMode]:
#             songTallyMode[phraseMode][songID] = set.counter()    
#         songTallyMode[phraseMode][songID] += 1
#         if phraseMode = begMode:
#             songMetaData[songID]['modeChange'] = 0
#         else: 
#             songMetaDat[songID]['modeChange'] = 1
#             