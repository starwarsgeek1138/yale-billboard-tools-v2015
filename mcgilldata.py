import os, string, music21

#Following are classes defined for mcgill data Corpus, Song, Phrase, Measure, Chord.

beatsPerMeasure = { #lookup table for beat definitions per meter
 	'1/4': 1,
	'2/4': 2,  
	'3/4': 3,
	'4/4': 4,
	'5/4': 5,
	'6/4': 6,
	'7/4': 7,
	'9/4': 9,
	'3/8': 1,
	'5/8': 2,
	'6/8': 2,
	'9/8': 3,
	'12/8': 4 } 
	
beatStrengthByMeter = {
	'4/4': [3,1,2,1],
	'6/4': [3,1,1,2,1,1],
	'9/4': [3,1,1,2,1,1,2,1,1],
	'3/4': [3,1,1],
	'3/8': [3],
	'5/8': [3,1] } #make sure consistent with number of beats per measure found in corpus (index numbers in music)
		#etc etc etc 

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
		self.formLetter = '' #identifies formal letter label of phrase
		self.formFunction = set() #identifies formal function of phrase
		self.changeForm = False #determines if change in formal section
		self.theLine = ''
		self.splitLine = list()
	#NEW INFO FOR PRINTING FORM INFO
	def __str__(self):
		output = str(self.time) + ': '
		if self.changeForm: 
			output += '*'
		output += self.formLetter + ' ( '
		for item in self.formFunction:
			output += item + ' '
		output += ')'
		
		return output
		
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
		self.rootSD = ''
		self.quality = ''
		self.beat = ''
		self.beatStrength = '' #hard - do later
		self.beatDuration = ''
		self.secsDuration = '' #determines chord length in seconds -  - TO DO AT A LATER TIME
	def __str__(self): #function for printing chord: gives beat, rootPC and quality information
		return 'b=' + str(self.beat) + ' d=' + str(self.beatDuration) + ' sd=' + self.rootSD + ' q=' + self.quality
		
		
