import sys

import tkinter
import tkinter.messagebox
import tkinter.ttk as ttk


class MainWindow(tkinter.Tk):
    def __init__(self):
        super().__init__()
        self.withdraw()

        self.title("Wwise Authoring Utility")
        self.iconbitmap(sys.executable)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.attributes('-topmost', 1)
        self.protocol("WM_DELETE_WINDOW", self.close_window)

        self.__process_name = tkinter.StringVar(value='WAAPI')
        self.__progress_rate = tkinter.IntVar(value=0)

        self.stategroup_name: str = ''
        self.assigned_keywords: dict = {}

    def open_custom_switchassign_setting(self, switch_info: dict):
        self.switch_dict = switch_info
        self.wd_switch_setting = tkinter.Toplevel(self)
        self.wd_switch_setting.title("Custom Switch Assign Setting")
        self.wd_switch_setting.geometry("500x300")
        self.wd_switch_setting.protocol(
            "WM_DELETE_WINDOW", self.close_window)

        self.frm_group_setting = ttk.Frame(self.wd_switch_setting, padding=5)
        self.lbl_groupname = ttk.Label(self.frm_group_setting,
                                       text='Select State/Switch Group to assign.')
        self.lbl_groupname.pack(anchor='nw')

        # Create GroupName ComboBox.
        cmb_values = [group_info.get('path', '')
                      for group_info in self.switch_dict.values()]
        groupname_length = len(max(cmb_values))+15
        self.cmb_groupname = ttk.Combobox(self.frm_group_setting,
                                          width=groupname_length, state='readonly', values=cmb_values)
        # self.cmb_groupname.current(0)
        self.cmb_groupname.bind('<<ComboboxSelected>>',
                                self._open_switch_keyword_setting)
        self.cmb_groupname.pack(anchor='nw', fill='x')

        self.cvs_scrollable = tkinter.Canvas(self.wd_switch_setting)

        self.frm_children = ttk.Frame(self.cvs_scrollable, padding=5)
        self.cvs_scrollable.create_window(
            (0, 0), window=self.frm_children, anchor='nw', tags='frame')
        self.frm_children.columnconfigure(0, weight=1)
        self.frm_children.columnconfigure(1, weight=2)
        self.frm_children.bind('<Configure>', lambda e: self.cvs_scrollable.configure(
            width=e.width, scrollregion=self.cvs_scrollable.bbox('all')))
        self.cvs_scrollable.bind('<Configure>', self._on_canvas_configure)

        self.vsb = ttk.Scrollbar(
            self.wd_switch_setting, command=self.cvs_scrollable.yview)
        self.vsb.pack(side='right', fill='y')
        self.cvs_scrollable.configure(yscrollcommand=self.vsb.set)

        self.lbl_childlen = ttk.Label(self.wd_switch_setting,
                                      text='Enter keyword between State/Switch and audio object.')
        self.keyword_objects = {}

        self.frm_buttons = ttk.Frame(self.wd_switch_setting, padding=5)
        self.btn_assign = ttk.Button(self.frm_buttons,
                                     state='disable', text='Assign', command=self._assign_switch_keywords)
        self.btn_assign.pack(side='left', anchor='center')
        self.btn_cancel = ttk.Button(self.frm_buttons,
                                     state='normal', text='Cancel', command=self.close_window)
        self.btn_cancel.pack(side='right', anchor='center')

        self.frm_group_setting.pack(anchor='nw', fill='x')
        self.lbl_childlen.pack(anchor='nw')
        self.frm_buttons.pack(anchor='w', side='bottom')
        self.cvs_scrollable.pack(anchor='nw', fill='both', expand=True)

        self.bind_all('<MouseWheel>', self._on_mouse_wheel_move)

    def _on_canvas_configure(self, event):
        self.cvs_scrollable.itemconfigure(
            'frame', width=self.cvs_scrollable.winfo_width())

    def _on_mouse_wheel_move(self, event=None):
        if event:
            self.cvs_scrollable.yview_scroll(
                int(-1*(event.delta/abs(event.delta))), 'units')

    def _open_switch_keyword_setting(self, event):
        self.btn_assign['state'] = 'normal'
        for switch_info in self.switch_dict.values():
            if event.widget.get() == switch_info.get('path', ''):
                if any(self.keyword_objects):
                    for label, entry in self.keyword_objects.items():
                        label.destroy()
                        entry.destroy()
                    self.keyword_objects.clear()

                childname_length = len(max(switch_info.get('child', [])))
                for child in switch_info.get('child', ''):
                    self.keyword_objects.setdefault(
                        ttk.Label(self.frm_children,
                                  name="lbl_" + child, width=childname_length, text=child, padding=2),
                        ttk.Entry(self.frm_children,
                                  name='ent_' + child, width=childname_length))

                for i, obj in enumerate(self.keyword_objects.items()):
                    obj[0].grid(column=0, row=i+1, sticky="EW")
                    obj[1].grid(column=1, row=i+1, sticky="EW")
        return

    def _assign_switch_keywords(self):
        # for keyword_entry in self.keyword_objects.values():
        #     switchname: str = keyword_entry.winfo_name().removeprefix('ent_')
        #     self.assigned_keywords[switchname.removeprefix('ent_')
        #                            ] = keyword_entry.get()

        self.stategroup_name = self.cmb_groupname.get()
        self.assigned_keywords = {keyword_entry.winfo_name().removeprefix(
            'ent_'): keyword_entry.get() for keyword_entry in self.keyword_objects.values()}

        print(self.assigned_keywords)
        self.close_window()

    def show_progress_window(self):
        self.lbl_process = ttk.Label(textvariable=self.__process_name)
        self.lbl_process.grid(row=0, column=0, sticky=("NESW"))

        self.prog_bar = ttk.Progressbar(self,
                                        maximum=100,
                                        variable=self.__progress_rate,
                                        length=200,
                                        mode="determinate")
        self.prog_bar.grid(row=1, column=0, sticky=("NESW"))

        self.deiconify()

    def set_current_process(self, progress_rate=0, process_name=''):
        self.__process_name.set(process_name)
        self.__progress_rate.set(progress_rate)
        self.update()

    def show_simple_info(self, title, message):
        print(f'INFO: {title}: {message}')
        tkinter.messagebox.showinfo(title, message, parent=self)

    def result_success(self, title, message):
        self.withdraw()
        print(f'SUCCESS: {title}: {message}')
        # tkinter.messagebox.showinfo(title, message)
        self.close_window()

    def result_warning(self, title, message):
        self.withdraw()
        print(f'WARNING: {title}: {message}')
        tkinter.messagebox.showwarning(title, message, parent=self)
        self.close_window()

    def result_error(self, title, message):
        self.withdraw()
        print(f'Exception: {title}: {message}')
        tkinter.messagebox.showerror(title, message, parent=self)
        self.close_window()

    def close_window(self):
        self.quit()


if __name__ == "__main__":
    root = MainWindow()
    root.mainloop()
