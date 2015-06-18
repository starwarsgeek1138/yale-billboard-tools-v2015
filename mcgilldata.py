import os, string

#mcgillCorpus is a dictionary of dictionaries for song metadata -
#key is name of folder/index for song as listed in billboard data structure
#dictionary is created for each song to hold four metadata: title, artist, metre, tonic

class mcgillSong:
	 def __init__(self):
		self.title = ''
		self.artist = ''
		self.phrases = list()
		self.measuresFlat = list()

class mcgillPhrase:
	def __init__(self):
		self.time = -1.	#watch emptyMeasure variable for timestamp purposes
		self.measures = list()

class mcgillMeasure:
	def __init__(self):
		self.meter = ''
		self.tonic = ''
		self.chords = list()
		self.changeMeter = False
		self.changeTonic = False
		self.measureNumber = ''	
	def __str__(self): #function for printing
		if len(self.chords) == 0 :
			return 'empty measure' + '\n'
		else :
			output = ''
			if self.changeMeter :
				output += 'Time Change: ' + self.meter + '\n'
			for theChord in self.chords:
				output += theChord.__str__() + '\n'
			return output
		
class mcgillChord:
	def __init__(self):
		self.rootPC = ''
		self.rootSD = '' #hard - do later
		self.quality = ''
		self.beat = ''
		self.beatStrength = '' #hard - do later
		self.duration = '' #hard - do later
	def __str__(self): #function for printing
		return 'b=' + str(self.beat) + ' r=' + self.rootPC + ' q=' + self.quality #prints chord as beat + root + quality	
		
class mcgillCorpus:
	def __init__(self, mcgillPath):
		self.songs = dict()
		for theFolder in os.listdir(mcgillPath):
			if theFolder == '.DS_Store':
				continue
			theSong = mcgillSong() #class for song information
			theFileName = mcgillPath + '/' + theFolder + '/' + 'salami_chords.txt'
			theFile = open(theFileName, 'r')
			currentTonic = ''
			prevTonic = ''
			currentMeter = ''
			prevMeter = ''
			for i, theLine in enumerate(theFile):
				if theLine[0:9] == '# title: ':
					if theLine[9] == ' ':
						raise RuntimeError('theLine contains too many spaces')	
					theSong.title = theLine[9:-1]
				elif theLine[0:10] == '# artist: ':
					if theLine[10] == ' ':
						raise RuntimeError('theLine contains too many spaces')	
					theSong.artist = theLine[10:-1]
				elif theLine[0:9] == '# metre: ':
					if theLine[9] == ' ':
						raise RuntimeError('theLine contains too many spaces')	
					prevMeter = currentMeter	
					currentMeter = theLine[9:-1]
				elif theLine[0:9] == '# tonic: ':
					if theLine[9] == ' ':
						raise RuntimeError('theLine contains too many spaces')	
					prevTonic = currentTonic
					currentTonic = theLine[9:-1]
				elif theLine[0] in string.digits: #we are assuming that if it begins with a digit, it's a "time" line
					thePhrase = mcgillPhrase()
					splitLine = string.split(theLine) #split the line by whitespaces
					thePhrase.time = float(splitLine[0]) #interpret first one as float for timestamp
					splitLine = string.split(theLine, '|')
					for theMeasureText in splitLine[1:-1]:
						theMeasure = mcgillMeasure()
						theMeasure.meter = currentMeter
						theMeasure.tonic = currentTonic
						if currentMeter != prevMeter:
							theMeasure.changeMeter = True
							prevMeter = currentMeter
						if currentTonic != prevTonic:
							theMeasure.changeTonic = True
							prevTonic = currentTonic
						string.strip(theMeasureText) #gets rid of extra white space before/after |
						chords = string.split(theMeasureText)
						emptyMeasure = False
						currentBeat = 0
						for i,eachItem in enumerate(chords):
							theChord = mcgillChord()
							try:
								s = string.split(eachItem, ':')
								theChord.rootPC = s[0]	
								theChord.quality = s[1]
								theChord.beat = currentBeat
								currentBeat += 1
							except:
								if eachItem[0] == '(' and eachItem[-1] == ')' :
									theMeasure.meter = eachItem[1:-1]
									theMeasure.changeMeter = True
									prevMeter = theMeasure.meter
									continue
 								if eachItem == '*' or eachItem == '&pause' :
 									emptyMeasure = True #flags empty measures (be careful with TIMESTAMPS)
 									continue 									 
 								if eachItem == 'N' :
									theChord.beat = currentBeat
									currentBeat += 1
 								if eachItem == '.' :
 									#implement something for quality/root of chord
									theChord.beat = currentBeat
									currentBeat += 1
							theMeasure.chords.append(theChord)
						if emptyMeasure : #keeps empty measures from being in analysis
							continue
						#count beats for cases where metric signature does not align with individual chords annotated. Redo if new release of Billboard data									
						beats = len(theMeasure.chords)
						if currentMeter in ['12/8', '4/4'] and beats == 2:
							theMeasure.chords[1].beat = 2
						thePhrase.measures.append(theMeasure)
						theSong.measuresFlat.append(theMeasure)		
					theSong.phrases.append(thePhrase)
			self.songs[theFolder] = theSong
								

	 
	 