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


def retrieveData(t, book=None):
    '''Get Data for profile from database.'''
    d = database.Retrieve(profile.database)

    if t == "books":
        profile.books = d.books()
        updateBookList()
    elif t == "quotes":
        profile.quotes = d.quotes(book=book)
        updateQuoteList()

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


def selectProfile():
    '''Get profile.'''
    profile.database = getFile("Select profile: ", 'db')
    profile_label['text'] = profile.database
    
    retrieveData(t="books")


def run():
    '''Get clippings file and database, run parser, and dump into database.'''
    profile.highlights = getFile("Select Kindle Highlights file: ", 'high')

    if not hasattr(profile, 'database'):
        selectProfile()
    
    p = clippingparser.Parse(profile.highlights, profile.database)
    print p.clean_clips
    
    p.database_dump()
    retrieveData(t='books')


def do_search():
    search_str = search_entry.get().lower()
    
    if not hasattr(profile, 'database'):
        selectProfile()
    
    s = database.Search(profile.database, profile.book_id, search_str, nocase=True)
    
    profile.search_terms = s.query_list
    
    #profile.books = s.books
    #updateBookList()
    profile.quotes = s.clips
    updateQuoteList()


def show_quote(sel):
    '''Open selected quote.'''
    quote = quote_box.get(sel[0])[0][1]

    ind_quote_win = Toplevel(root)
    ind_quote_win.config(bg="#666")
    
    t = Text(ind_quote_win, wrap=WORD)
    t.grid()
    t.insert(END, quote)
    
    # for testing:
    #profile.search_terms = ['to', 'and', 'or']
    
    if profile.search_terms:
        for s in profile.search_terms:
            show_search(t, s)
        t.tag_configure("sr", foreground="white", background="black")


def get_book(sel):
    '''Open selected book.'''
    global quote_box
    global search_entry
    
    profile.search_terms = []
    
    book_string = msg_box.get(sel[0])[0]
    profile.book_id = book_string[2]
    profile.book_title = " - ".join([book_string[1],book_string[0]])
    
    quote_win = Toplevel(root)
    quote_win.title(profile.book_title)
    quote_win.config(bg="#666")

    qs = Frame(quote_win)
    qs.config(pady=2, bg="#666")
    qs.grid()

    qf = Frame(quote_win)
    qf.config(height=30, pady=10)
    qf.grid()
    
    search_entry = StringVar()
    search_box = Entry(qs, textvariable=search_entry)
    search_box.grid(row=0, column=0, columnspan=4, sticky=W)
    Button(qs, command=do_search, text="Search Quotes").grid(row=0, column=4, sticky=E)
    
    scroll_quote = Scrollbar(qf, orient=VERTICAL)
    quote_box = treectrl.MultiListbox(qf, yscrollcommand=scroll_quote.set)
    scroll_quote.config(command=quote_box.yview, highlightbackground="#fff")
    scroll_quote.grid(row=0, column=1, sticky=N+S)
    quote_box.grid(row=0, column=0, sticky=E+W)

    quote_box.config(selectcmd=show_quote, selectmode='extended', columns=('Location', 'Quote'), expandcolumns=[1], width=750)
    [[quote_box.column_configure(quote_box.column(x), arrow='down', arrowgravity='right')] for x in range(2)]
    quote_box.notify_install('<Header-invoke>')
    quote_box.notify_bind('<Header-invoke>', lambda: sort_column(quote_box))
    quote_box.colors = ('white', '#ffdddd', 'white', '#ddeeff')
    [[quote_box.column_configure(quote_box.column(x), itembackground=quote_box.colors)] for x in range(2)]
    quote_box.sorting_order = {0:'increasing', 1:'increasing'}

    retrieveData(t="quotes", book=profile.book_id)


def sort_column(e):
    '''Sort column in multilistbox widgets.'''
    msg_box.sort(column=e.column, mode=msg_box.sorting_order[e.column])

    if msg_box.sorting_order[e.column] == 'increasing':
        msg_box.column_configure(msg_box.column(e.column), arrow='up')
        msg_box.sorting_order[e.column] = 'decreasing'
    else:
        msg_box.column_configure(msg_box.column(e.column), arrow='down')
        msg_box.sorting_order[e.column] = 'increasing'


def color_text(edit, tag, word, fg_color='black', bg_color='white'):
    # add a space to the end of the word
    word = word + " "
    edit.insert('end', word)
    end_index = edit.index('end')
    begin_index = "%s-%sc" % (end_index, len(word) + 1)
    edit.tag_add(tag, begin_index, end_index)
    edit.tag_config(tag, foreground=fg_color, background=bg_color)


def show_search(win, term):
    '''Showcase search terms'''
    win.mark_set("matchStart", win.index(1.0))
    win.mark_set("matchEnd", win.index(1.0))
    win.mark_set("searchLimit", win.index(END))
    
    count = IntVar()
    while True:
        i = win.search(term, "matchEnd", "searchLimit", count=count)
        if not i:
            break
        win.mark_set("matchStart", i)
        win.mark_set("matchEnd", "%s+%sc" % (i, count.get()))
        win.tag_add("sr", "matchStart", "matchEnd")


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
    book_menu.add_command(label="Sort by Author[LAST]", command=lambda: msg_box.sort(column=0))
    book_menu.add_command(label="Sort by Title", command=lambda: msg_box.sort(column=1))
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
    
    scroll_msg = Scrollbar(frame2, orient=VERTICAL)
    msg_box = treectrl.MultiListbox(frame2, yscrollcommand=scroll_msg.set)
    scroll_msg.config(command=msg_box.yview, highlightbackground="#fff")
    scroll_msg.grid(row=1, column=1, sticky=N+S)
    msg_box.grid(row=1, column=0, sticky=E+W)

    msg_box.config(selectcmd=get_book, selectmode='extended', columns=('Author[Last,First]', 'Title', 'ID'), expandcolumns=[0,1], width=750)
    [[msg_box.column_configure(msg_box.column(x), arrow='down', arrowgravity='right')] for x in range(2)]
    msg_box.column_configure(msg_box.column(2), width=1)
    msg_box.notify_install('<Header-invoke>')
    msg_box.notify_bind('<Header-invoke>', sort_column)
    msg_box.colors = ('white', '#ffdddd', 'white', '#ddeeff')
    [[msg_box.column_configure(msg_box.column(x), itembackground=msg_box.colors)] for x in range(2)]
    msg_box.sorting_order = {0:'increasing', 1:'increasing'}
    
    root.mainloop()
