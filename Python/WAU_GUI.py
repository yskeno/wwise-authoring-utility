import tkinter, tkinter.ttk, tkinter.messagebox


class MainWindow(tkinter.Tk):
    def __init__(self):
        super().__init__()

        self.title("Wwise Authoring Utility")
        self.geometry("300x75")
        self.iconbitmap()
        self.attributes("-topmost", 1)
        self.protocol("WM_DELETE_WINDOW", self.quit)

    def show_progress_bar(self):
        self.proc_label = tkinter.Label(text="Wwise Utility Process")
        self.proc_label.pack(side="top")

        self.prog_bar = tkinter.ttk.Progressbar(self, length=200, mode="determinate")
        self.prog_bar.pack(side="top")

    def update_progress(self, process: str, progress: int):
        if self.proc_label == None or self.prog_bar == None:
            return False

    def show_error(self, title: str, message: str):
        self.withdraw()
        tkinter.messagebox.showerror(title, message)

    def show_warning(self, title: str, message: str):
        self.withdraw()
        tkinter.messagebox.showwarning(title, message)
