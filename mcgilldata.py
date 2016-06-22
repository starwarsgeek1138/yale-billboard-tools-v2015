import os, string, music21, sys, cPickle, time, json, csv, collections, math, fractions

# from http://stackoverflow.com/questions/3012421/python-lazy-property-decorator
# used for lazy evaluation of flatLetter and flatSD

class lazy_property(object):
	'''
	meant to be used for lazy evaluation of an object attribute.
	property should represent non-mutable data, as it replaces itself.
	'''

	def __init__(self,fget):
		self.fget = fget
		self.func_name = fget.__name__


	def __get__(self,obj,cls):
		if obj is None:
			return None
		value = self.fget(obj)
		setattr(obj,self.func_name,value)
		return value


#Following are classes defined for mcgill data Corpus, Song, Phrase, Measure, Chord.
#Main parser for McGill data Corpus

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

beatStrengthByMeter = { #lookup table for beat strengths by meter
	'1/4': [3],
	'2/4': [3,1],
	'3/4': [3,1,1],
	'4/4': [3,1,2,1],
	'5/4': [3,1,1,1,1],
	'6/4': [3,1,1,2,1,1],
	'7/4': [3,1,1,1,1,1,1],
	'9/4': [3,1,1,2,1,1,2,1,1],
	'3/8': [3],
	'5/8': [3],
	'6/8': [3,1],
	'9/8': [3,1,1],
	'12/8': [3,1,2,1] }
	
chordLabelAbstraction = { #lookup table for chord label abstraction
	'maj': 'M',
	'maj7': 'M7',
	'min': 'mi',
	'min7': 'mi7',	
	'7': '7',
	'sus4': 's4',
	'no3': 'n',
	'': 'n',
	'maj6': 'M6',
	'min6': 'mi6',
	'no3': 'n',
	'aug': 'a',
	'dim': 'd',
	'dim7': 'dd',
	'hdim': 'hd' }
	
formTranslateDict = { #lookup/standardization table for form functions
	'applause': '',	  
	'bridge': 'bridge', #shortened as b
	'coda': 'outro', #shortened as o
	'chorus': 'chorus', #shortened as c
	'chorusa': 'chorus',
	'chorusb': 'chorus',
	'end': '',
	'ending': 'outro',
	'fadein': 'fadein', #shortened as n (think: in)
	'fadeout': 'fadeout',	#changed to d (think: decay) 
	'flute)': '',
	'instrumental': 'instrumental', #shortened as s
	'instrumentalbreak': 'instrumental',
	'interlude': 'interlude', #shortened as u
	'intro': 'intro', #shortened as i
	'introa': 'intro',
	'introb': 'intro',
	'keychange': 'transition', #shortened as t
	'maintheme': 'theme',  #shortened as h
	'modulation': 'transition',
	'noise': '',
	'outro': 'outro',
	'prechorus': 'prechorus', #shortened as p
	'prechorustwo': 'prechorus',
	'preintro': '', 
	'preverse': 'interlude',
	'refrain': 'refrain', #shortened as r
	'(secondary)theme': 'theme',
	'secondarytheme': 'theme',
	'silence': '',
	'solo': 'solo', #shortened as l
	'spoken': '',
	'spokenverse': '',
	'talking': '',
	'theme': 'theme',
	'trans': 'transition',
	'transition': 'transition',
	'verse': 'verse', #shortened as v
	'versefive': 'verse',
	'versefour': 'verse',
	'verseone': 'verse',
	'versethree': 'verse',
	'versetwo': 'verse',
	'vocal': ''}

shortFormDict = { #Short one-letter versions for chord functions  
	'bridge': 'b',
	'chorus': 'c', 
	'fadein': 'n', #shortened as n (think: in)
	'fadeout': 'd',	  #changed to d (think: decay) 
	'instrumental': 's', 
	'interlude': 'u',
	'intro': 'i',
	'outro': 'o',
	'prechorus': 'p', 
	'refrain': 'r',
	'solo': 'l',
	'theme': 'h',
	'transition': 't',
	'verse': 'v',
	'': ' '}
	
pitchClassTranslate = {
	'C' : 0,
	'B#' : 0,
	'C#' : 1,
	'D-' : 1,
	'D' : 2,
	'E--': 2,
	'D#' : 3,
	'E-' : 3,
	'E' : 4,
	'F-' : 4,
	'E#' : 5, 
	'F' : 5,
	'F#' : 6,
	'G-' : 6,
	'F##' : 7,
	'G' : 7,
	'A--': 7,
	'G#' : 8,
	'A-' : 8,
	'A' : 9,
	'B--' : 9,
	'A#' : 10,
	'B-' : 10,
	'B' : 11,
	'C-' : 11 }
	
