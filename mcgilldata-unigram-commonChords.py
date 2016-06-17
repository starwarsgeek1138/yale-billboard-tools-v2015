import mcgilldata, string, os, sys, collections, pprint, csv

#This code gives the most common chord for each root-type
#Chords are organized by chordRoot

mcgillPath = 'mcgill-billboard'

theCorpus = mcgilldata.mcgillCorpus(mcgillPath, testMode = False)

ChordTally = collections.Counter() #Create dictionary of unigram distributions for all roots
ChordTallyReduced = collections.Counter() #Create dictionary of unigram distributions for all reduced chords

for theSongid, theSong in theCorpus.songs.items():
    for thePhrase in theSong.phrases:
        for theMeasure in thePhrase.measures:
            for theChord in theMeasure.chords:
                chordRoot = theChord.rootPC
                chordQual = theChord.rootPC + theChord.quality
                chordRed = theChord.rootPC + theChord.qualityReduced
                #create chord tally for specific root
                ChordTally[chordRoot] += 1
                #create chord tally for specific reduced chord
                ChordTallyReduced[chordRed] += 1

for (chordRoot, count) in ChordTally.most_common():
	frequency = ((count * 1.0) / sum(ChordTally.values()))
	#determines frequency for a specific chordRoot
	print '{:>4}: {:.1%} ({})'.format(chordRoot,frequency,count)	
	#prints most common chords for specific root, based on given parameters
	 
	
for (chordRoot, count) in ChordTallyReduced.most_common():
	frequency = ((count * 1.0) / sum(ChordTallyReduced.values()))
	#determines frequency for a specific chordRoot
	print '{:>4}: {:.1%} ({})'.format(chordRed,frequency,count)	
	#prints most common chords for specific chord, based on given parameters 

#w = csv.writer(open('ngrams-entropyByProgressionNoKey_Beat&Form.csv', 'w'))
#for row in outputList:
 #   w.writerow(row)
    