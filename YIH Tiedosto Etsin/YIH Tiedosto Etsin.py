__author__ = "Atte Kangasvieri"

import configparser, os, fnmatch, multiprocessing, subprocess, time
import tkinter as tk   
from tkinter import *
from tkinter import font  as tkfont

result = []

# Global method to get value of entry
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
        self.geometry("400x450")

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
        # Show a frame for the given page name
        frame = self.frames[page_name]
        frame.tkraise()

    def ini_settings(self,path):     
        # Get current location of program
        filepath = str(os.path.dirname(os.path.abspath(__file__)))
        try:
            # Create target Directory
            os.mkdir("assets")
        except FileExistsError:
            pass
        config = configparser.ConfigParser()
        config.read('assets\settings.INI')
        # Set program location as default search path if no other is set
        config['DEFAULT']['path'] = filepath    # update
        if path != None:
            config['SEARCH'] = {}
            # Set path as search path
            config['SEARCH']['Search_path'] = path    # update
        with open('assets\settings.INI', 'w') as configfile:    # save
            config.write(configfile)

class StartPage(tk.Frame):
    lb1 = None
    entry1 = None

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller       
        f_mid = Frame(self)
        f_top = Frame(self)
        f_bot = Frame(self)
        label = tk.Label(f_top, text="Haku", font=controller.title_font)
        label.grid(row=0, column=1)
        e1 = Entry(f_top)
        self.entry1 = e1
        button1 = tk.Button(f_top, text="Hae",
                           command=lambda: self.search())
        lb = Listbox(f_mid)        
        self.lb1 = lb
        sb = Scrollbar(lb, orient="vertical")
        l_loading = tk.Label(f_mid)
        self.label_loading = l_loading
        button2 = tk.Button(f_bot, text="Avaa",
                           command=lambda listbox=lb: self.opencur(lb))
        button3 = tk.Button(f_bot, text="Avaa Tiedosto sijainti",
                           command=lambda listbox=lb: subprocess.Popen(r'explorer /select,' + result[lb.curselection()[0]]))
        button4 = tk.Button(f_bot, text="Sulje",
                           command=lambda: controller.destroy())

        # Listbox double click
        lb.bind('<Double-1>', lambda listbox=lb: self.opencur(lb))

        # Element configs
        sb.config(command=lb.yview)
        lb.config(yscrollcommand=sb.set)

        f_top.pack()
        f_mid.pack(fill='both',expand=True)
        f_bot.pack()
        # f_top childs
        e1.grid(row=2, column=1)
        button1.grid(row=3, column=1,pady=10)
        # f_mid childs
        lb.pack(side="top",fill='both',expand=True)
        l_loading.pack(pady=10)
        sb.pack(side='right',fill='y')
        # f_bot childs
        button2.grid(row=5,column=1)
        button3.grid(row=6,column=1,pady=10)
        button4.grid(row=7,column=1)

        self.update()

    def update(self):
        # If queue not empty update lb1 listbox and empty queue
        if not queue_lb.empty():            
            self.lb1.insert('end',queue_lb.get())
            queue_lb.empty()
        # If queue not empty update result array and empty queue
        if not queue_result.empty():
            result.append(queue_result.get())
            queue_result.empty()
        # If queue not empty update label with 'Ladataa...' else set label empty
        if not queue_loading.empty():  
            self.label_loading['text'] = 'Ladataan...'
        else:
            self.label_loading['text'] = ''
        # call update function again in X ms
        self.after(1, self.update)
    
    # Open currently selected file in listbox
    def opencur(self,lb):
        file = result[lb.curselection()[0]]
        file_extension = os.path.splitext(file)
        subprocess.Popen(r'"'+file+'"',shell=True)

    # Start searching
    def search(self):
        global p_search
        # Empty listbox
        self.lb1.delete(0,'end')
        # Empty rersult array
        del result[:]
        queue_lb.empty()
        queue_result.empty()
        # Create new process for searching files in background
        p2 = multiprocessing.Process(target=Search, args=(str(getin(self.entry1)),queue_lb,queue_result,queue_loading))
        p2.daemon = True
        p2.start()

class Options(tk.Frame):

    def __init__(self, parent, controller):        
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="Polku", font=controller.title_font)
        e1 = Entry(self)
        self.entry1 = e1
        button1 = tk.Button(self, text="Save",
                           command=lambda: self.save_button())
        button2 = tk.Button(self, text="Back",
                           command=lambda: controller.show_frame("StartPage"))
        label.pack(side="top", fill="x", pady=10)
        e1.pack()
        button1.pack()
        button2.pack()

    # call mainapp.ini_settings to save path
    def save_button(self):
        self.controller.ini_settings(getin(self.entry1))
        # Empty entry
        self.entry1.delete(0, 'end')
        # Change page to StartPage
        self.controller.show_frame("StartPage")

# Seach process
class Search():
    def __init__(self, input, qlb, qresult,ql, *args, **kwargs):
        self.search_func(input, qlb, qresult, ql)

    def search_func(self, pattern = '', qlb = None, qresult = None, ql = None):
        pattern = '*'+pattern+'*.*'
        # Read path from settings.ini file
        config = configparser.ConfigParser()
        config.read('assets\settings.INI')
        dir_path = config['SEARCH']['search_path']
        # Set queue_loading True
        ql.put(True)
        for root, dirs, files in os.walk(dir_path):
            for name in files:
                if fnmatch.fnmatch(name, pattern):
                    # Add pattern matching results to queue_lb and queue_result
                    qlb.put((os.path.basename(os.path.join(root,name))))
                    qresult.put((os.path.join(root, name)))
        # Empty loading queue and cancel
        ql.empty()
        # Currently used to get update to queue so 'Ladataan...' text can be removed
        print(ql.get())

if __name__ == "__main__":
    multiprocessing.freeze_support()
    # create a manager - it lets us share native Python object types like
    # lists and dictionaries without worrying about synchronization - 
    # the manager will take care of it
    manager = multiprocessing.Manager()

    # using the manager, create shared data structures
    queue_lb = manager.Queue()
    queue_result = manager.Queue()
    queue_lb1 = manager.Queue()
    queue_loading = manager.Queue()

    # Main app
    app = MainApp()
    app.mainloop()