class mcgillSong:
	def __init__(self):
		self.songID = ''
		self.title = ''
		self.artist = ''
		self.phrases = list() 
		self.numPhrases = '' #number of phrases in song with harmonic content ONLY
		self.measuresFlat = list() #for ease of parsing measure content without opening mcgillPhrase and mcgill Measure
		self.form = list() #gives form of the song
		self.begTonic = '' #gives beginning tonic of song
		self.begMeter = '' #gives beginning tonic of song
		self.songLength = 0 #identifies number of measures in song
	
	@lazy_property #Lazy prop for a flat list of chords with transposed SD and quality
	def chordsFlat(self):	####Use this chordsFlat for excluding inversions in quality
		outputList = ['>S'] #one element list with this as first element (start token)
		for thePhrase in self.phrases:
			for theMeasure in thePhrase.measures:
				for theChord in theMeasure.chords:
					qualitySplit = string.split(theChord.quality, "/")[0]
					if qualitySplit == '':
						continue
					chordForm = shortFormDict[theChord.formFunction]
					currentChord = chordForm + str(theChord.beat) + theChord.rootSD + '_' + reducedQuality[qualitySplit]
					if len(outputList) > 1 and currentChord == outputList[-1]:
						continue
					outputList.append(currentChord)
		outputList.append('>E') #set end token 
		return outputList		  
	# def chordsFlat(self):	 ###Use this chordsFlat for inclusion of inversions in quality (FULL CHORDS)
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
			 
	@lazy_property
	def begTonic(self):
		begTonic = ''
		for thePhrase in self.phrases:
			for theMeasure in thePhrase.measures:
				if theMeasure.measureNumber == 1:
					begTonic = theMeasure.tonic
					break
			if begTonic != '':
				break
		return begTonic

			 
class mcgillPhrase:
	def __init__(self):
		self.time = -1. #watch emptyMeasure variable for timestamp purposes
		self.measures = list() 
		self.measureLength = 0 #identifies how long phrase is
		self.formLetter = '' #identifies formal letter label of phrase
		self.formFunction = list() #identifies formal function of phrase
		self.changeForm = False #determines if change in formal section
		self.theLine = ''
		self.mode = ''
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
		self.formFunction = list() #identifies formal function of the measure's phrase
		self.changeMeter = False #determines change of meter within song structure
		self.changeTonic = False #determines change of song within song structure
		self.measureNumber = 0 #determines measure number within the phrase
	def __str__(self): #function for printing measure information
		if len(self.chords) == 0 :
			return 'empty measure' + '\n' #if no chords (i.e. 'N' or *), print as empty measure
		else :
			output = 'Measure: ' + str(self.measureNumber) + ' - ' + '\n'
			if self.changeMeter : #print meter change info if there's a change
				output += 'Time Change: ' + self.meter + '\n'
			for theChord in self.chords: #print information for each chord from mcgillChord.__str__
				output += theChord.__str__() + '\n'
			return output
		
class mcgillChord:
	def __init__(self):
		self.rootPC = ''
		self.rootSD = ''
		self.quality = ''
		self.qualityReduced = ''
		self.qualityNormalForm = ''
		self.beat = ''
		self.beatStrength = '' 
		self.beatDuration = ''
		self.formFunction = '' #identifies formal function of the chord's phrase
		self.secsDuration = '' #determines chord length in seconds -  - TO DO AT A LATER TIME
	def __str__(self): #function for printing chord: gives beat, rootPC and quality information
		return 'b=' + str(self.beat) + ' d=' + str(self.beatDuration) + ' sd=' + self.rootSD + ' q=' + self.quality + ' bs=' + str(self.beatStrength)
  
		
