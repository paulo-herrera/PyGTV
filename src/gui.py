from Tkinter import *
import ttk
import tkFileDialog
import os
import webbrowser
from version import PYGTV_VERSION

_default_font = ("Helvetica", 11)

def make_label(window, text, col, row):
    l = Label(window, text=text)
    l.grid(column=col, row=row)
    l.config(font=_default_font)
    return l
    
def make_button(window, title, cmd, col, row):
    b = Button(window, text=title, command = cmd, bg="black", fg="white", width = 15, pady=4)
    b.grid(column=col, row=row)
    b.config(font=_default_font)
    return b

def make_entry(window, col, row, width = 80, justify = "left"):
    e = Entry(window, width=width, justify = justify)
    e.grid(column=col, row=row) 
    e.config(font=_default_font)
    return e

def browse_file(target):
    fname = tkFileDialog.askopenfilename(filetypes = (("Shape files", "*.shp"), ("DBase files", "*.dbf"), ("All files", "*")), title='Please select a file')
    target.insert(5, fname)
    
def browse_dir(target):
    fname = tkFileDialog.askdirectory(title='Please select a directory')
    target.insert(5, fname)

def dummy():
    print("Dummy!")

class Echo:
    def __init__(self, text_frame):
        self.text = text_frame 
        
    def write(self, sstr):
        self.text.insert(END, sstr)
        print(sstr.strip())
    
    def error(self, sstr):
        sstr = "ERROR: " + sstr
        self.text.insert(END, sstr)  # TODO: change color font
        print(sstr.strip())
    
    def warning(self, sstr):
        sstr = "WARNING: " + sstr
        self.text.insert(END, sstr)  # TODO: change color font
        print(sstr.strip())
    
    
class PyGIS(Frame):
    def __init__(self):
        Frame.__init__(self)   
        self.version = PYGTV_VERSION
        self.initUI()
        
    def initUI(self):
        self.width  = 1000
        self.height = 300
        win_size = '%dx%d'%(self.width, self.height)
        self.master.geometry(win_size)
        self.master.title("GTV: Gis to VTK")
        self.pack(fill=BOTH, expand=True)
        
        self.setupUpperPanel()
        self.setupMiddlePanel()
        self.setupBottomPanel()

    def setupUpperPanel(self):
        w = Frame(self, relief=RAISED, borderwidth=1)
        w.pack(fill=X, expand=True)
        
        # Input
        self.l1 = make_label(w, "Path to shape file (.shp or .dbf) to export?", col=0, row=0) 
        self.e1 = make_entry(w, col=1, row=0)
        self.b1 = make_button(w, "Choose file", cmd = lambda: browse_file(self.e1), col=2, row=0)
        
        # Output
        self.l2 = make_label(w, "Directory where VTK files should be saved? ", col=0, row=1)
        self.e2 = make_entry(w, col=1, row=1)
        self.b2 = make_button(w, "Choose directory", cmd = lambda: browse_dir(self.e2), col=2, row=1)
        
        # Third row
        w2 = Frame(self, relief=RAISED, borderwidth=1)
        w2.pack(fill=X, expand=True)
        
        # Export only file or all files in directory
        self.processDirectory = BooleanVar()
        self.chk1 = Checkbutton(w2, text='Export all shape files in directory?', var = self.processDirectory,  command= lambda: self.text.write("Selected to export all files in directory\n"))
        self.chk1.config(font=_default_font)
        self.chk1.grid(column=0, row=0)
        
        self.verbose = BooleanVar()
        self.chk2 = Checkbutton(w2, text='Verbose output?', var = self.verbose,  command= lambda: self.text.write("Selected verbose output\n"))
        self.chk2.config(font=_default_font)
        self.chk2.grid(column=1, row=0)
        
        self.l3 = make_label(w2, "       Default elevation: ", col=2, row=0)
        self.e3 = make_entry(w2, col=3, row=0, width = 10, justify="right")
        self.e3.insert(5, "0.0")
        self.l3 = make_label(w2, "  (Only considered for files that do not contain z coordinate)", col=4, row=0)

    def setupMiddlePanel(self):
        w = Frame(self, relief=RAISED, borderwidth=1)
        w.pack(fill=BOTH, expand=True)
        
        # Main text export
        T = Text(w, height=10, width=160) # width and height in characters and lines 
        S = Scrollbar(w)
        T.pack(side=LEFT, fill=Y)
        S.pack(side=RIGHT, fill=Y)
        S.config(command=T.yview)
        T.config(yscrollcommand=S.set)
        T.pack()
        
        self.text = Echo(T)
        self.text.write("PyGTV version %s\n"%self.version)
        self.text.write("==============================\n")
        # for i in range(40):
            # T.insert(END, "Just a text Widget in two lines\n")
        
    def setupBottomPanel(self):
        w = Frame(self, relief=RAISED, borderwidth=1)
        w.pack(fill=BOTH, expand=True)
        
        self.brun  = make_button(w, "Run", cmd = self.run, col=0, row=0)
        
        self.l4 = make_label(w, "Exported files: ", col = 1, row = 0)
        self.exportedFiles = ttk.Combobox(w, values= ["None"])
        self.exportedFiles.grid(column=2, row=0)
        self.exportedFiles.current(0)
        
        self.bquit = make_button(w, "View File", cmd = self.view_file, col=3, row=0)
        self.bquit = make_button(w, "Quit", cmd = self.quit, col=4, row=0)
    
    def quit(self):
        self.master.destroy()

    def run(self):
        # some checking
        if len(self.e1.get()) == 0:
            self.text.error("Please select file to export\n")
            return
            
        elif len(self.e2.get()) == 0:
            self.text.error("Please select destination directory \n")
            return
        
        if self.processDirectory.get():
            self.src = os.path.dirname(self.e1.get())
            self.text.write("Exporting all files in directory: \n")
            self.text.write(self.src + "\n")
        else:
            self.src = self.e1.get()
            self.text.write("Exporting file: \n")
            self.text.write(self.src + "\n")
        
        self.dst = self.e2.get()
        self.text.write("To directory: \n")
        self.text.write(self.dst + "\n")
        
        default_z = float(self.e3.get())
        self.text.write("Default elevation: %g\n"%default_z)
        
        from shapeToVTK import get_file_list, export_files
        files_src, files_dst = get_file_list(self.src, self.dst)
        export_files(files_src, files_dst, default_z, self.verbose.get())
        self.text.write("=====================\n")
        self.text.write("  All files exported \n")
        self.text.write("=====================\n")
        
        import glob
        g = os.path.join(self.dst, "*.vtu")
        ff = glob.glob(g)
        
        filenames = [os.path.basename(f) for f in ff]
        #for f in ff: print(f)
        self.exportedFiles['values'] = filenames
        self.exportedFiles.current(0)
    
    def view_file(self):
        filename = self.exportedFiles.get()
        print(filename)
        
        path = os.path.join(self.dst, filename)
        print(path)
        
        editor = "gedit"
        os.system(editor + ' ' + path)
        
    
################################################################################
def run_gui(args):
    win = PyGIS()
    win.mainloop()
################################################################################

if __name__ == "__main__":
    run_gui()
    
# def show_file():
    # print("Clicked!!!")
    # filename = src_shp
    # # os.system(filename) # WINDOWS
    
    # print("Editor: " + os.getenv('EDITOR'))
    # os.system('%s %s' % (os.getenv('EDITOR'), filename))
    
    #editor = os.getenv('EDITOR')
    #if editor:
    #    os.system(editor + ' ' + filename)
    #else:
    #    webbrowser.open(filename)  