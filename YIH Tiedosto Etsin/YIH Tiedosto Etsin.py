"""
@author: Atte Kangasvieri
"""
import configparser, os, fnmatch, multiprocessing, subprocess, time 
import tkinter as tk   
from tkinter import *
from tkinter import font  as tkfont

result = []

def getin(e1):
    string = e1.get()
    return string

class MainApp(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.title_font = tkfont.Font(family='Helvetica', size=18, weight="bold", slant="italic")
        self.title("YIH")
        if(os.path.isfile('assets\yih.ico')):
            self.iconbitmap('assets\yih.ico')
        self.geometry("400x350")

        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (StartPage, Options):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame

            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")

        menubar = Menu(self)
        menubar.add_command(label="Asetukset", command=lambda: self.show_frame("Options"))
        self.config(menu=menubar)

        self.show_frame("StartPage")
        self.ini_settings(None)

    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.tkraise()

    def ini_settings(self,path):        
        filepath = str(os.path.dirname(os.path.abspath(__file__)))
        try:
            # Create target Directory
            os.mkdir("assets")
        except FileExistsError:
            print('')
        config = configparser.ConfigParser()
        config.read('assets\settings.INI')
        config['DEFAULT']['path'] = filepath    # update
        if path != None:
            config['SEARCH'] = {}
            config['SEARCH']['Search_path'] = path    # update
        with open('assets\settings.INI', 'w') as configfile:    # save
            config.write(configfile)

class StartPage(tk.Frame):
    lb1 = None
    entry1 = None

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        label = tk.Label(self, text="Haku", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)
        e1 = Entry(self)
        e1.pack()
        self.entry1 = e1
        button1 = tk.Button(self, text="Hae",
                           command=lambda: self.search())       
        button1.pack()        
        lb = Listbox(self)        
        lb.pack(side="top",fill="x",expand=True)
        self.lb1 = lb
        global lb1G
        lb1G = self.lb1
        button2 = tk.Button(self, text="Avaa",
                           command=lambda listbox=lb: self.opencur(lb))
        button3 = tk.Button(self, text="Avaa Tiedosto sijainti",
                           command=lambda listbox=lb: subprocess.Popen(r'explorer /select,' + result[lb.curselection()[0]]))
        button4 = tk.Button(self, text="Sulje",
                           command=lambda: controller.destroy())
        button2.pack()
        button3.pack()
        button4.pack()
        self.update()

    def update(self):
        if not queue_lb.empty():            
            self.lb1.insert(0,queue_lb.get()[1])
            queue_lb.empty()
        if not queue_result.empty():
            result.insert(0,queue_result.get())
            queue_result.empty()
        self.after(100, self.update)

    def opencur(self,lb):
        file = result[lb.curselection()[0]]
        file_extension = os.path.splitext(file)
        subprocess.Popen(r'"'+file+'"',shell=True)

    def search(self):
        self.lb1.delete(0,'end')
        del result[:]
        p2 = multiprocessing.Process(target=Search, args=(str(getin(self.entry1)),queue_lb,queue_result))
        p2.daemon = True
        p2.start()

class Options(tk.Frame):

    def __init__(self, parent, controller):        
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="Asetukset", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)
        e1 = Entry(self)
        e1.pack()
        self.entry1 = e1
        button1 = tk.Button(self, text="Save",
                           command=lambda: self.save_button())
        button2 = tk.Button(self, text="Back",
                           command=lambda: controller.show_frame("StartPage"))
        button1.pack()
        button2.pack()

    def save_button(self):
        self.controller.ini_settings(getin(self.entry1))
        self.entry1.delete(0, 'end')
        self.controller.show_frame("StartPage")

class Search():
    def __init__(self, input, qlb, qresult, *args, **kwargs):
        self.search_func(input, qlb, qresult)

    def search_func(self, pattern = '', qlb = '', qresult = ''):
        pattern = '*'+pattern+'*.*'
        config = configparser.ConfigParser()
        config.read('assets\settings.INI')
        dir_path = config['SEARCH']['search_path']
        i = 0
        for root, dirs, files in os.walk(dir_path):
            for name in files:
                if fnmatch.fnmatch(name, pattern):
                    qlb.put((i,os.path.basename(os.path.join(root,name))))
                    qresult.put((os.path.join(root, name)))
            ++i  

if __name__ == "__main__":
    multiprocessing.freeze_support()
    # create a manager - it lets us share native Python object types like
    # lists and dictionaries without worrying about synchronization - 
    # the manager will take care of it
    manager = multiprocessing.Manager()

    # using the manager, create shared data structures
    queue_lb = manager.Queue()
    queue_result = manager.Queue()
    queue_gresult = manager.Queue()
    queue_lb1 = manager.Queue()
    app = MainApp()
    # create our pool of workers - this spawns the processes
    pool = multiprocessing.Pool()

    app.mainloop()