class mcgillCorpus:
	def __init__(self, mcgillPath, testMode = False): #set variable for testing parameters (shorten time!)
		
		##################
		#  PICKLE		 #
		##################
		
		### Define dupSongID as dictionary that calls list of duplicates from RockPop-DupSongID.csv for conversion		 
		global dupSongID
		global dupSongNum
		global dupSongOthers
		dupSongID = dict()
		dupSongNum = dict()		 
		dupSongOthers = dict()
		theReader = csv.reader(open('RockPop-DupSongID.csv', 'rU'))
		for row in theReader:
			dupSong = json.loads(row[1]) #identifies token duplicated ID
			dupSongID[row[0]] = dupSong #Finds a duplicated song (in row[0]) and translates that song to the token duplicated ID
			dupSongNum[row[0]] = row[2] #spits out how many other duplicated songs there are
			dupSongOthers[row[0]] = row[3] #spits out what the other duplicated songs are
		
		### Define quality2NF as dictionary that calls normal chord list from RockPop-ChordTo-NF.csv for conversion		  
		global quality2NF
		global reducedQuality
		global triadQuality
		quality2NF = dict()
		reducedQuality = dict()
		triadQuality = dict()		 
		theReader = csv.reader(open('RockPop-ChordToNF.csv', 'rU'))
		for row in theReader:
			normalChord = json.loads(row[1]) #json will read text from NFchord .csv as list data  
			quality2NF[row[0]] = normalChord
			reducedQuality[row[0]] = row[2] #translates quality of chord to reduced triad or 7th chord
			triadQuality[row[0]] = row[3] #translates quality of chord to maximally reduced name (triad)

		pickleFilename = 'mcgillCorpusData.pickle'
		if os.path.isfile(pickleFilename):
			sys.stderr.write("getting data from Song Corpus pickle... ")
			start = time.clock()
			self.songs = cPickle.load(open(pickleFilename, 'r'))
			sys.stderr.write(str(time.clock()-start) + ' secs\n')
		else:
			sys.stderr.write("Song Corpus data pickle not found, recalculating... ")
			start = time.clock()
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
				theSong.songID = theFolder
				prevTonic = ''
				currentMeter = ''
				prevMeter = ''
				currentFormLetter = ''
				currentFormFunction = list()
				begMeterCounter = 0
				begTonicCounter = 0
		
				#Populate classes with individual file data, enumerating through each salami_chords.txt line
				songPhraseLength = 0 #start phrase counter	
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
						begMeterCounter += 1
						#if the line is longer than 9 characters, emit error
						if theLine[9] == ' ':
							raise RuntimeError('theLine contains too many spaces')	
						if begMeterCounter < 2:
							prevMeter = theLine[9:-1]
							theSong.begMeter = theLine[9:-1]
						else:
							prevMeter = currentMeter #identify prevMeter for future use
						currentMeter = theLine[9:-1]
  
					#find tonic metadata, store as currentTonic
					elif theLine[0:9] == '# tonic: ':
						begTonicCounter += 1
						#if the line is longer than 9 characters, emit error
						if theLine[9] == ' ':
							raise RuntimeError('theLine contains too many spaces')	
						if begTonicCounter < 2:
							prevTonic = theLine[9:-1]
							theSong.begTonic = theLine[9:-1]
						else:
							prevTonic = currentTonic #identify prevTonic for future use
						currentTonic = theLine[9:-1]
						
					#Parse data line-by-line; start with timespan data, parse into measures, then into individual chords
					elif theLine[0] in string.digits: #If a line begins with a digit, assume it's a time marker
						thePhrase = mcgillPhrase() #store thePhrase as class mcgillPhrase
						splitLine = string.split(theLine) #split the line by whitespaces
						thePhrase.time = float(splitLine[0]) #Set/store timestamp information as floate
						thePhrase.theLine = theLine
						theLine = ' '.join(splitLine[1:]) #theLine without timestamp information
								
						#FORM/MODE INFORMATION (== splitLine[0])
						##Create blank variables to tally chord-score for phrase MODE INFORMATION 
						minorScore = 0
						majorScore = 0
						splitLine = string.split(theLine, '|') #split the line by '|'  
						thePhrase.splitLine = splitLine		 
						if theLine[0] == '|' : #ignore if phrase has no form information (theLine starts with '|')
							thePhrase.formLetter = currentFormLetter
							thePhrase.formFunction = currentFormFunction
						else: #find form information
							#print splitLine
							formInfo = string.split(splitLine[0], ',')	#form info is splitLine split by commas
							#print formInfo
							currentFormFunction = list() #form info put into list of items
							thePhrase.formLetter = currentFormLetter
							for item in formInfo: #iterate through items in forminfo 
								#Format formInfo items to get rid of dashes, blank spaces, etc.
								if item[0] == ' ': #if item begins blank, get rid of space
									item = item.translate(None, ' ')   
								if len(item) == 0 or item == ' ' or item == '': #if item length is zero or blank (no form info), ignore
									continue
								if item.find('-') != -1: #if item contains dash, get rid of dash
									item = item.translate(None, '-')
								if item[0] in string.uppercase: #if item starts with capital letter, it is a letter label -- store as formLetter
									thePhrase.formLetter = item
									currentFormLetter = item 
									thePhrase.changeForm = True
								else:	#if lowercase, formFunction: standardize using translation dictionary
									function = formTranslateDict[item] #use translation chart to identify proper form function label
									if function == '': #identifies translation that is blank, ignores
										continue
									else:  #identifies proper translation as form function	 
										thePhrase.formFunction.append(function) #else, item is a function label -- store as formFunction
										currentFormFunction.append(function)

						#MEASURE DATA POPULATION: 
						#Split line information by '|' to identify measure spans
						#Populate measure information (based on split entities 1 to lineend AKA all data after line's timestamp)
						measureCounter = 0 #establish measure counter to keep track of # of measures
						for theMeasureText in splitLine[1:-1]:
							measureCounter += 1
							theMeasure = mcgillMeasure() #identify measure data as mcgillMeasure class 
							theMeasure.meter = currentMeter #set current meter variable as theMeasure data
							theMeasure.tonic = currentTonic #set current tonic variable as theMeasure data
							theMeasure.formFunction = function #set current function as form function variable in theMeasure data
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

							#CHORDS: parse each split of the line (within each measure - identify if empty or complete measure)	 
							for i,eachItem in enumerate(chords):
								theChord = mcgillChord() #identify theChord as mcgillChord class
						
								#set split measure contents as s - otherwise, identify type of measure content for the following cases:
									#1. (__) signifies time change (no musical measure) - set new meter, change prevMeter variables, delete measure from counter, continue
									#2. '*' signifies music with no clear harmony - set measure as emptyMeasure, delete measure from counter
									#3. '&pause' signifies arbitrary pause in song - set measure as emptyMeasure
									#4. 'N' signifies no chord data for the beat - add beat value, no harmony information added
									#5. '.' signifies chord carried over from previous beat - add beat value, implement quality/root of previous chord
						
								#store harmony contents of chords if no problems found
								s = string.split(eachItem, ':') #split s by ':' to identify chords from other entities
								if len(s) == 2: #Is this a chord? Only a chord if there are two elements when split by ":" 
									theChord.formFunction = function
									theChord.rootPC = s[0]
									p = music21.pitch.Pitch(s[0].replace('b','-')+'4') #pitch of the root of the chord
									x = music21.pitch.Pitch(currentTonic.replace('b','-')) #pitch of the current tonic 
									y = music21.pitch.Pitch('C') #pitch of 'C' (reference for transposition)
									ivl = music21.interval.Interval(noteStart = x, noteEnd = y) #interval between reference 'C' and SD root of chord	
									theChord.rootSD = p.transpose(ivl).name
									theChord.quality = s[1]
									theChord.qualitySplit = string.split(theChord.quality, "/")[0]
									theChord.qualityReduced = reducedQuality[theChord.qualitySplit]
									try: 
										theChord.qualityNormalForm = quality2NF[theChord.qualitySplit]
									except:
										print theChord.qualitySplit 
									theChord.beat = currentBeat
									#identify and store current beat strength 
									meterStrengths = beatStrengthByMeter[theMeasure.meter]
									theChord.beatStrength = meterStrengths[currentBeat]
									currentBeat += 1 #add count for next beat
									
									#MODE identification: Store chord information								
									try:  #turn chordRoot into a pitch object 
										chordRoot = music21.pitch.Pitch(theChord.rootSD).pitchClass
									except: #assume rootSD is empty
										pass
									quality = theChord.qualityNormalForm #turn the quality of the chord into a normalForm	
									for theNote in quality: #find if the notes of the chord include b3, b6, b7 in the home tonic
										if (theNote + chordRoot) % 12 in [3,8,10]:
											minorScore += 1 #if b3, b6, b7 are present, add 1 to minorScore
										elif (theNote + chordRoot) % 12 in [4,9,11]:
											majorScore += 1 #if 3, 6, and 7 are present, add 1 to majorScore
								else: #If no colon is present, no chord present, take special cases as above
									if eachItem[0] == '(' and eachItem[-1] == ')' : #Case 1 - meter change
										theMeasure.meter = eachItem[1:-1]
										theMeasure.changeMeter = True
										prevMeter = theMeasure.meter
										continue
									if eachItem == '*' or eachItem == '&pause' : #Case 2 and 3 - emptyMeasure
										emptyMeasure = True #flags empty measures (be careful with TIMESTAMPS)
										measureCounter -= 1
										continue									 
									if eachItem == 'N' : #case 4 - no chord for the beat
										theChord.beat = currentBeat
										currentBeat += 1
									if eachItem == '.' : #case 5 - carry previous chord to current beat
										#implement something for quality/root of chord 
										theChord.formFunction = function
										theChord.beat = currentBeat
										theChord.rootPC = '.'
										currentBeat += 1 
								theMeasure.chords.append(theChord) #append chord data to theMeasure class
								theMeasure.measureNumber = measureCounter	#appends # of measure (within phrase)
																
							##FIND BEAT DURATION FOR MEASURES WITH *, N, ' ' or other values   
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
							thePhrase.measureLength = int(measureCounter) * 1.0 #stores length of Phrase (in measures) information 
							thePhrase.measures.append(theMeasure) #append theMeasure information to thePhrase class
							theSong.measuresFlat.append(theMeasure) #append theMeasure information to theSong class
						
						if int(thePhrase.measureLength) > 0:  # Gets # of phrases in song and # of measures in song						
							songPhraseLength += 1	  
						theSong.numPhrases = songPhraseLength #Store length of song (in phrases)					
						theSong.songLength += int(thePhrase.measureLength)	#store total number of measures in song
						
						##MODE: Calculate Phrase Mode Information
						##Mode is determined by: 
						##	1) Identifying tonic of each song 
						##	2) Identifying normal form of each chord within a phrase *using external Rockpop-NSF list*
						##	3) Identify if chord tones are b3, b6, and b7 in tonic key (add to a minor-key counter)
						##	4) If the minor-key counter outweighs the counter for major key, codify phrase as minor (if equal, ambiguous mode)

						if minorScore == majorScore:
							thePhrase.mode = 'ambiguous' 
						elif minorScore > majorScore: #identify whether majorScore or minorScore prevails in phrase
							#if minorScore prevails, phrase encoded as minor, chords added to minor dictionary tally
							thePhrase.mode = 'minor'
						else:
							thePhrase.mode = 'major'	   
						theSong.phrases.append(thePhrase) #append thePhrase information to theSong class
				self.songs[theFolder] = theSong #define theFolder item number as dictionary key for theSong
		
			#write pickle
			cPickle.dump(self.songs, open(pickleFilename,'w'), protocol=cPickle.HIGHEST_PROTOCOL)
			sys.stderr.write(str(time.clock()-start) + ' secs\n')
