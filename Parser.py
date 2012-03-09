#!/usr/bin/env python
#	take the clippings file from kindle and parse out into database

from pysqlite2 import dbapi2 as sqlite

class parse():
	''' do the initial raw parse and split up everything by books by looking for the main entry dividers (=== etc)
		we also use some email regex to snipe out any personal emails (amazon whisper conversions) and replace with a string
	'''

	def __init__(self, f, db, html=False):
		'''parse over raw dictionary and split up entries by looking for the entry starters (_prefix)
			we will split by book and then store by the hashed id
			the hash_id is created from the header of each entry to make a unique entry id 
				we use sha224->hexdigest of the entire header portion (the "_prefix location | date" portion)
				the hash_id is looked for before dumping each quote into the database and if found is merely skipped
		'''
		
		self.db = db
		self.error = []
		
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
		

		self.clean_clips = {}
		n = 0
		h_prefix = "- Highlight"
		n_prefix = "- Note"
		b_prefix = "- Bookmark"
		for k in clips:
			self.clean_clips[k] = dict()
			for line in clips[k]:
				if line.startswith(h_prefix) or line.startswith(n_prefix) or line.startswith(b_prefix):
					n = 0
				else:
					n = 1
				if n == 0:
					this_entry = line
					this_loc = int(this_entry.split('Loc.')[1].strip().split('-')[0].split(' ')[0])
					this_id = hashlib.sha224(line).hexdigest()
					self.clean_clips[k][this_id] = list()
					self.clean_clips[k][this_id].append(this_loc)
					self.clean_clips[k][this_id].append(this_entry)
					
				else:
					self.clean_clips[k][this_id].append(line)
					n = 0


	def doHTML(self):
		'''directly dump an html version for testing
			we only run if DB_DUMP is set to zero
		'''
		for k in self.clean_clips:
			print "<div class=book>",k
			the_keys = sorted(self.clean_clips[k].iterkeys())
			for e in the_keys:
				print "<p class=entry>",self.clean_clips[k][e][1],"</p>"
				if len(self.clean_clips[k][e])>2:
					print "<p class=quote>",self.clean_clips[k][e][2],"</p>"
			print "</div>"


	def dbDUMP(self):
		''' dump into the database
			we only run if DB_DUMP is set to one
			table setup: id | book (book_hash_id to match book table id)* | location* | entry_header*^ | hash_id* | quote*^
				* inserted by us	^ pickled object
					pickle the dirty data
			iterate over all the entries for each book and check the hash_id to make sure not previously inserted and if not dump it
			also break up the book title into title and author and create a hash_id_book to dump as the id for that table
			book table setup: book_hash_id* | title*^ | author*^
				* inserted by us	^ pickled object
		'''

		connection = sqlite.connect(db)
		cursor = connnection.cursor()

		for k in self.clean_clips:
			book_hash_id = hashlib.sha224(k).hexdigest()
			if "(" in k:
				book_string = k.rpartition("(")
				book_title = book_string[0]
				book_author = book_string[2].rstrip(")\r\n")
			else:
				book_title = k
				book_author = "NULL"
			
			try:
				sql = "SELECT * FROM books WHERE id=?"
				cursor.execute(sql,(book_hash_id))
				cursor.fetchone()
				book_dupe = []
				for d in cursor:
					book_dupe.append(d)
			except connection.Error, err:
				e = "Error: %s" % err.args[0]
				self.error.append(e)
			
			if len(book_dupe)<1:
				try:
					sql = "INSERT INTO books VALUES(?,?,?)"
					cursor.execute(sql,(book_hash_id,book_title,book_author))
				except connection.Error, err:
					e = "Error: %s" % err.args[0]
					self.error.append(e)

			the_keys = sorted(self.clean_clips[k].iterkeys())
			for e in the_keys:
				entry_header = self.clean_clips[k][e][1]
				location = int(self.clean_clips[k][e][0])
				hash_id = e
				if len(self.clean_clips[k][e])>2:
					quote = self.clean_clips[k][e][2]
				else:
					quote = "NULL"
				try:
					sql = "SELECT id FROM clips WHERE hash_id like ?"
					cursor.execute(sql,(hash_id))
					cursor.fetchone()
					entry_dupe = []
					for d in cursor:
						entry_dupe.append(d)
				except connection.Error, err:
					e = "Error: %s" % err.args[0]
					self.error.append(e)

				if len(entry_dupe)>0:
					pass
				else:
					sql = "INSERT INTO clips VALUES(null,?,?,?,?,?)"
					try:
						cursor.execute(sql,(book_hash_id,location,entry_header,hash_id,quote))
					except connection.Error, err:
						e = "Error: %s" % err.args[0]
						self.error.append(e)
