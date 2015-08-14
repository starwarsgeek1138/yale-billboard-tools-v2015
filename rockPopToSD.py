from csv import *
from re import *
from music21 import *
from pprint import *
import json
import copy

#######################################################################

def PCNormalForm(chord1):

    '''
    The function PCNormalForm takes a list of integers and reorders them into transposed prime form.
    For example, the chord [2, 7, 11] becomes [7, 11, 2], which is [0, 4, 7] transposed up by 7 semitones.
    '''
    
    c1 = chord.Chord(chord1)
    normal = c1.normalForm
   
    ordered = c1.orderedPitchClasses
   
    Intervals= []
    NormalOrderedPcs = []
   
    i = 1
    while i <= len(ordered):
        modulus = len(ordered)
        x = (ordered[i % modulus] - ordered[(i-1)%modulus]) %12
        Intervals.append(x)
        i+=1
   
    r= 0
    while True:
        modulus = len(ordered)
        NormalOrderedPcs = []
        i = 0
        testSet = [0]
        pc = ordered[r]
        NormalOrderedPcs.append(pc)
        while i < len(Intervals)-1:
            interval = Intervals[(i+r) % modulus]+ testSet[i]
            testSet.append(interval)
            i += 1
            pc = ordered[(i+r) % modulus]
            NormalOrderedPcs.append(pc)
        r+=1
        if normal == testSet:
            global GlobalPCNormalForm
            GlobalPCNormalForm = NormalOrderedPcs
            break
    return GlobalPCNormalForm
  
#######################################################################

#myReader = reader(open('RockPopListOfChords.csv', 'rU'))
#rockVocabulary = []
#wantToAddZero = ['0', '2', '3', '4', '5', '6', '7', '8', '9']
#qualityLetters = ['m', 's', 'a', 'd']
#newChord = ''
#firstLine = True
#for row in myReader:
#    chord = row[21]
#    if firstLine:
#        firstLine = False
#        continue
#    if chord[0] in wantToAddZero:
#        newChord = '0'
#        newChord += chord
#        chord = newChord
#    elif len(chord) == 2 and chord[0] == '1':
#        newChord = '0'
#        newChord += chord
#        chord = newChord
#    elif chord[0] == '1' and chord[1] in qualityLetters:
#        newChord = '0'
#        newChord += chord
#        chord = newChord
#
#    if chord not in rockVocabulary:
#        rockVocabulary.append(chord)
#
#print 'This is the rock and pop vocabulary'
#pprint (rockVocabulary)
#print 'There are', len(rockVocabulary), 'chords in the rock and pop vocabulary'
#chordQualities = set()
#
#'''
#Yo, make it say 'Hello World!' - Alec Yang
#'''
#
#for chord in rockVocabulary:
#
#    chordQualities.add(chord[2:])
#        
#print
#print 'These are the chord qualities'    
#print (chordQualities)
#print 'There are', len(chordQualities), 'chord quality types'
#
#myWriter = writer(open('RockPop-ChordToNF.csv', 'w'))
#
#for quality in chordQualities:
#    myWriter.writerow([quality])
###############################################################################

theReader = reader(open('RockPop-ChordToNF.csv', 'rU'))
chordSwitch = {}
for row in theReader:
    initialChord = json.loads(row[1])
    normalChord = PCNormalForm(initialChord)   
    chordSwitch[row[0]] = normalChord

pprint (chordSwitch)

newReader = reader(open('RockPopListOfChords.csv', 'rU'))
newWriter = writer(open('RockPopSDListOfChords.csv', 'w'))




wantToAddZero = ['0', '2', '3', '4', '5', '6', '7', '8', '9']
qualityLetters = ['m', 's', 'a', 'd']
newChord = ''
theChord = ''
newNote = ''
quality = ''
root = ''
firstLine = True
for row in newReader:
    jazzChord = row[21]
    if jazzChord == '9min':
        pass
    if firstLine:
        newWriter.writerow(row)
        firstLine = False
        continue
    if jazzChord[0] in wantToAddZero:
        newChord = '0'
        newChord += jazzChord
        jazzChord = newChord
    elif len(jazzChord) == 2 and jazzChord[0] == '1':
        newChord = '0'
        newChord += jazzChord
        jazzChord = newChord
    elif jazzChord[0] == '1' and jazzChord[1] in qualityLetters:
        newChord = '0'
        newChord += jazzChord
        jazzChord = newChord
    quality = jazzChord[2:]
    if jazzChord[0] == '0':
        root = int(jazzChord[1])
    elif jazzChord[0] == '1':
        root = int(jazzChord[0:2])
    tonic = int(row[15])
    if quality in chordSwitch:
        theChord = ''
        theChord = copy.deepcopy(chordSwitch[quality])
        for i, note in enumerate(theChord):
            newNote = int((int(note+root)%12))
            theChord[i] = newNote
        unnormalizedChord = copy.deepcopy(theChord)
        for i, myNote in enumerate(unnormalizedChord):
            newestNote = int((int(myNote+tonic)%12))
            unnormalizedChord[i] = newestNote
#        print theChord
#        finalChord = PCNormalForm(theChord)
        row[21] = str(theChord)
        row[4] = str(theChord)
        row[3] = str(unnormalizedChord)
        newWriter.writerow(row)
        
        
        