#####END OF MAIN PARSING CODE	   
	
###############################################################################		
#########TRAVERSE SUFFIX TREE - for chord progression finding##################
############################################################################### 
###CODE FOR FINDING LICKS BASED ON TONICS AND ROMAN NUMERALS
	def findLicks( self, treeDepth = 20, countThreshold = 10, entropyThreshold = .9):
		#Parameters for findLicks:
			#treeDepth - delimits the number of levels created for suffix tree
			#countThreshold - delimits the size of the count for each case (prefix)
		
		self.suffixTree = dict()
		self.treeDepth = treeDepth
		self.countThreshold = countThreshold
		self.entropyThreshold = entropyThreshold
		for n in range(1,self.treeDepth+1): #sets up suffix tree - a dict of dict for progressions of various lengths (n)
			self.suffixTree[n] = dict()
			self.suffixTree[n]['total'] = 0

		self.keyDistribution = collections.defaultdict(collections.Counter)
			#are certain progressions confined to specific keys?


		for theSongID, theSong in self.songs.items():

			mList = theSong.chordsFlat
			# Build suffix tree

			for n in range(1, self.treeDepth+1):
	
				# suffix tree
	
				for loc in range(len(mList)):
					if loc >= (len(mList) - n + 1): break #n is length of unit (ngram); must start n-gram with enough room to account for all
					ngram = tuple(mList[loc:loc+n]) #make the ngram
					#print ngram
					prefix = tuple(ngram[0:-1]) #prefix = all but the last element of ngram
					suffix = tuple([ngram[-1]]) #suffix = last element of ngram
					if prefix not in self.suffixTree[n]: #create prefix entry if not in dictionary
						self.suffixTree[n][prefix] = dict() #tallies number of times that the suffix follows this prefix
						self.suffixTree[n][prefix]['total'] = 0
					if suffix in self.suffixTree[n][prefix]:
						self.suffixTree[n][prefix][suffix] += 1
					else:
						self.suffixTree[n][prefix][suffix] = 1
					self.suffixTree[n][prefix]['total'] += 1
			
					self.suffixTree[n]['total'] += 1
		
					# tally modal distribution of lick
					
					self.keyDistribution[ngram][theSong.begTonic] += 1 #adds ngram to dictionary of tonics
					
