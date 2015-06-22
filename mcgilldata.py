import os, string

#Following are classes defined for mcgill data Corpus, Song, Phrase, Measure, Chord.

class mcgillSong:
	 def __init__(self):
		self.title = ''
		self.artist = ''
		self.phrases = list() 
		self.measuresFlat = list() #for ease of parsing measure content without opening mcgillPhrase and mcgill Measure
		self.form = list() #gives form of the song

class mcgillPhrase:
	def __init__(self):
		self.time = -1.	#watch emptyMeasure variable for timestamp purposes
		self.measures = list() 
		self.measureLength = '' #identifies how long phrase is
		self.formLevel = '' #identifies formal letter label of phrase
		self.formFunction = '' #identifies formal function of phrase
	#NEW INFO FOR PRINTING FORM INFO
	def __str__(self):
		return self.formLevel + self.formFunction

class mcgillMeasure:
	def __init__(self):
		self.meter = ''
		self.tonic = ''
		self.chords = list()
		self.changeMeter = False #determines change of meter within song structure
		self.changeTonic = False #determines change of song within song structure
		self.measureNumber = ''	
	def __str__(self): #function for printing measure information
		if len(self.chords) == 0 :
			return 'empty measure' + '\n' #if no chords (i.e. 'N' or *), print as empty measure
		else :
			output = ''
			if self.changeMeter : #printer meter change info if there's a change
				output += 'Time Change: ' + self.meter + '\n'
			for theChord in self.chords: #print information for each chord from mcgillChord.__str__
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
	def __str__(self): #function for printing chord: gives beat, rootPC and quality information
		return 'b=' + str(self.beat) + ' r=' + self.rootPC + ' q=' + self.quality	
		
