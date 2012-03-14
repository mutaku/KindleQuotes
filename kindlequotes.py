#!/usr/bin/env python
#	KindleQuotes - xiao_haozi@mutaku.com - http://mutaku.com
# -*- coding: utf_8 -*-

from Tkinter import *
import tkFileDialog
import TkTreectrl as treectrl
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


def retrieveData():
    '''Get Data for profile from database.'''
    d = database.Retrieve(profile.database)

    profile.books = d.books()
    updateBookList()


def updateBookList():
    '''Update the books listed in main display.'''
    msg_box.delete(0, END)

    for b in profile.books:
        entry = (b[2], b[1])
        msg_box.insert(END, *entry)



def selectProfile():
    '''Get profile.'''
    profile.database = getFile("Select profile: ", 'db')
    profile_label['text'] = profile.database
    
    retrieveData()


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
        retrieveData()
        print "success."


def do_search():
    search_str = search_entry.get().lower()
    
    if not hasattr(profile, 'database'):
        selectProfile()
    
    s = database.Search(profile.database, search_str)
    
    profile.books = s.books
    updateBookList()
    print s.clips


def get_book(sel):
    '''Open selected book.'''
    print sel

class Book():
    '''Book sorting.'''
    # THIS IS NOT CORRECT - Need to set this up properly when more lucid
    
    def __init__self():
        pass
    
    def author(self):
        '''Sort by Author[LAST].'''
        pass
    
    def title(self):
        '''Sort by Title.'''
        pass
    


if __name__ == '__main__':

    profile = Profile()

    root = Tk()
    root.title('KindleQuotes')
    
    menubar = Menu(root)
    
    main_menu = Menu(menubar, tearoff=0)
    main_menu.add_command(label="Exit", command=root.destroy)
    menubar.add_cascade(label="KindleQuotes", menu=main_menu)
    
    pro_menu = Menu(menubar, tearoff=0)
    pro_menu.add_command(label="Open/Switch Profile", command=selectProfile)
    pro_menu.add_command(label="New Profile", command=setupProfile)
    menubar.add_cascade(label="Profile", menu=pro_menu)

    sync_menu = Menu(menubar, tearoff=0)
    sync_menu.add_command(label="Sync Database", command=run)
    menubar.add_cascade(label="Sync", menu=sync_menu)

    book_menu = Menu(menubar, tearoff=0)
    book_menu.add_command(label="Sort by Author[LAST]", command=Book.author)
    book_menu.add_command(label="Sort by Title", command=Book.title)
    menubar.add_cascade(label="Books", menu=book_menu)
    
    root.config(bg="#666", menu=menubar)
    
    frame1 = Frame(root)
    frame1.config(bg="#666", padx=5, pady=10)
    frame1.grid(row=0)
    
    frame2 = Frame(root)
    frame2.config(bg="#666", padx=5, pady=10)
    frame2.grid(row=1)
    
    Label(frame1, text="Active Profile:", bg="#666", fg="#808080").grid(row=0, column=0, sticky=W)
    profile_label = Label(frame1, text="Create or Select a profile.", bg="#666", fg="#ccc")
    profile_label.grid(row=0, column=1, columnspan=4, sticky=E)
    
    search_entry = StringVar()
    search_box = Entry(frame1, textvariable=search_entry, fg="#000", bg="#ccc")
    search_box.grid(row=0, column=5, columnspan=4, sticky=W)
    Button(frame1, command=do_search, text="Search Quotes").grid(row=0, column=9, sticky=E)
    
    scroll_msg = Scrollbar(frame2, orient=VERTICAL)
    #msg_box = Listbox(frame2, fg="#000", bg="#ccc", width=100, height=20, selectmode=MULTIPLE, selectbackground="#666", selectforeground="#ccc", yscrollcommand=scroll_msg.set)
    msg_box = treectrl.MultiListbox(frame2)
    msg_box.config(selectcmd=get_book, selectmode='extended', columns=('Author[Last,First]', 'Title'), width=750)
    scroll_msg.config(command=msg_box.yview, highlightbackground="#fff")
    scroll_msg.grid(row=1, column=1, sticky=N+S)
    msg_box.grid(row=1, column=0, sticky=E+W)
    
    root.mainloop()