###CODE FOR FINDING LICKS NAIVE TO TONIC/RN (BASED ON CHORD QUALITY AND INTERVAL MOTION ONLY)
	def findLicksNoKey(self, treeDepth = 20, countThreshold = 10, entropyThreshold = .9):
		########################################
		#########PICKLE #2 #####################
		########################################
		pickleFilename = 'mcgillCorpusDataEntropyProgs.pickle'
		if os.path.isfile(pickleFilename):
			sys.stderr.write("getting data from Entropy pickle... ")
			start = time.clock()
			self.songs = cPickle.load(open(pickleFilename, 'r'))
			sys.stderr.write(str(time.clock()-start) + ' secs\n')
		else:
			sys.stderr.write("Entropy data pickle not found, recalculating... ")
			start = time.clock()
			
		def transToC(ngram):
			transposedNgram = list()
			def chordSplit(chord):
				chordRootInfo = chord.split("_")[0]
				chordRoot = chordRootInfo[2:]
				#OLD CODE FOR FINDING ROOTS/QUALITY (Finds sharps or flats after chord root and separates root info from quality - not reliable...
				#n = chord.rfind('-') #find flats in chord (from the right)
				#p = chord.rfind('#') # find sharps in chord (from the right)
				#if n == -1 and p == -1:
				#	y = 2	  ##CHANGED FOR INCLUSION OF CHORD FORM AND BEAT AS 1st/2nd CHARACTER INFO - y=1 if no beat info wanted
				#else:
				#	y = max(n,p)
				#chordRoot = chord[2:y+1] ##CHANGED FOR INCLUSION OF CHORD BEAT/Form - [0:y+1] if no beat info wanted
				#chordQuality = chord[y+1:]
				chordForm = chord[0]
				beat = int(chord[1])
				chordBeat = str(beat + 1) ##COMMENT OUT IF NO BEAT INFO INCLUDED IN CHORD SYMBOL (ADDS ONE TO MAKE 1st beat = 1) 
				try:
					chordQuality = chord.split("_")[1]
				except: 
					chordQuality = ''
				return (chordRoot, chordQuality, chordBeat, chordForm)
			
			first = True #dummy variable for identifying first chord of a song
			for chord in ngram:
				if chord == '>S' or chord == '>E' or chord[0] == ' ':
					newChord = chord
				else: ##TRANSPOSES PROGRESSION: First chord of prefix is always "C" 
					chordParts = chordSplit(chord) 
					if first:
						firstChordRoot = chordParts[0]
						transInterval = pitchClassTranslate[firstChordRoot]
						first = False
					newRoot = pitchClassTranslate[chordParts[0]] - transInterval
					newChordRoot = ['C','D-','D','E-','E','F','F#','G','A-','A','B-','B'][newRoot]
					newChord = chordParts[2] + newChordRoot + chordParts[1] + chordParts[3] #new chord = chord beat + transposed root + chord quality + chord Form --> get rid of chordParts[2] if no beat info included
				transposedNgram.append(newChord)
			return tuple(transposedNgram)
			
		#Parameters for findLicksNoKey:
			#treeDepth - delimits the number of levels created for suffix tree
			#countThreshold - delimits the size of the count for each case
		
		self.suffixTree = dict()
		self.songIDLicks = dict()
		self.treeDepth = treeDepth
		self.countThreshold = countThreshold
		self.entropyThreshold = entropyThreshold
		for n in range(1,self.treeDepth+1): #sets up suffix tree - a dict of dict for progressions of various lengths (n)
			self.suffixTree[n] = dict()
			self.suffixTree[n]['total'] = 0
			self.songIDLicks[n] = dict() #create dictionary of songIDs for specific licks

		self.keyDistribution = collections.defaultdict(collections.Counter)
			#are certain progressions confined to specific keys?


		for theSongID, theSong in self.songs.items():

			mList = theSong.chordsFlat
			# Build suffix tree
			songID = str(theSong.songID)
			
			for n in range(1, self.treeDepth+1):
				# suffix tree
	
				for loc in range(len(mList)):
					if loc >= (len(mList) - n + 1): 
						break #n is length of unit (ngram); must start n-gram with enough room to account for all
					longNgram = transToC(mList[loc:loc+n]) #make an ngram, transposes to C based on first chord of progression
					ngram = list()
					ngramForm = set()
					for i in longNgram: #separates form information from chords in ngram, creates ngram without form information. Creates chord form list.
						if i == '>S' or i == '>E':
							chord = i
						else:
							if i[-1] not in ngramForm:
								ngramForm.add(i[-1])   
							chord = i[0:-1]
						ngram.append(chord)
					ngramForm = list(ngramForm) 
					prefix = tuple(ngram[0:-1]) #prefix = all but the last element of ngram
					suffix = tuple([ngram[-1]]) #suffix = last element of ngram
					if prefix not in self.suffixTree[n]: #create prefix entry if not in dictionary
						self.suffixTree[n][prefix] = dict() #tallies number of times that the suffix follows this prefix
						self.suffixTree[n][prefix]['total'] = 0 
						self.songIDLicks[n][prefix] = dict()
					if suffix in self.suffixTree[n][prefix]:
						self.suffixTree[n][prefix][suffix] += 1 #adds one to number of times suffix follows the prefix
						#script to encode the formal part in which a chord occurs
						f = len(ngramForm)
						for f in ngramForm:
							self.songIDLicks[n][prefix][suffix].add(songID + str(f))
					else:
						self.suffixTree[n][prefix][suffix] = 1 
						self.songIDLicks[n][prefix][suffix] = set()
						f = len(ngramForm)
						for f in ngramForm:
							self.songIDLicks[n][prefix][suffix].add(songID + str(f))
					self.suffixTree[n][prefix]['total'] += 1 
								
					self.suffixTree[n]['total'] += 1
		
					# tally modal distribution of lick
					
					#self.keyDistribution[ngram][theSong.begTonic] += 1 #adds ngram to dictionary of tonics
		
		#write pickle
		cPickle.dump(self.songs, open(pickleFilename,'w'), protocol=cPickle.HIGHEST_PROTOCOL)
		sys.stderr.write(str(time.clock()-start) + ' secs\n')

	def traverseSuffixTree ( self, lick, chainLength, outputList ):
		#traverse through suffix tree (built above)
		

		def suffixProb ( lick ): #probability that, given the first n-1 elements of lick, the last element will follow (when n is the number of elements of lick)
			n = len(lick) #determines number of chords in the lick
			branch = self.suffixTree[n][lick[0:-1]] #identifies the lick elements from first to last (the last then becomes the "suffix")
