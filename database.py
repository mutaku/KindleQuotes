#!/usr/bin/env python
#	Database interactions
# -*- coding: utf_8 -*-
    
from pysqlite2 import dbapi2 as sqlite
import hashlib


def setup(dbname):
    '''Setup the database and tables for a new profile.'''  
    connection = sqlite.connect(dbname)
    cursor = connection.cursor()
    
    booksTable = '''CREATE TABLE books (
                    id VARCHAR(56)  UNIQUE NOT NULL PRIMARY KEY,
                    title VARCHAR(255)  NULL,
                    author VARCHAR(100)  NULL
                )'''
    cursor.execute(booksTable)
    connection.commit()
    
    clipsTable = '''CREATE TABLE clips (
                    id INTEGER  UNIQUE NOT NULL PRIMARY KEY,
                    book VARCHAR(56)  NULL,
                    location INTEGER  NULL,
                    entry_header VARCHAR(255)  NULL,
                    hash_id VARCHAR(56)  NULL,
                    quote BLOB  NULL
                )'''
    cursor.execute(clipsTable)
    connection.commit()
    
    cursor.close()
    connection.commit()
    connection.close()


def dump(db, data, line_ending):
    '''
    Input data into the database on a fresh parse.
            table setup: id | book (book_hash_id to match book table id)* | location* | entry_header*^ | hash_id* | quote*^
                    * inserted by us	^ pickled object
                            pickle the dirty data
            iterate over all the entries for each book and check the hash_id to make sure not previously inserted and if not dump it
            also break up the book title into title and author and create a hash_id_book to dump as the id for that table
            book table setup: book_hash_id* | title*^ | author*^
                    * inserted by us	^ pickled object
    '''
    connection = sqlite.connect(db)
    cursor = connection.cursor()
    
    connection.text_factory = str
    
    error = []

    for k in data:
        book_hash_id = hashlib.sha224(k).hexdigest()
        if "(" in k:
            book_string = k.rpartition("(")
            book_title = book_string[0]
            book_author = book_string[2].rstrip(''.join([")",line_ending]))
        else:
            book_title = k
            book_author = "NULL"
        
        book_check = []
        try:
            sql = "SELECT title FROM books WHERE id=?"
            cursor.execute(sql, (book_hash_id,))
            book_check = cursor.fetchone()
        except connection.Error, err:
            e = "Error: %s" % err.args[0]
            error.append(e)

        if not book_check:
            try:
                sql = "INSERT INTO books VALUES(?,?,?)"
                cursor.execute(sql, (book_hash_id, book_title, book_author,))
                connection.commit()
            except connection.Error, err:   
                e = "Error: %s" % err.args[0]
                error.append(e)

        the_keys = sorted(data[k].iterkeys())
        for e in the_keys:
            entry_header = data[k][e][1]
            location = int(data[k][e][0])
            hash_id = e
            
            if len(data[k][e])>2:
                quote = data[k][e][2]
            else:
                quote = "NULL"

            quote_check = []
            try:
                sql = "SELECT id FROM clips WHERE hash_id LIKE ?"
                cursor.execute(sql, (hash_id,))
                quote_check = cursor.fetchone()
            except connection.Error, err:
                e = "Error: %s" % err.args[0]
                error.append(e)
        
            if not quote_check:
                sql = "INSERT INTO clips VALUES(null,?,?,?,?,?)"
                try:
                    cursor.execute(sql, (book_hash_id, location, entry_header, hash_id,quote,))
                    connection.commit()
                except connection.Error, err:
                    e = "Error: %s" % err.args[0]
                    error.append(e)

    cursor.close()
    connection.commit()
    connection.close()

    return error


class Retrieve():
    '''Grab database data.'''
    def __init__(self, db):
        self.connection = sqlite.connect(db)
        self.cursor = self.connection.cursor()
        
        self.connection.text_factory = str
        
        self.error = []

    def books(self):
        '''Get all books.'''
        try:
            sql = "SELECT * FROM books"
            self.cursor.execute(sql)
            data = self.cursor.fetchall()
            return data
        except self.connection.Error, err:   
            e = "Error: %s" % err.args[0]
            self.error.append(e)

    def quotes(self, book=None):
        '''Get quotes for a selected book id.'''
        try:
            sql = "SELECT * FROM clips WHERE book=?"
            self.cursor.execute(sql, (book,))
            data = self.cursor.fetchall()
            return data
        except self.connection.Error, err:   
            e = "Error: %s" % err.args[0]
            self.error.append(e)  


class Search():
    '''Search database for string.'''
    def __init__(self, db, b_id, s):
        connection = sqlite.connect(db)
        cursor = connection.cursor()
        
        connection.text_factory = str
        
        self.error = []
        
        self.query_list = s.split(" ")
        array = list(s.replace(" ", "%"))
        array[:0] = "%"
        array.append("%")
        query_string = "".join(array)
        
        try:
            sql = "SELECT * FROM clips WHERE quote LIKE ? and book=?"
            cursor.execute(sql, (query_string, b_id,))
            self.clips = cursor.fetchall()
        except connection.Error, err:   
            e = "Error: %s" % err.args[0]
            self.error.append(e)   
    
        self.book_ids = []
        for c in self.clips:
            if c[1] not in self.book_ids:
                self.book_ids.append(c[1])
        
        try:
            self.books = []
            for i in self.book_ids:
                sql = "SELECT * FROM books WHERE id=?"
                cursor.execute(sql, (i,))
                self.books.append(cursor.fetchone())
        except connection.Error, err:   
            e = "Error: %s" % err.args[0]
            self.error.append(e)
