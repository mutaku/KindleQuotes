#!/usr/bin/env python
#	KindleQuotes - xiao_haozi@mutaku.com - http://mutaku.com

from Tkinter import *
import tkFileDialog
import Parser


def getFile(title, t):
    options = {
        'parent' : root,
        'title' : title
    }
    
    ftypes = {
        'high' : ['Kindle Highlights','.txt'],
        'db' : ['Sqlite3 DB','.s3db']
    }
    
    options['filetypes'] = [(ftypes[t][0],ftypes[t][1])]
    
    return tkFileDialog.askopenfilename(**options)
    

def setupProfile():
    # instead of a save-as, could just prompt for a name in a tkinter entry then store in ~/.KindleQuotes
    options = {
        'parent' : root,
        'title' : 'Choose a Profile Name to save as: ',
        'filetypes' : [('Sqlite3 DB','.s3db')]
    }
    
    name = tkFileDialog.asksaveasfilename(**options)
    
    from pysqlite2 import dbapi2 as sqlite
    
    connection = sqlite.connect(name)
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


# test functionality for now
def testRun():
    global root
    
    root = Tk()
    root.title('KindleQuotes')
    root.config(bg="#666666")
    
    setupProfile()
    
    highlights = getFile("Select Kindle Highlights file: ", 'high')
    database = getFile("Select profile: ", 'db')
    
    p = Parser.parse(highlights, database)
    
    return p.doHTML()
    
if __name__ == '__main__':
    testRun()