#			  print lick, lick[-1], branch
			return branch[(lick[-1],)] * 1. / branch['total'] #finds total number of times last element of lick appears,  multiplies by 1/total branches
			
		def suffixEntropy ( lick ): #treats whole lick as prefix; calculates the entropy of the distribution of all possible suffixes (after lick, suffix is NOT part of lick)
			n = len(lick) + 1
			H = 9.99 #set ceiling on H (entropy)
			if n > 1 and n <= self.treeDepth and lick[-1] != '>E':
				#prevents calculation if tree doesn't have enough levels or if endtoken (hence H would be 9.99)
				H = 0. #reset entropy at 0
				branch = self.suffixTree[n][lick]
				#calculate entropy for all possible cases of suffixes following this lick
				for leaf in branch:
					if leaf == 'total': continue
					P = branch[leaf] * 1. / branch['total']
					H -= P * math.log(P, 2)
#				 print '{:3f} {:45}	 {:10}	{}'.format(H, lick[0:-1], leaf, branch)
			return H

		n = len(lick) 
		theSuffixEntropy = suffixEntropy(lick) #again: suffix used to calculate entropy is the event AFTER lick (not part of lick)
		
		sortString = '' 
		for i in reversed(lick):
			sortString += i
	
		hashes = ''
		#OUTPUT TABLE OF CHORD PROGRESSIONS	 
		#output = row of ngram (lick) + parameters
		output = list()
		####how many times does a lick happen?
		output.append(self.suffixTree[n][lick[0:-1]][lick[-1:]]) 
		####how many chords are in a lick?
		output.append(len(lick)) 
		#####output the chords in lick
		for c in lick: output.append(c)	 
		#####empty cells for alignment
		for i in range(n,self.treeDepth-1): output.append('')
		#####resulting entropy at end of lick (treats lick as prefix)
		output.append(theSuffixEntropy) 
		
		##################################
		###HASHES#########################
		#If probability of last event in lick is less than 0.5 given the first n-1 elements of the lick, set chainLength to 0 (THUS: WITHIN LICK, no elements after included)
		if suffixProb(lick) < .5: chainLength = 0
		#####If the entropy after last element of the lick is less than set threshold (minus .3), chainLength will increase by 1 (THUS: refers to entropy AFTER LICK)
		if theSuffixEntropy < self.entropyThreshold - .3: 
			chainLength += 1 #thus: if we have low entropy following lick (AKA high certainty of what event will follow), then add 1 (which will turn into a hash)
		if chainLength != 0 and theSuffixEntropy >= self.entropyThreshold: 
			#if chainlength has other value than zero AND entropy after the lick is larger than the set threshold 
			if theSuffixEntropy >= self.entropyThreshold: 
				for i in range(chainLength): #number of hashes is telling me what the chainLength is for a particular lick
					hashes += '#' 
			chainLength = 0 #starts at zero
		output.append(hashes)
		####################################  
		##Output progression: 
		if hashes != '':
			
			####CASE ID####
			self.suffixTreeCounter += 1
			output.append(self.suffixTreeCounter)
			
			####FIND LOOPING PROGRESSIONS####
			lickLen = len(lick)
			for i in range(1, lickLen - 1):
				testLoop = lick[0:i+1] #find loop to test as subset
				loopLen = len(lick[0:i+1]) #find test loop length
				testVal = int(lickLen/loopLen) #find divisor, rounded down 
				testValRem= lickLen%loopLen #find remainder
				if lick == (testLoop * testVal) + testLoop[0:testValRem]: # if lick = a multiple of the loop (including remainder), then loop is valid loop 
					loop = lick[0:i+1]
					repeats = round(lickLen/float(loopLen), 2)
					if self.maxLoopLen < len(loop):
						self.maxLoopLen = len(loop)
					break
				else:
					loop = lick
					repeats = 1
					if self.maxLoopLen < len(loop):
						self.maxLoopLen = len(loop)
			#APPEND ALL INFORMATION FROM LOOPS		
			output.append(loop)	 
			output.append(repeats)
			#####ABSTRACTION OF LOOP CHORDS #####
			prevRoot = str() #dummy variable to keep track of previous chord root
			for i in range (0, len(loop)): #iterate through chords in loop
				testChord = str(loop[i]) #turn chord tuple into string for finding info
				#find accidentals in chord root
				accIndex1 = testChord.rfind('-') 
				accIndex2 = testChord.rfind('#')
				if accIndex1 > -1: #if chord root contains flats, find quality after
					chordBeat = testChord[0]
					chordRoot = testChord[1:accIndex1+1]
					chordQual = testChord[accIndex1+1:]
					prevRoot = chordRoot
				elif accIndex2 > -1: #if chord root contains sharp, find quality after
					chordBeat = testChord[0]
					chordRoot = testChord[1:accIndex2+1]
					chordQual = testChord[accIndex2+1:]
					prevRoot = chordRoot
				else: #if chord root contains neither, find quality after root name
					chordBeat = testChord[0]
					chordRoot = testChord[1]
					chordQual = testChord[2:]
					prevRoot = chordRoot
				#find distance interval from previous chord 
				if prevRoot == '': #if no previous chord, distance = 0
					chordDist = ''
					prevRoot = chordRoot
				else:	
					y = int(pitchClassTranslate[chordRoot]) 
					print y
					x = int(pitchClassTranslate[prevRoot]) 
					print x
					chordDist = (y - x) % 12 #find interval distance mod 12
					print chordDist
					prevRoot = chordRoot
				chordAbst = chordQual + '_' + chordBeat
				output.append(chordDist) #append chord distance from previous chord 
				output.append(chordAbst) #append chord abstraction	 
			#####empty cells for alignment#######
			for i in range(len(loop), 2*self.treeDepth): output.append('')

			####Song IDs (of those containing licks) added to spreadsheet
			lickSongs = set()
			songsCounter = set() #keeps track of total songs for lick (including duplicates)
			dupSongs = set() #keeps track of total duplicated songs
			songForms = set() #keeps track of form letters
			for s in sorted(self.songIDLicks[n][lick[0:-1]][lick[-1:]]):
				#split songID from the formal marker
				sID = s[:-1]
				sForm = s[-1:]
				songsCounter.add(sID)
				#identify if song is a duplicate using RockPop-DupSongID.csv
				if sID in dupSongID:
					sName = str(dupSongID[sID])
					songID = sName + sForm
					sDups = str.split(dupSongOthers[sName], '_') #find other duplicates corresponding to song (using translated named) 
					dups = set(sDups)
					dupSongs.update(dups) #add song duplicates to duplicates set
				else:
					songID = sID + sForm
				songForms.add(sForm)
				lickSongs.add(str(songID))
			totalSongs = len(songsCounter)
			totalNonDupSongs = totalSongs - len(dupSongs) 
			###APPEND: Song number + form, number of songs, number of songs without dups, distinct song forms
			output.append(totalSongs)
			output.append(totalNonDupSongs)
			
			#### FIGURE OUT HOW TO ITERATE THROUGH THESE SETS. ALSO DON'T FORGET TO 
			####APPEND BLANK SPACES IN BETWEEN
			for y in range(1, len(lickSongs)):
				output.append(lickSongs[y])
			for x in range(1, len(songForms)):
				output.append(songForms[x])
			#####Output Progression Chords (Sorted backward)
			output.append('_'+sortString)
						
			# calculate entropy of this lick's distribution over selected modes

			# NOTE: this currently ignores any transposed or "capitalized" mode
						
			#tonicEntropy = 0
			#total = 0
			#for m in self.modeFilter:		
			#	 total += self.keyDistribution[lick][m]
			# for m in self.modeFilter:
