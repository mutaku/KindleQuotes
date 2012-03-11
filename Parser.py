#!/usr/bin/env python
#	take the clippings file from kindle and parse out into database
# -*- coding: utf_8 -*-

from pysqlite2 import dbapi2 as sqlite
import Database
import re
import hashlib

class parse():
	''' do the initial raw parse and split up everything by books by looking for the main entry dividers (=== etc)
		we also use some email regex to snipe out any personal emails (amazon whisper conversions) and replace with a string
	'''

	def __init__(self, f, db):
		'''parse over raw dictionary and split up entries by looking for the entry starters (_prefix)
			we will split by book and then store by the hashed id
			the hash_id is created from the header of each entry to make a unique entry id 
				we use sha224->hexdigest of the entire header portion (the "_prefix location | date" portion)
				the hash_id is looked for before dumping each quote into the database and if found is merely skipped
		'''
		
		self.db = db
		self.f = open(f, 'r').readlines()
		self.error = []
		
		self.clips = {}
		n = 0
		for line in self.f:
			line = re.sub(r'[\w\-][\w\-\.]+@[\w\-][\w\-\.]+[a-zA-Z]{1,4}', "__email generated __", line)
			if n == 0:
				if line not in self.clips:
					self.clips[line] = list()
				self.this_title = line
				n = 1
			else:
				if line ==  '==========\r\n':
					n = 0
					pass
				elif line != '\r\n':
					self.clips[self.this_title].append(line)
		

		self.clean_clips = {}
		n = 0
		h_prefix = "- Highlight"
		n_prefix = "- Note"
		b_prefix = "- Bookmark"
		for k in self.clips:
			self.clean_clips[k] = dict()
			for line in self.clips[k]:
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
		'''directly dump an html version for testing'''
		
		for k in self.clean_clips:
			print "<div class=book>",k
			the_keys = sorted(self.clean_clips[k].iterkeys())
			for e in the_keys:
				print "<p class=entry>",self.clean_clips[k][e][1],"</p>"
				if len(self.clean_clips[k][e])>2:
					print "<p class=quote>",self.clean_clips[k][e][2],"</p>"
			print "</div>"


	def dbDUMP(self):
		''' dump into the database'''

		Database.dump(self.db, self.clean_clips)