class mcgillCorpus:
	def __init__(self, mcgillPath, testMode = False): #set variable for testing parameters (shorten time!)
		self.songs = dict() #songs is a dictionary of songs instances
		for j,theFolder in enumerate(os.listdir(mcgillPath)): # establish folder as mcgillPath to parse files
			if testMode and j > 20:
				break
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
			currentFormLetter = ''
			currentFormFunction = set()
			
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
					thePhrase.time = float(splitLine[0]) #Set/store timestamp information as float
					thePhrase.theLine = theLine
					theLine = ' '.join(splitLine[1:]) #theLine without timestamp information
					splitLine = string.split(theLine, '|')
									
					#FORM INFORMATION
					thePhrase.splitLine = splitLine
					if splitLine[0] == '' : #ignore if phrase has no form information (line starts with '|')
						thePhrase.formLetter = currentFormLetter
						thePhrase.formFunction = currentFormFunction
					else: #find form information
						formInfo = string.split(splitLine[0], ',')  #take form info from line and split it by commas
						currentFormFunction = set()
						thePhrase.formLetter = currentFormLetter
						for item in formInfo: #iterate through items in forminfo 
							if len(item) == 0:  #if comma has nothing after it, ignore
								continue
							if item[0] in string.uppercase: #if item starts with capital letter, it is a letter label -- store as formLetter
								thePhrase.formLetter = item
								currentFormLetter = item 
								thePhrase.changeForm = True
							else:
								thePhrase.formFunction.add(item) #else, item is a function label -- store as formFunction
								currentFormFunction.add(item)

					#MEASURE DATA: split following line information by '|' to identify measure spans
					
					#populate measure information based on split entities 1 to end of line (all data after timestamp)
					for theMeasureText in splitLine[1:-1]:
						theMeasure = mcgillMeasure() #identify measure data as mcgillMeasure class 
						theMeasure.meter = currentMeter #set current meter variable as theMeasure data
						theMeasure.tonic = currentTonic #set current tonic variable as theMeasure data
						if currentMeter != prevMeter: #if currentMeter doesn't equal prevMeter, then signal change
							theMeasure.changeMeter = True
							prevMeter = currentMeter
						if currentTonic != prevTonic: #if currentTonic doesn't equal prevTonic, then signal change
							theMeasure.changeTonic = True
							prevTonic = currentTonic
						string.strip(theMeasureText) #gets rid of extra white space before/after '|'  
						chords = string.split(theMeasureText) #sets chords as the splits of the measure line
						emptyMeasure = False 
						currentBeat = 0
						 
						#parse each split of the line (within each measure - identify if empty or complete measure)  
						for i,eachItem in enumerate(chords):
							theChord = mcgillChord() #identify theChord as mcgillChord class
							
							#set split measure contents as s - otherwise, identify type of measure content for the following cases:
								#1. (__) signifies time change (no musical measure) - set new meter, change prevMeter variables, continue
								#2. '*' signifies music with no clear harmony - set measure as emptyMeasure
								#3. '&pause' signifies arbitrary pause in song - set measure as emptyMeasure
								#4. 'N' signifies no chord data for the beat - add beat value, no harmony information added
								#5. '.' signifies chord carried over from previous beat - add beat value, implement quality/root of previous chord
							
							#store harmony contents if no problem
							s = string.split(eachItem, ':') #split s by ':' to identify chords from other entities
							if len(s) == 2: #is this a chord? 
								theChord.rootPC = s[0]
								p = music21.pitch.Pitch(s[0].replace('b','-')+'4') #pitch of the root of the chord
								x = music21.pitch.Pitch(currentTonic.replace('b','-')) #pitch of the current tonic 
								y = music21.pitch.Pitch('C') #pitch of 'C' (reference for transposition)
								ivl = music21.interval.Interval(noteStart = x, noteEnd = y) #interval between reference 'C' and SD root of chord	
								theChord.rootSD = p.transpose(ivl).name
								theChord.quality = s[1]
								theChord.beat = currentBeat
								currentBeat += 1
							else: #not a chord since no colon
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
									theChord.rootPC = '.'
									currentBeat += 1
							theMeasure.chords.append(theChord) #append chord data to theMeasure class
						if emptyMeasure : #keeps empty measures from being in analysis
							continue
						#Beat count when metric signature doesn't align with # of chords annotated (MUST redo if new release of Billboard data!)									
						#Only done for 12/8 and 4/4, when only two chords per measure
						beats = len(theMeasure.chords) #establishes the number of beats as the length of the measure (number of splits)
						if currentMeter in ['12/8', '4/4'] and beats == 2:
							theMeasure.chords[1].beat = 2 #sets the beat of the second chord as '2'
						w = 0
						while w < (len(theMeasure.chords)): #go through measure, identify '.' and take out (for replacement with duration) at location w
							if theMeasure.chords[w].rootPC == '.':
								theMeasure.chords.pop(w) #deleting chord item w (aka '.') from list of chords within this measure
							else: #no '.' at location 'w'
 								w += 1
 						for w in range(len(theMeasure.chords)):
 							if w < (len(theMeasure.chords) - 1):
 								theMeasure.chords[w].beatDuration = theMeasure.chords[w+1].beat - theMeasure.chords[w].beat
 							else:
 								theMeasure.chords[w].beatDuration = beatsPerMeasure[currentMeter] - theMeasure.chords[w].beat
 						thePhrase.measures.append(theMeasure) #append theMeasure information to thePhrase class
						theSong.measuresFlat.append(theMeasure) #append theMeasure information to theSong class
					theSong.phrases.append(thePhrase) #append thePhrase information to theSong class
			self.songs[theFolder] = theSong #define theFolder item number as dictionary key for theSong
	 
	 