#				  p = self.keyDistribution[lick][m] * 1. / total
#				  if p != 0: tonicEntropy -= p * math.log(p)
#			  output.append(tonicEntropy)
#			  output.append(str(self.keyDistribution[lick]))
			
			outputList.append(output) #row is only appended to the table if the row has hashes (otherwise, the row is thrown out)
		if lick[-1] == '>E' or n+1 == self.treeDepth: return 
		#only time we stop running this function is if A) we reach an end token or B) the tree is filled up (determined by treeDepth variable and length of lick (n))
		for suffix in sorted(self.suffixTree[n+1][lick]): #goes through the sorted suffixes for a given lick
			if suffix == 'total': continue 
			if self.suffixTree[n+1][lick][suffix] >= self.countThreshold:  #If the count of licks given a specific suffix is greater than the threshold, then the function will continue running
					self.traverseSuffixTree ( lick + suffix, chainLength, outputList )	#calls itself until it can't anymore
		
	def listLicks (self): #creates your output list and starts the suffix tree traversal
		outputList = list()
		self.suffixTreeCounter = 0 ###Set counter for CASE IDs of progressions
		self.maxLoopLen = 0 ###Set counter for maximum loop length
		for note in sorted(self.suffixTree[2]):
			if note == 'total': continue
			self.traverseSuffixTree(note, 0, outputList)
		return outputList 
		