'''
textgrid.py

Purpose: to read in TextGrid files 
    (which are created with Praat for annotation of sound files)

Output: object which is a dictionary of dictionaries (Python object type), with the following key-value pairs (typically)
    object
        main
            Object class    = "TextGrid" (usually)
            File type        = "ooTextFile" (if TextGrid saved in long format; if saved in shortened format, this script will not work)
            xmin            = start time of the whole sound file (usually zero)
            xmax            = end time of the whole sound file (if xmin was zero, then xmax is the length of the sound file)
            size            = number of tiers in this TextGrid (digit as string) 
            
        item
            1                (item#)
                xmin        =interval start time (msec, as string of digits)
                xmax        =interval end time
                class        e.g. "Interval Tier"
                name        =name of [item#]'th tier
                intervals
                    1        interval 1 in tier 1
                        xmin
                        xmax
                        text    =text that was typed into this interval. = empty string ('') if nothing there
                        
                
                
            
            
     
Created on Aug 6, 2012

@author: Scott Hajek
'''

import os
import re


def textgrid_to_dict(filepath):

    # read in file
    f = open(filepath)
    lines = f.readlines()
    
    # create RegExObjects to be used in later pattern matching
    parentRE = re.compile('(item|intervals)\s{0,1}\[{0,1}\]{0,1}:')  # e.g. 'item []:' or 'intervals: size = 3'
    nodeRE = re.compile('(item|intervals)\s+\[(\d+)\]:')  # e.g. 'item [2]:' or 'intervals [2]:'
    keyvalRE = re.compile('\s*=\s*')    # e.g. ' = ' as in 'xmax = 3.309'
    
    # Create data variable as dictionary with top-level key as 'main'
    data = {'main' : {}}
    
    # initialize variables to be first used within the FOR loop below
    parent=""
    itemindex = 0
    intervalindex = 0
#    embedlevel=0
    newitem = False
    newinterv = False
    newitemelement=False
    newintervelement=False
    linecount=0
    
    # FOR loop for each line of the input file
    for line in lines:
        linecount=linecount+1
        # If the line contains a node definition (e.g. item [3]: ) then get the node info (nodetuple = (nodename,index))
        if parentRE.search(line) != None:
            parentmatch = parentRE.search(line)
            parent = parentmatch.group(1)
            if parent=="item":
                data.update({"item":{}})  #["item"] = dict()
#                embedlevel = 1
                newitem = True
                (newinterv,newintervelement)=(False,False)
            elif parent=="intervals":
                data["item"][itemindex].update({"intervals" : {}})
#                embedlevel = 2
                newinterv = True
                (newitem,newitemelement)=(False,False)
            else:
                print "parent loop didn't work in input line # "+str(linecount)
        elif nodeRE.search(line) != None:
            nodetuple = nodeRE.search(line)
            if nodetuple.group(1)=="item":
                itemindex = int(nodetuple.group(2))
                data["item"].update({itemindex : {}})
                newitemelement=True
                (newinterv,newintervelement)=(False,False)
            elif nodetuple.group(1) =="intervals":
                intervalindex = int(nodetuple.group(2))
                data["item"][itemindex]['intervals'].update({intervalindex : {}})
                newintervelement=True
                (newitem,newitemelement)=(False,False)
            else:
                print "node loop didn't work, input line # "+str(linecount)
        elif len(keyvalRE.split(line))>1:
            keyval = keyvalRE.split(line)
            keyval = [s.strip() for s in keyval]
            kvdict = {keyval[0] : keyval[1]}
    
            if not (newitem or newitemelement or newinterv or newintervelement):
                data["main"].update(kvdict)
            elif newitemelement:  #itemindex > 0 and (intervalindex == 0 or newinterv):
                data["item"][itemindex].update(kvdict)
            elif newintervelement:  #(intervalindex > 0 and itemindex > 0)
                data["item"][itemindex]["intervals"][intervalindex].update(kvdict)
            else:
                print "problem in element part"
            if newinterv:
                newitem=False
                newitemelement=False
            if newitem:
                newinterv=False
                newintervelement=False
        else:
            print "Input line # "+str(linecount)+" ignored or unrecognized"
    print "\n\n"
    return data





