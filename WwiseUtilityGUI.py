#! python3
import tkinter
import tkinter.messagebox
import tkinter.ttk as ttk

from WwiseUtilityInterface import WwiseUtilityClient


class MainWindow(tkinter.Tk):
    def __init__(self):
        super().__init__()

        self.client: WwiseUtilityClient = None

        self.title("Wwise Authoring Utility")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.attributes('-topmost', 1)

        self.__process_name = tkinter.StringVar(value='Connecting to Wwise...')
        self.lbl_process = ttk.Label(textvariable=self.__process_name)
        self.lbl_process.grid(row=0, column=0, sticky=("NESW"))

        self.__progress_rate = tkinter.IntVar(value=0)
        self.prog_bar = ttk.Progressbar(self,
                                        maximum=100,
                                        variable=self.__progress_rate,
                                        length=200,
                                        mode="determinate")
        self.prog_bar.grid(row=1, column=0, sticky=("NESW"))

        btn_cancel = ttk.Button(text="Cancel", command=self.btn_cancel_pressed)
        btn_cancel.grid(row=2, column=0)

        self.protocol("WM_DELETE_WINDOW", self.btn_cancel_pressed)

        self.withdraw()

    def btn_cancel_pressed(self):
        print("btn_cancel_pressed")
        if self.client is not None:
            self.client.disconnect()
        self.quit()

    def show_window(self):
        self.deiconify()

    def hide_window(self):
        self.withdraw()

    def show_simple_info(self, title, message):
        print(f"INFO: {title}: {message}")
        tkinter.messagebox.showinfo(title, message, parent=self)

    def show_warning(self, title, message):
        print(f"WARNING: {title}: {message}")
        self.hide_window()
        tkinter.messagebox.showwarning(title, message, parent=self)
        if self.client is not None:
            self.client.disconnect()
        self.quit()

    def show_error(self, title, message):
        print(f"ERROR: {title}: {message}")
        self.hide_window()
        tkinter.messagebox.showerror(title, message, parent=self)
        if self.client is not None:
            self.client.disconnect()
        self.quit()

    def set_current_process(self, progress_rate=0, process_name=''):
        self.__process_name.set(process_name)
        self.__progress_rate.set(progress_rate)
        self.update()

    def process_complete(self):
        self.after(500, lambda: self.quit())


if __name__ == "__main__":
    root = MainWindow()
    root.mainloop()