class mcgillCorpus:
	def __init__(self, mcgillPath): 
		self.songs = dict() #songs is a dictionary of songs instances
		for theFolder in os.listdir(mcgillPath): # establish folder as mcgillPath to parse files
			if theFolder == '.DS_Store': 
				continue #ignore .DS_Store as a folder
			theSong = mcgillSong() #class for song information
			theFileName = mcgillPath + '/' + theFolder + '/' + 'salami_chords.txt' #find data file for each song
			theFile = open(theFileName, 'r') #theFile is each song: read-only
			#Establish variables for tonic, meter and potential changes
			currentTonic = '' 
			prevTonic = ''
			currentMeter = ''
			prevMeter = ''
			#Populate classes with individual file data, enumerating through each salami_chords.txt line
			for i, theLine in enumerate(theFile):
				#find title metadata for each song, store as theSong.title
				if theLine[0:9] == '# title: ':
					#if the title line is longer than 9 characters, emit error
					if theLine[9] == ' ':
						raise RuntimeError('theLine contains too many spaces')	
					theSong.title = theLine[9:-1]
				#find artist metadata, store as theSong.artist 
				elif theLine[0:10] == '# artist: ':
					#if the line is longer than 10 characters, emit error
					if theLine[10] == ' ':
						raise RuntimeError('theLine contains too many spaces')	
					theSong.artist = theLine[10:-1]
				#find meter metadata, store as currentMeter
				elif theLine[0:9] == '# metre: ':
					#if the line is longer than 9 characters, emit error
					if theLine[9] == ' ':
						raise RuntimeError('theLine contains too many spaces')	
					prevMeter = currentMeter	#identify prevMeter for future use
					currentMeter = theLine[9:-1]
				#find tonic metadata, store as currentTonic
				elif theLine[0:9] == '# tonic: ':
					#if the line is longer than 9 characters, emit error
					if theLine[9] == ' ':
						raise RuntimeError('theLine contains too many spaces')	
					prevTonic = currentTonic #identify prevTonic for future use
					currentTonic = theLine[9:-1]
				#Parse data line-by-line; start with timespan data, parse into measures, then into individual chords
				elif theLine[0] in string.digits: #If a line begins with a digit, assume it's a time marker
					thePhrase = mcgillPhrase() #store thePhrase as class mcgillPhrase
					splitLine = string.split(theLine) #split the line by whitespaces
					lineMetaText = string.split(splitLine[0], '\t') #Split by '\t' to separate timestamp and form info
					thePhrase.time = float(lineMetaText[0]) 
					#identify if lineMetaText contains formal information
					if ", " in lineMetaText[-1]: #lineMetaText contains formal information
						#populate form information for phrase from 
						lineFormInfo = string.strip(lineMetaText[-1]) #strip form items from ending whitespace
						splitLineFormInfo = string.split(lineFormInfo, ',')
						thePhrase.formLevel = string.strip(lineFormInfo[0], ',') #Strip comma and store first item as letter label
						thePhrase.formFunction = string.strip(lineFormInfo[-1], ',') #strip comma and store last item as function label
					else: #lineMetaText contains silence/end information
						thePhrase.formFunction = string.strip(lineMetaText[-1]) #strip and store last item as function label
						continue
					#split following line information by '|' to identify measure spans
					splitLine = string.split(theLine, '|')
					#populate measure information based on split entities 1 to end of line (all data after timestamp)
					for theMeasureText in splitLine[1:-1]:
						theMeasure = mcgillMeasure() #identify measure data as mcgillMeasure class 
						theMeasure.meter = currentMeter #set current meter variable as theMeasure data
						theMeasure.tonic = currentTonic #set current tonic variable as theMeasure data
						if currentMeter != prevMeter: #if currentMeter doesn't equal prevMeter, then signal change
							theMeasure.changeMeter = True
							prevMeter = currentMeter
						if currentTonic != prevTonic: #if currentMeter doesn't equal prevMeter, then signal change
							theMeasure.changeTonic = True
							prevTonic = currentTonic
						string.strip(theMeasureText) #gets rid of extra white space before/after '|'  
						chords = string.split(theMeasureText) #sets chords as the splits of the measure line
						emptyMeasure = False 
						currentBeat = 0 
						#parse data split-by-split of each line (within each measure - identify if empty or complete measure)  
						for i,eachItem in enumerate(chords):
							theChord = mcgillChord() #identify theChord as mcgillChord class
							#set split measure contents as s - otherwise, identify type of measure content for the following cases:
								#1. (__) signifies time change (no musical measure) - set new meter, change prevMeter variables, continue
								#2. '*' signifies music with no clear harmony - set measure as emptyMeasure
								#3. '&pause' signifies arbitrary pause in song - set measure as emptyMeasure
								#4. 'N' signifies no chord data for the beat - add beat value, no harmony information added
								#5. '.' signifies chord carried over from previous beat - add beat value, implement quality/root of previous chord
							try:
								s = string.split(eachItem, ':')
								theChord.rootPC = s[0]	
								theChord.quality = s[1]
								theChord.beat = currentBeat
								currentBeat += 1
							except:
								if eachItem[0] == '(' and eachItem[-1] == ')' : #Case 1 - meter change
									theMeasure.meter = eachItem[1:-1]
									theMeasure.changeMeter = True
									prevMeter = theMeasure.meter
									continue
 								if eachItem == '*' or eachItem == '&pause' : #Case 2 and 3 - emptyMeasure
  									emptyMeasure = True #flags empty measures (be careful with TIMESTAMPS)
 									continue 									 
 								if eachItem == 'N' : #case 4 - no chord for the beat
									theChord.beat = currentBeat
									currentBeat += 1
 								if eachItem == '.' : #case 5 - carry previous chord to current beat
 									#implement something for quality/root of chord
									theChord.beat = currentBeat
									currentBeat += 1
							theMeasure.chords.append(theChord) #append chord data to theMeasure class
						if emptyMeasure : #keeps empty measures from being in analysis
							continue
						#Beat count when metric signature doesn't align with # of chords annotated (MUST redo if new release of Billboard data!)									
						#Only done for 12/8 and 4/4, when only two chords per measure
						beats = len(theMeasure.chords) #establishes the number of beats as the length of the measure (number of splits)
						if currentMeter in ['12/8', '4/4'] and beats == 2:
							theMeasure.chords[1].beat = 2 #sets the beat of the second chord as '2'
						thePhrase.measures.append(theMeasure) #append theMeasure information to thePhrase class
						theSong.measuresFlat.append(theMeasure) #append theMeasure information to theSong class
					theSong.phrases.append(thePhrase) #append thePhrase information to theSong class
			self.songs[theFolder] = theSong #define theFolder item number as dictionary key for theSong
	 
	 