def printtoFile(textgrids, outputDir):
	'''
	    Output intended to be ready for import into R
	    
	    Table of Main (each value of main in a separate column, headers being the keys)
	    
	        dirpath    filename    transcriber    'File type'    'Object class'    xmin    xmax    Ntiers(=size)
	    
	    Table of Item
	    
	        dirpath    filename    transcriber    TierNum(=itemNum)    TierName(=name)    intervalNum    xmin    xmax    text
	    
	    common key(s) between tables Item and Main would be 'filepath', 'filename', and 'transcriber' 
	    
	    Created on Aug 8, 2012
	    @author: Scott Hajek
	
	    Modified on August 16th, 2012
	    @authors: Scott Hajek and Nathan Couch
	
	    Changed to a function called by main.py
	
	    Added directory path, filename, and transcriber information to the output.
	'''

	#sets the directory where the output files will be saved to.
	if not os.path.exists(outputDir):
		os.makedirs(outputDir)
	
	#===============================================
	# creates the files for the output, with headers
	#===============================================

	# define item separator/delimiter
	t='\t'

	# creates headers for the description file
	f1 = open(outputDir + 'sound_file_desc', 'w')

	mainfieldsTuple = ('dirpath','filename','transcriber','File type','Object class','xmin', 'xmax', 'size')	

#	first=True
#	for d in mainfieldsTuple:
#	    if first:
#		f1.write(d)
#		first=False
#	    else:
#		f1.write(t + d)

	first = True
	for d in mainfieldsTuple:
		if not first: d = t+d
		else: first=False
		f1.write(d)
		

	f1.write("\n")

	# create headers for interval File
	f2 = open(outputDir + 'sound_file_intervals', 'w')

	itemfieldsTuple = ('dirpath','filename','transcriber','File type','tierName','intervNum','xmin','xmax','text')

#	first=True
#	for d in mainfieldsTuple:
#	    if first:
#		f1.write(d)
#		first=False
#	    else:
#		f1.write(t + d)

	for c in itemfieldsTuple:
		f2.write(c + t)

	f2.write("\n")

	for textgrid_path in textgrids:
		
		#retrieves filepath, filename, and transcriber
		fname = os.path.basename(textgrid_path)		
		fdir = os.path.dirname(textgrid_path)
		transPattern = re.search('bmp\.(\w+)\.TextGrid',fname)
		
		if transPattern:  # if there was a match to the pattern
			transcriber = transPattern.group(1)
		else:
			transcriber = 'BLANK'
		
		os.chdir(fdir)

		#passes the file to parseTextGrid, which returns a dictionary.
		dic = textgrid_to_dict(fname)

		#===============================================================================
		# Create Whole-sound-file descriptors table
		#===============================================================================

		for x in mainfieldsTuple:
			if x == 'dirpath':
				f1.write(fdir)
			elif x == 'filename':
				f1.write(t + fname)
			elif x == 'transcriber':
				f1.write(t + transcriber)
			else:
				f1.write(t + dic['main'][x])

		f1.write("\n")

		#===============================================================================
		# Interval data (aka 'item')
		#===============================================================================

		for i in range(1,len(dic['item'])+1):
			ith = dic['item'][i]
			name = ith['name']
			for j in range(1, len(ith['intervals']) + 1):
				jth = ith['intervals'][j]
				xmin = jth['xmin']
				xmax = jth['xmax']
				text = jth['text']
				f2.write(fdir + t + fname + t + transcriber + t + str(i) + t + name + t + str(j) + t + xmin + t + xmax + t + text + "\n")

	f1.close()
	f2.close()		



if __name__ == '__main__':
    # test out the function textgrid as defined above
    
    filepath = "/path/to/file.TextGrid"
    test = textgrid_to_dict(filepath)
