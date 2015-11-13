from tkinter import *


class GUI_Window(Frame):
    def __init__(self, exit_funtion=None, pause_function=None):
        master = Tk()
        Frame.__init__(self, master)
        master.geometry("50x50")
        self.master = master
        self.init_window()
        self.exit_function = exit_funtion
        self.pause_function = pause_function
        master.mainloop()

    def init_window(self):
        self.master.title("IMDB Crawler")
        self.pack(fill=BOTH, expand=1)
        quit_button = Button(self, text="Quit", command=self.client_exit)
        quit_button.place(x=0, y=0)

        quit_button = Button(self, text="Pause", command=self.client_pause)
        quit_button.place(x=50, y=0)

    def client_exit(self):
        print("exit function")
        if self.exit_function is not None:
            self.exit_function()
        else:
            exit()

    def client_pause(self):
        if self.pause_function is not None:
            self.pause_function()
        else:
            pass



'''
def my_exit_function():
    print ("here")

app = MyWindow(my_exit_function)
'''