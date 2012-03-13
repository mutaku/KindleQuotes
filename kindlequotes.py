#!/usr/bin/env python
#	KindleQuotes - xiao_haozi@mutaku.com - http://mutaku.com
# -*- coding: utf_8 -*-

from Tkinter import *
import tkFileDialog
import clippingparser
import database


class Profile():
    '''Profile attribute holder.'''
    def __init__(self):
        pass


def getFile(title, t):
    '''Ask for respective file.'''
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
    '''Establish a new profile and setup the tables appropriately.'''
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
    
    profile.database = name
    profile_label['text'] = profile.database


def selectProfile():
    '''Get profile.'''
    profile.database = getFile("Select profile: ", 'db')
    profile_label['text'] = profile.database

def run():
    '''Get clippings file and database, run parser, and dump into database.'''
    profile.highlights = getFile("Select Kindle Highlights file: ", 'high')

    if not hasattr(profile, 'database'):
        selectProfile()
    
    p = clippingparser.Parse(profile.highlights, profile.database)
    
    p.database_dump()
    
    if p.error:
        print p.error
    else:
        print "success."

def do_search():
    search_str = search_entry.get().lower()
    
    if not hasattr(profile, 'database'):
        selectProfile()
    
    s = database.Search(profile.database, search_str)
    
    print s.clips

if __name__ == '__main__':

    profile = Profile()

    root = Tk()
    root.title('KindleQuotes')
    root.config(bg="#666")
    
    frame1 = Frame()
    frame1.config(bg="#666", padx=5, pady=5)
    frame1.grid(row=0)
    
    frame2 = Frame()
    frame2.config(bg="#666", padx=5, pady=5)
    frame2.grid(row=1)
    
    profile_label = Label(frame1, text="Create or Select a profile.", bg="#666", fg="#ccc")
    profile_label.grid(row=0, column=0, columnspan=3)    
    Button(frame1, command=setupProfile, text="Setup Profile").grid(row=1, column=0)
    Button(frame1, command=run, text="Update Profile").grid(row=1, column=2)
    Button(frame1, command=selectProfile, text="Choose Profile").grid(row=1, column=1)
    
    search_entry = StringVar()
    search_box = Entry(frame2, textvariable=search_entry, fg="#000", bg="#ccc").grid(row=0, column=0, columnspan=2)
    Button(frame2, command=do_search, text="Search Quotes").grid(row=0, column=2)
    
    root.mainloop()
