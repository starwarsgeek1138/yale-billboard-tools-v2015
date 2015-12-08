import mcgilldata, string, os, sys, csv, math
from collections import defaultdict

mcgillPath = 'mcgill-billboard'

#Determines average phrase length info by mode and by section (Verse vs. Chorus vs. Other)

theCorpus = mcgilldata.mcgillCorpus(mcgillPath, testMode = False)

phraseTally = dict() #Create dictionary of phrase lengths 
phraseTally['major'] = dict() #create dict of phrase lengths for major keys
phraseTally['minor'] = dict() #create dict of phrase lengths for minor keys
phraseTally['ambiguous'] = dict() #create dict of phrases for ambiguous modes

outputColumns = set()

for theSongid, theSong in theCorpus.songs.iteritems():
#build dictionaries for length of phrases by mode and section
	for thePhrase in theSong.phrases:
		mode = thePhrase.mode
		phraseLength = thePhrase.measureLength
		section = thePhrase.formFunction
		#Identify formFunction for the phrase
		for item in section:
			if phraseLength == '' or phraseLength == ' ': #If length is blank, label as '0'
				phraseLength = 0
			if item not in phraseTally[mode]:
				phraseTally[mode][item] = list()
			phraseTally[mode][item].append(phraseLength)
				
outputCsv = csv.writer(open('csv-results/phrase-lengthByModeBySection.csv', 'wb'))
headerRow = list()
headerRow.append('Mode')
headerRow.append('Section')
headerRow.append('Average Length (in mm)')
headerRow.append('Median Length (in mm)')
headerRow.append('Range Min (in mm)')
headerRow.append('Range Max (in mm)')
outputCsv.writerow(headerRow)

def median(input_list):
	input_list.sort()
	if len(input_list) %2 == 1: #check if odd # of elements
		return input_list[len(input_list)/2]
	else: 
		return (input_list[len(input_list)/2]+input_list[len(input_list)/2-1])/2.0
def listsum(numList):
	theSum = 0
	for i in numList:
		theSum = theSum + i
	return theSum
	
for mode in phraseTally:
	#totalmode = 0
	#for section in phraseTally[mode]:
	#	totalmode += sum(phraseTally[mode][section])
	for section in phraseTally[mode]:
		#print listsum(phraseTally[mode][section])
		thisRow = list()
		thisRow.append(mode)
		thisRow.append(section)
		#descriptive statistics
		print sum(phraseTally[mode][section]), len(phraseTally[mode][section])
		average = sum(phraseTally[mode][section])/len(phraseTally[mode][section])
		thisRow.append(average)
		med = median(phraseTally[mode][section])
		thisRow.append(med)
		phraseTally[mode][section].sort()
		min = phraseTally[mode][section][0]
		thisRow.append(min)
		phraseTally[mode][section].sort()
		length = len(phraseTally[mode][section]) - 1
		max = phraseTally[mode][section][length]
		thisRow.append(max)
		outputCsv.writerow(thisRow)
