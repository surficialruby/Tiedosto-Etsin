import Tkinter as tk
import time

class SampleApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.clock = tk.Label(self, text="")
        self.clock.pack()

        # start the clock "ticking"
        self.update_clock()

    def update_clock(self):
        now = time.strftime("%H:%M:%S" , time.gmtime())
        self.clock.configure(text=now)
        # call this function again in one second
        self.after(1000, self.update_clock)

if __name__== "__main__":
    app = SampleApp()
    app.mainloop()