#!/usr/bin/env python
#	KindleQuotes - xiao_haozi@mutaku.com - http://mutaku.com
# -*- coding: utf_8 -*-

from Tkinter import *
import tkFileDialog
import os
import sys
import TkTreectrl as treectrl
import clippingparser
import database
import fb


path = os.path.dirname(sys.argv[0])


class Profile():
    '''Profile attribute holder.'''
    def __init__(self):
        pass


def getFile(title, t):
    '''Ask for respective file.'''
    options = {
        'parent' : root,
        'title' : title,
        'initialdir' : path,
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
        'initialdir' : path,
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

    profile.name = os.path.basename(profile.database).rstrip('.s3db')
    profile_label['text'] = ''.join([profile.name.capitalize(), "'s Kindle Quotes, Highlights, and Bookmarks"])


def retrieveData(t, book=None):
    '''Get Data for profile from database.'''
    d = database.Retrieve(profile.database)

    if t == "books":
        profile.books = d.books()
        updateBookList()
    elif t == "quotes":
        profile.quotes = d.quotes(book=book)
        updateQuoteList()
        profile.search_terms = []
        profile.search_tag = ""
        search_box.delete(0, END)


def selectProfile():
    '''Get profile.'''
    profile.database = getFile("Select profile: ", 'db')
    profile.name = os.path.basename(profile.database).rstrip('.s3db')
    profile_label['text'] = ''.join([profile.name.capitalize(), "'s Kindle Quotes, Highlights, and Bookmarks"])
    
    retrieveData(t="books")


def sync_db():
    '''Get clippings file and database, run parser, and dump into database.'''
    profile.highlights = getFile("Select Kindle Highlights file: ", 'high')

    if not hasattr(profile, 'database'):
        selectProfile()
    
    p = clippingparser.Parse(profile.highlights, profile.database)
    
    p.database_dump()
    retrieveData(t='books')


def do_search(event):
    quote_box.selection_clear(0,END)
    search_str = search_entry.get().lower()
    
    if len(search_str) > 2:
        s = database.Search(profile.database, profile.book_id, search_str)
        
        profile.search_terms = s.query_list
        profile.search_tag = "Showing search results for: "+', '.join(profile.search_terms)
        
        profile.quotes = s.clips
        updateQuoteList()
    else:
        pass


def show_search(win, term):
    '''Showcase search terms'''
    win.mark_set("matchStart", win.index(1.0))
    win.mark_set("matchEnd", win.index(1.0))
    win.mark_set("searchLimit", win.index(END))
    
    count = IntVar()
    while True:
        i = win.search(term, "matchEnd", "searchLimit", count=count, nocase=True)
        if not i:
            break
        win.mark_set("matchStart", i)
        win.mark_set("matchEnd", "%s+%sc" % (i, count.get()))
        win.tag_add("sr", "matchStart", "matchEnd")


def sort_column(e, t=None):
    '''Sort column in multilistbox widgets.'''
    #some debugging for sort events
    #for attr in dir(e):
    #    print str(attr)+" => "+str(getattr(e, attr))

    t.sort(column=e.column, mode=t.sorting_order[e.column])
    #msg_box.sort(column=e.column, mode=msg_box.sorting_order[e.column], key=lambda x: x.lower())

    if t.sorting_order[e.column] == 'increasing':
        t.column_configure(t.column(e.column), arrow='up')
        t.sorting_order[e.column] = 'decreasing'
    else:
        t.column_configure(t.column(e.column), arrow='down')
        t.sorting_order[e.column] = 'increasing'


def updateBookList():
    '''Update the books listed in main display.'''
    msg_box.delete(0, END)

    for b in profile.books:
        entry = (b[2], b[1], b[0])
        msg_box.insert(END, *entry)
    
    msg_box.sort(0)


def updateQuoteList():
    '''Update the quotes listed in toplevel display.'''
    quote_box.delete(0, END)

    for q in profile.quotes:
        entry = (q[2], q[5])
        quote_box.insert(END, *entry)
    
    quote_box.sort(0, mode="increasing")


def post_quote():
    '''Post this quote to Facebook with optional note.'''
    try:
        note = quote_post_entry.get()
        
        #quote_post_box.delete(0, END)
        #quote_post_box.insert(0, "[trying to post to Facebook] ")

        #f = fb.FacebookIt(app_id='134978336629865')
        f = fb.FacebookIt()
        post_string = '\n\n'.join([profile.current_quote.rstrip('\n'), "--"+profile.book_title, note, "Posted from KindleQuotes (https://github.com/mutaku/KindleQuotes/wiki)"])
 
        #quote_post_box.delete(0, END)
        quote_post_box.insert(0, "Posted successfully. ")

    except Exception as inst:
        quote_post_box.delete(0, END)
        quote_post_box.insert(0, " - ".join(["Error posting to Facebook", inst.__str__()]))


def show_quote(event):
    '''Open selected quote.'''
    global quote_post_entry
    global quote_post_box
    
    try:
        element = quote_box.get(quote_box.curselection()[0])
        profile.current_quote = element[0][1]
    
        ind_quote_win = Toplevel(root)
        ind_quote_win.config(bg="#666")
        
        t = Text(ind_quote_win, wrap=WORD, font=("Helvetica", 13,), padx=10, pady=10)

        t.insert(END, profile.current_quote)
        
        if profile.search_terms:
            for s in profile.search_terms:
                show_search(t, s)
            t.tag_configure("sr", foreground="white", background="black", font=("bold"))
            Label(ind_quote_win, text=profile.search_tag, foreground="white", background="#666", font=("Helvetica", 13, "bold")).pack()

        t.pack()

        qp = Frame(ind_quote_win)

        qp.config(bg="#666")
        qp.pack(side=BOTTOM, fill=X, expand=1, pady=5)        
        
        quote_post_entry = StringVar()
        quote_post_box = Entry(qp, text=quote_post_entry, font=("Helvetica", 11, "bold"))
        quote_post_box.bind('<Return>', post_quote)
        quote_post_box.pack(side=LEFT, fill=BOTH, expand=1, ipadx=60)
        
        Button(qp, command=post_quote, text="Post to Facebook").pack(side=RIGHT)

    except:
        pass


def get_book(sel):
    '''Open selected book.'''
    global quote_box
    global search_entry
    global search_box
    
    profile.search_terms = []
    
    book_string = msg_box.get(sel[0])[0]
    profile.book_id = book_string[2]
    profile.book_title = " - ".join([book_string[1],book_string[0]])
    
    quote_win = Toplevel(root)
    quote_win.title(profile.book_title)
    quote_win.config(bg="#333333")

    qs = Frame(quote_win)
    qs.config(pady=2, bg="#333333")
    qs.pack(side=TOP, fill=BOTH, expand=0)

    qf = Frame(quote_win)
    qf.config(pady=10)
    qf.pack(side=BOTTOM, fill=BOTH, expand=1)
    
    search_entry = StringVar()
    search_box = Entry(qs, textvariable=search_entry, font=("Helvetica", 11, "bold"))
    search_box.bind('<Return>', do_search)
    search_box.pack(side=LEFT, fill=BOTH, expand=1, ipadx=60)
    Button(qs, command=lambda: retrieveData(t="quotes", book=profile.book_id), text="Reset").pack(side=RIGHT)
    Button(qs, command=do_search, text="Search Quotes").pack(side=RIGHT)
    
    scroll_quote = Scrollbar(qf, orient=VERTICAL)
    quote_box = treectrl.MultiListbox(qf, yscrollcommand=scroll_quote.set, font=("Helvetica", 11,))
    scroll_quote.config(command=quote_box.yview, highlightbackground="#fff")
    scroll_quote.pack(side=RIGHT, fill=Y)
    quote_box.pack(fill=BOTH, expand=1)

    quote_box.config(selectcmd=show_quote, selectmode='extended', columns=('Location', 'Quote'), expandcolumns=[1], width=900, height=500)
    [[quote_box.column_configure(quote_box.column(x), arrow='down', arrowgravity='right')] for x in range(2)]
    quote_box.notify_install('<Header-invoke>')
    #quote_box.notify_bind('<Header-invoke>', lambda event: quote_box.sort(column=event.column, mode='increasing'))
    quote_box.notify_bind('<Header-invoke>', lambda event,t=quote_box: sort_column(event, t))    
    quote_box.colors = ('white', '#ffdddd', 'white', '#ddeeff')
    [[quote_box.column_configure(quote_box.column(x), itembackground=quote_box.colors)] for x in range(2)]
    
    quote_box.sorting_order = {0:'increasing', 1:'increasing'}

    retrieveData(t="quotes", book=profile.book_id)


if __name__ == '__main__':

    profile = Profile()

    root = Tk()
    root.title('KindleQuotes')
    
    menubar = Menu(root, font=("Helvetica", 11,))
    
    main_menu = Menu(menubar, tearoff=0, font=("Helvetica", 11,))
    main_menu.add_command(label="Exit", command=root.destroy)
    menubar.add_cascade(label="KindleQuotes", menu=main_menu)
    
    pro_menu = Menu(menubar, tearoff=0, font=("Helvetica", 11,))
    pro_menu.add_command(label="Open/Switch Profile", command=selectProfile)
    pro_menu.add_command(label="New Profile", command=setupProfile)
    menubar.add_cascade(label="Profile", menu=pro_menu)

    sync_menu = Menu(menubar, tearoff=0, font=("Helvetica", 11,))
    sync_menu.add_command(label="Sync Database", command=sync_db)
    menubar.add_cascade(label="Sync", menu=sync_menu)

    book_menu = Menu(menubar, tearoff=0, font=("Helvetica", 11,))
    book_menu.add_command(label="Sort by Author", command=lambda: msg_box.sort(column=0))
    book_menu.add_command(label="Sort by Title", command=lambda: msg_box.sort(column=1))
    menubar.add_cascade(label="Books", menu=book_menu)
    
    root.config(bg="#333333", menu=menubar)
    
    frame1 = Frame(root)
    frame1.config(bg="#333333", padx=10, pady=10)
    frame1.pack(side=TOP, fill=BOTH)

    frame2 = Frame(root)
    frame2.config(bg="#333333", padx=10, pady=10)
    frame2.pack(side=RIGHT, fill=BOTH)
    
    frame3 = Frame(frame1)
    frame3.config(bg="#333333", padx=5, pady=10)
    frame3.pack(side=LEFT, fill=BOTH)

    frame4 = Frame(frame1)
    frame4.config(bg="#333333", padx=5, pady=10)
    frame4.pack(fill=BOTH)
    
    photo = PhotoImage(file=path+"/kindle_sm.gif")
    pLabel = Label(frame3, image=photo, relief=SUNKEN, borderwidth=3)
    pLabel.image = photo
    pLabel.pack(side=LEFT, expand=1)
    
    profile_label = Label(frame4, text="Welcome to KindleQuotes!\n Create or Select a profile.", bg="#333333", fg="#fff", font=("Helvetica", 18), wraplength=600)
    profile_label.pack(fill=X, expand=1, ipady=10)
    
    scroll_msg = Scrollbar(frame2, orient=VERTICAL)
    msg_box = treectrl.MultiListbox(frame2, yscrollcommand=scroll_msg.set, font=("Helvetica", 11,))
    scroll_msg.config(command=msg_box.yview, highlightbackground="#fff")
    scroll_msg.pack(side=RIGHT, fill=Y)
    msg_box.pack(fill=BOTH, expand=1)

    msg_box.config(selectcmd=get_book, selectmode='extended', columns=('Author', 'Title', 'ID'), expandcolumns=[0,1], width=750)
    [[msg_box.column_configure(msg_box.column(x), arrow='down', arrowgravity='right')] for x in range(2)]
    msg_box.column_configure(msg_box.column(2), width=1)
    msg_box.notify_install('<Header-invoke>')
    msg_box.notify_bind('<Header-invoke>', lambda event,t=msg_box: sort_column(event, t))
    msg_box.colors = ('white', '#ffdddd', 'white', '#ddeeff')
    [[msg_box.column_configure(msg_box.column(x), itembackground=msg_box.colors)] for x in range(2)]
    msg_box.sorting_order = {0:'increasing', 1:'increasing'}
    
    root.mainloop()
