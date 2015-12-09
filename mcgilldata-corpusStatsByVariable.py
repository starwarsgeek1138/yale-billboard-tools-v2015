import mcgilldata, string, os, sys, collections, csv, music21

mcgillPath = 'mcgill-billboard'

#Gives spreadsheet of information by song:
    #Each song's tonic, mode, meter, instrumentation (including tonic/mode/meter change
#Mode includes ambiguous, major, and minor

theCorpus = mcgilldata.mcgillCorpus(mcgillPath, testMode = True)

#create spreadsheet with basic song information metadata
outputCsv = csv.writer(open('csv-results/corpusStatsByVariable.csv', 'wb'))
headerRow = list()
headerRow.append('SongID')
headerRow.append('Title')
headerRow.append('Artist')
headerRow.append('Beg. Tonic') 
headerRow.append('Beg. Mode')
headerRow.append('Beg. Meter')
headerRow.append('Meter Change?')
headerRow.append('Tonic Change?')
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
    thisRow = list()
#Build metadata spreadsheet
    songID = theSongid
        if songID not in songMetaData:
            songMetaData[songID] = dict()
    songMetaData[songID][songTitle] = theSong.title
    songMetaData[songID][songArtist] = theSong.artist
    begTonicTrack = 0
    begMode = 0
    for thePhrase in theSong.phrases:
        #FIND BEGINNING SONG VALUES ONLY (TONIC, METER, MODE)    
        for theMeasure in thePhrase.measures:
            while begTonicTrack == 0:
                if theMeasure.measureNumber == 1:
                    songMetaData[songID]['begTonic'] = theMeasure.tonic
                    songMetaData[songID]['begMode'] = thePhrase.mode
                    begMode = 0
                    songMetaData[songID]['begMeter'] = theMeasure.meter
                    begTonicTrack += 1
            meterChange = 0
            while meterChange == 0:
                if theMeasure.changeMeter == True:
                    songMetaData[songID]['meterChange'] = 1
                    meterChange = 1
                else:
                    songMetaData[songID]['meterChange'] = 0
                    meterChange = 0
            tonicChange = 0
            while tonicChange == 0:
                if theMeasure.changeTonic == True:
                    songMetaData[songID]['tonicChange'] = 1
                    tonicChange = 1
                else:
                    songMetaData[songID]['tonicChange'] = 0
                    tonicChange = 0
                    
        #POPULATE REMAINDER OF VALUES     
        phraseMode = thePhrase.mode
        if phraseMode not in songTallyMode:
            songTallyMode[phraseMode] = dict()
        if songID not in songTallyMode[phraseMode]:
            songTallyMode[phraseMode][songID] = set.counter()    
        songTallyMode[phraseMode][songID] += 1
        if phraseMode = begMode:
            songMetaData[songID]['modeChange'] = 0
        else: 
            songMetaDat[songID]['modeChange'] = 1
            
outputCsv.writerow(thisRow)
