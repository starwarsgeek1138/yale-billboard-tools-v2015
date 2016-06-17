import mcgilldata, string, os, sys, collections, pprint, csv

#This will derive the most common progressions (> 10 occurrences), with ending H > 0.9, given FULL chord names (including inversions)

#CHANGE in mcgilldata.py lines 161-162: @lazyproperty def chordsFlat(self) TO:
#   def chordsFlat(self):	 ###Use this chordsFlat for inclusion of inversions in quality (FULL CHORDS)
#		outputList = ['>S'] #one element list with this as first element (start token)
#		for thePhrase in self.phrases:
#			for theMeasure in thePhrase.measures:
#				for theChord in theMeasure.chords:
#					#converts phrase form information into single character as listed in Dict above
#					chordForm = shortFormDict[theChord.formFunction]
#					#translate chord into string of 4 elements: form, beat location, root SD, quality
#					currentChord = chordForm + str(theChord.beat) + theChord.rootSD +"_"+ theChord.quality
#					if len(outputList) > 1 and currentChord == outputList[-1]:
#						continue
#					outputList.append(currentChord)
#		outputList.append('>E') #set end token 
#		return outputList

# CHANGE in mcgilldata.py: 
#   c. line 606:
# def transToC(ngram):
           #  transposedNgram = list()
#             def chordSplit(chord): #SHITTY ALGORITHM FOR FINDING ROOT SHARP/FLAT BUT IT WORKS FOR THIS PURPOSE...
#                 if chord[3] != '#' or chord[3] != '-': #if no flat or sharp sign found, y is index of chordRoot
#                     y = 2    ##CHANGED FOR INCLUSION OF CHORD FORM AND BEAT AS 1st/2nd CHARACTER INFO (y=1 if no beat info included)
#                 else: #check for multiple sharps or flats
#                     if chord[4] == '#' or chord[4] == '-':
#                         if chord [5] == '#' or chord [5] == '-':
#                             y = 5
#                         else:
#                             y = 4
#                     else:                    
#                         y = 3
#                 #chordRoot is set as third character plus the sharp/flat sign
#                 chordRoot = chord[2:y+1] ##CHANGED FOR INCLUSION OF CHORD BEAT/Form ( [0:y+1] if no beat info included)
#                 chordQuality = chord[y+1:]
#                 chordForm = chord[0]
#                 chordBeat = chord[1] ##COMMENT OUT IF NO BEAT INFO INCLUDED IN CHORD SYMBOL
#                 return (chordRoot, chordQuality, chordBeat, chordForm)
 

mcgillPath = 'mcgill-billboard'

theCorpus = mcgilldata.mcgillCorpus(mcgillPath, testMode = False)

theCorpus.findLicksNoKey()
outputList = theCorpus.listLicks()


w = csv.writer(open('csv-results/ngrams-entropyByProgressionFullChord_NoKey_Beat&Form.csv', 'w'))
for row in outputList:
    w.writerow(row)
    