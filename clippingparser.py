#!/usr/bin/env python
#	take the clippings file from kindle and parse out into database
# -*- coding: utf_8 -*-

from pysqlite2 import dbapi2 as sqlite
import re
import hashlib
import platform
import database

class Parse():
	'''
	Do the initial raw parse and split up everything by books by looking for the main entry dividers (=== etc)
		we also use some email regex to snipe out any personal emails (amazon whisper conversions) and replace with a string.
	'''
	def __init__(self, f, db):
		'''parse over raw dictionary and split up entries by looking for the entry starters (_prefix)
			we will split by book and then store by the hashed id
			the hash_id is created from the header of each entry to make a unique entry id 
				we use sha224->hexdigest of the entire header portion (the "_prefix location | date" portion)
				the hash_id is looked for before dumping each quote into the database and if found is merely skipped
		'''
		self.db = db
		_f = open(f, 'r').readlines()
		self.error = []
		
		_machine = platform.system()
		if _machine == "Windows":
			self.line_ending = "\n"
		else:
			self.line_ending = "\r\n"
		
		_clips = {}
		_n = 0
		for line in _f:
			line = re.sub(r'[\w\-][\w\-\.]+@[\w\-][\w\-\.]+[a-zA-Z]{1,4}', "__email generated __", line)
			if _n == 0:
				if line not in _clips:
					_clips[line] = list()
				this_title = line
				_n = 1
			else:
				if line ==  ''.join(['==========',self.line_ending]):
					_n = 0
					pass
				elif line != self.line_ending:
					_clips[this_title].append(line)
		

		self.clean_clips = {}
		_n = 0
		_hPrefix = "- Highlight"
		_nPrefix = "- Note"
		_bPrefix = "- Bookmark"
		for k in _clips:
			self.clean_clips[k] = dict()
			for line in _clips[k]:
				if line.startswith(_hPrefix) or line.startswith(_nPrefix) or line.startswith(_bPrefix):
					_n = 0
				else:
					_n = 1
				if _n == 0:
					this_entry = line
					this_loc = int(this_entry.split('Loc.')[1].strip().split('-')[0].split(' ')[0])
					this_id = hashlib.sha224(line).hexdigest()
					self.clean_clips[k][this_id] = list()
					self.clean_clips[k][this_id].append(this_loc)
					self.clean_clips[k][this_id].append(this_entry)
					
				else:
					self.clean_clips[k][this_id].append(line)
					_n = 0


	def print_HTML(self):
		'''Print out parsed data in HTML format ready for CSS styling.'''
		for k in self.clean_clips:
			print "<div class=book>",k
			the_keys = sorted(self.clean_clips[k].iterkeys())
			for e in the_keys:
				print "<p class=entry>",self.clean_clips[k][e][1],"</p>"
				if len(self.clean_clips[k][e])>2:
					print "<p class=quote>",self.clean_clips[k][e][2],"</p>"
			print "</div>"


	def database_dump(self):
		'''Dump parsed data into the appropriate database.'''
		d = database.dump(self.db, self.clean_clips, self.line_ending)
		self.error.append(d)
