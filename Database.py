#!/usr/bin/env python
#	Database interactions
# -*- coding: utf_8 -*-
    
from pysqlite2 import dbapi2 as sqlite
import hashlib


def setup(dbname):
    '''Setup the database and tables for a new profile'''
    
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
    '''Input data into the database on a fresh parse
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
        
        book_dupe = []
        try:
            sql = "SELECT * FROM books WHERE id = ?"
            cursor.execute(sql,(book_hash_id,))
            cursor.fetchone()
            for d in cursor:
                book_dupe.append(d)
        except connection.Error, err:
            e = "Error: %s" % err.args[0]
            error.append(e)
        
        if len(book_dupe)<1:
            try:
                sql = "INSERT INTO books VALUES(?,?,?)"
                cursor.execute(sql,(book_hash_id,book_title,book_author,))
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
            
            entry_dupe = []
            try:
                sql = "SELECT id FROM clips WHERE hash_id LIKE ?"
                cursor.execute(sql,(hash_id,))
                cursor.fetchone()
                for d in cursor:
                    entry_dupe.append(d)
            except connection.Error, err:
                e = "Error: %s" % err.args[0]
                error.append(e)
        
            if len(entry_dupe)>0:
                pass
            else:
                sql = "INSERT INTO clips VALUES(null,?,?,?,?,?)"
                try:
                    cursor.execute(sql,(book_hash_id,location,entry_header,hash_id,quote,))
                    connection.commit()
                except connection.Error, err:
                    e = "Error: %s" % err.args[0]
                    error.append(e)

    cursor.close()
    connection.commit()
    connection.close()

    return error