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

# test functionality for now
def testRun():
    global root
    
    root = Tk()
    root.title('KindleQuotes')
    root.config(bg="#666666")
    
    highlights = getFile("Select Kindle Highlights file: ", 'high')
    database = getFile("Select profile: ", 'db')
    
    p = Parser.parse(highlights, database)
    
    return p.doHTML()
    
if __name__ == '__main__':
    testRun()