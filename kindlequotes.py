#!/usr/bin/env python
#	KindleQuotes - xiao_haozi@mutaku.com - http://mutaku.com
# -*- coding: utf_8 -*-

from Tkinter import *
import tkFileDialog
import clippingparser
import database


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
        name = ''.join([name,'.s3db'])
    
    f = open(name, 'w')
    f.close()
    
    database.setup(name)


# test functionality for now
def new():

    setupProfile()
    

def run():
    
    highlights = getFile("Select Kindle Highlights file: ", 'high')
    database = getFile("Select profile: ", 'db')
    
    p = clippingparser.Parse(highlights, database)
    
    p.database_dump()
    
    print p.error


if __name__ == '__main__':

    root = Tk()
    root.title('KindleQuotes')
    root.config(bg="#666666")
    
    Button(root, command=new, text="Setup Profile").grid(row=0, column=0)
    Button(root, command=run, text="Update Profile").grid(row=0, column=1)
    
    root.mainloop()
