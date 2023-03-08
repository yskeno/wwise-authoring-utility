#! python3
import sys

import tkinter
import tkinter.messagebox
import tkinter.ttk as ttk


class MainWindow(tkinter.Tk):
    def __init__(self):
        super().__init__()
        self.withdraw()

        self.client = None

        self.title("Wwise Authoring Utility")
        self.iconbitmap(sys.executable)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.attributes('-topmost', 1)

        self.__process_name = tkinter.StringVar(value='WAAPI')
        self.__progress_rate = tkinter.IntVar(value=0)

    def show_progress_window(self):
        self.lbl_process = ttk.Label(textvariable=self.__process_name)
        self.lbl_process.grid(row=0, column=0, sticky=("NESW"))

        self.prog_bar = ttk.Progressbar(self,
                                        maximum=100,
                                        variable=self.__progress_rate,
                                        length=200,
                                        mode="determinate")
        self.prog_bar.grid(row=1, column=0, sticky=("NESW"))

        self.protocol("WM_DELETE_WINDOW", self.close_window)
        self.deiconify()

    def set_current_process(self, progress_rate=0, process_name=''):
        self.__process_name.set(process_name)
        self.__progress_rate.set(progress_rate)
        self.update()

    def show_simple_info(self, title, message):
        print(f"INFO: {title}: {message}")
        tkinter.messagebox.showinfo(title, message, parent=self)

    def result_warning(self, title, message):
        print(f"WARNING: {title}: {message}")
        self.withdraw()
        tkinter.messagebox.showwarning(title, message, parent=self)
        self.close_window()

    def result_error(self, title, message):
        print(f"ERROR: {title}: {message}")
        self.withdraw()
        tkinter.messagebox.showerror(title, message, parent=self)
        self.close_window()

    def close_window(self):
        if self.client is not None:
            self.client.disconnect()
        self.quit()


if __name__ == "__main__":
    root = MainWindow()
    root.mainloop()
