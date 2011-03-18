#!/usr/bin/env python
# kindlequotes - 
#	take the clippings file from kindle and parse out into database
#	version 0.2	2-14-2011 xiao_haozi

import sys,os,re,hashlib,MySQLdb,pickle


# This variable sets the stage for what to do with the parsed data
#	if not set, we will spit out html that can be piped to a file for testing purposes
#	if this is set, we will not spit out html and instead dump to the database
#		remember we don't everwrite anything (see hash_id code and explanation below)
############################################################
DB_DUMP = 1	# 0 = spit out html, 1 = dump to the database
############################################################

# FILL IN THESE VARIABLES TO MATCH YOUR DATABASE
DB_HOST = ""
DB_USER = ""
DB_PASSWD = ""
DB_DATABASE = ""

# error display  -- display error message and kill itself
def error(msg):
	print 
	print msg
	print
	exit()

# make sure the DB_DUMP variable is appropriately set
if DB_DUMP not in range(0,2):
	e = "DB_DUMP variable must be set to either 0 or 1 ... please fix."
	error(e)

# establish the database connection for dumping
global connection, cursor
try:
	connection = MySQLdb.connect(host = DB_HOST, user = DB_USER, passwd = DB_PASSWD, db = DB_DATABASE)
	cursor = connection.cursor()
except MySQLdb.Error, e:
	e = "Error %d: %s" % (e.args[0], e.args[1])
	error(e)

# read in the file from the command-line --simple only looks for the first argument
try:
	to_open = sys.argv[1]
	f = open(to_open,'r').readlines()
except:
	e = "Problem opening file."
	error(e)

# do the initial raw parse and split up everything by books by looking for the main entry dividers (=== etc)
#	we also use some email regex to snipe out any personal emails (amazon whisper conversions) and replace with a string
clips = {}
n = 0
for line in f:
	line = re.sub(r'[\w\-][\w\-\.]+@[\w\-][\w\-\.]+[a-zA-Z]{1,4}', "__email generated __", line)
	if n == 0:
		if line not in clips:
			clips[line] = list()
		this_title = line
		n = 1
	else:
		if line ==  '==========\r\n':
			n = 0
			pass
		elif line != '\r\n':
			clips[this_title].append(line)

# parse over raw dictionary and split up entries by looking for the entry starters (_prefix)
#	we will split by book and then store by the hashed id
#	the hash_id is created from the header of each entry to make a unique entry id 
#		we use sha224->hexdigest of the entire header portion (the "_prefix location | date" portion)
#		the hash_id is looked for before dumping each quote into the database and if found is merely skipped
clean_clips = {}
n = 0
h_prefix = "- Highlight"
n_prefix = "- Note"
b_prefix = "- Bookmark"
for k in clips:
	clean_clips[k] = dict()
	for line in clips[k]:
		if line.startswith(h_prefix) or line.startswith(n_prefix) or line.startswith(b_prefix):
			n = 0
		else:
			n = 1
		if n == 0:
			this_entry = line
			this_loc = int(this_entry.split('Loc.')[1].strip().split('-')[0].split(' ')[0])
			this_id = hashlib.sha224(line).hexdigest()
			clean_clips[k][this_id] = list()
			clean_clips[k][this_id].append(this_loc)
			clean_clips[k][this_id].append(this_entry)
			
		else:
			clean_clips[k][this_id].append(line)
			n = 0

# directly dump an html version for testing
#	we only run if DB_DUMP is set to zero
if DB_DUMP == 0:
	for k in clean_clips:
		print "<div class=book>",k
		the_keys = sorted(clean_clips[k].iterkeys())
		for e in the_keys:
			print "<p class=entry>",clean_clips[k][e][1],"</p>"
			if len(clean_clips[k][e])>2:
				print "<p class=quote>",clean_clips[k][e][2],"</p>"
		print "</div>"

# dump into the database
#	we only run if DB_DUMP is set to one
#	table setup: id | book (book_hash_id to match book table id)* | location* | entry_header*^ | hash_id* | quote*^
#		* inserted by us	^ pickled object
#			pickle the dirty data
#	iterate over all the entries for each book and check the hash_id to make sure not previously inserted and if not dump it
#	also break up the book title into title and author and create a hash_id_book to dump as the id for that table
#	book table setup: book_hash_id* | title*^ | author*^
#		* inserted by us	^ pickled object
elif DB_DUMP == 1:
	for k in clean_clips:
		book_hash_id = hashlib.sha224(k).hexdigest()
		if "(" in k:
			book_string = k.rpartition("(")
			book_title = pickle.dumps(book_string[0])
			book_author = pickle.dumps(book_string[2].rstrip(")\r\n"))
		else:
			book_title = pickle.dumps(k)
			book_author = pickle.dumps("NULL")
		try:
			sql = "SELECT * FROM books WHERE id like %s"
			cursor.execute(sql,(book_hash_id))
			cursor.fetchone()
			book_dupe = []
			for d in cursor:
				book_dupe.append(d)
		except MySQLdb.Error, e:
			e = "Error %d: %s" % (e.args[0], e.args[1])
			error(e)
		if len(book_dupe)<1:
			try:
				sql = "INSERT INTO books VALUES(%s,%s,%s)"
				cursor.execute(sql,(book_hash_id,book_title,book_author))
			except MySQLdb.Error, e:
				e = "Error %d: %s" % (e.args[0], e.args[1])
				error(e)
		the_keys = sorted(clean_clips[k].iterkeys())
		for e in the_keys:
			entry_header = pickle.dumps(clean_clips[k][e][1])
			location = int(clean_clips[k][e][0])
			hash_id = e
			if len(clean_clips[k][e])>2:
				quote = pickle.dumps(clean_clips[k][e][2])
			else:
				quote = pickle.dumps("NULL")
			try:
				sql = "SELECT id FROM clips WHERE hash_id like %s"
				cursor.execute(sql,(hash_id))
				cursor.fetchone()
				entry_dupe = []
				for d in cursor:
					entry_dupe.append(d)
			except MySQLdb.Error, e:
				e = "Error %d: %s" % (e.args[0], e.args[1])
				error(e)
			if len(entry_dupe)>0:
				pass
			else:
				sql = "INSERT INTO clips VALUES(null,%s,%s,%s,%s,%s)"
				try:
					cursor.execute(sql,(book_hash_id,location,entry_header,hash_id,quote))
				except MySQLdb.Error, e:
					e = "Error %d: %s" % (e.args[0], e.args[1])
					error(e)
