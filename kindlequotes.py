#!/usr/bin/env python
#	KindleQuotes - xiao_haozi@mutaku.com - http://mutaku.com

from Tkinter import *
import tkFileDialog
import Parser
import Database


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
    if not name.endswith('.s3db'):
        name = name+'.s3db'
    
    f = open(name, 'w')
    f.close()
    
    Database.setupTables(name)


# test functionality for now
def testRun():

    setupProfile()
    
    highlights = getFile("Select Kindle Highlights file: ", 'high')
    database = getFile("Select profile: ", 'db')
    
    p = Parser.parse(highlights, database)
    
    p.dbDUMP()
    
    
if __name__ == '__main__':

    root = Tk()
    root.title('KindleQuotes')
    root.config(bg="#666666")
    
    testRun()