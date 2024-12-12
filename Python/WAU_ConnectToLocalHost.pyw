import tkinter.ttk
from waapi import WaapiClient, CannotConnectToWaapiException
import concurrent.futures, tkinter, time


class NoAvailableLocalhostException(Exception):
    pass


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


def connect_to_localhost(client: WaapiClient, root: MainWindow) -> bool:
    if client.call("ak.wwise.core.remote.getConnectionStatus")["isConnected"]:
        root.title("Wwise Utility: Disconnect from Localhost")
        root.proc_label["text"] = "Disconnect..."
        root.prog_bar.configure(mode="indeterminate")
        root.prog_bar.start(5)

        client.call("ak.wwise.core.remote.disconnect")
        client.disconnect()

        root.prog_bar.configure(mode="determinate")
        root.prog_bar.step(100)
        time.sleep(0.5)
        root.quit()

    else:
        root.title("Wwise Utility: Connect to Localhost")
        root.proc_label["text"] = "Get available consoles..."
        root.prog_bar.step(20)

        availables = client.call("ak.wwise.core.remote.getAvailableConsoles")["consoles"]

        root.proc_label["text"] = "Search target localhost application..."
        root.prog_bar.step(40)

        target = []
        for console in availables:
            if console["host"] != "127.0.0.1":
                continue
            target.append(console)

        if len(target) == 0:
            raise NoAvailableLocalhostException

        if len(target) != 1:
            result = []
            for console in target:
                if "editor" in console["appName"].lower():
                    result.append(console)
            if len(result) > 0:
                target = result

        root.proc_label["text"] = f"Connect to \"{target[0]['appName']}\"..."
        root.prog_bar.step(20)

        client.call(
            "ak.wwise.core.remote.connect", {"host": target[0]["host"], "commandPort": target[0]["commandPort"]}
        )
        client.disconnect()

        root.proc_label["text"] = "Connected!"
        root.prog_bar.step(19.9)
        root.quit()


def main():
    root = MainWindow()
    root.show_progress_bar()

    try:
        with WaapiClient() as client, concurrent.futures.ThreadPoolExecutor() as executor:
            thread = executor.submit(connect_to_localhost, client, root)

            root.mainloop()
            result = thread.result()
            if result is not None:
                raise result

    except NoAvailableLocalhostException as e:
        print("NoAvailableLocalhostException", f"{str(e)}\nNo available consoles on localhost.")

    except CannotConnectToWaapiException as e:
        # window.result_error(
        #     "CannotConnectToWaapiException", f"{str(e)}\nIs Wwise running and Wwise Authoring API enabled?"
        # )
        print("CannotConnectToWaapiException", f"{str(e)}\nIs Wwise running and Wwise Authoring API enabled?")

    except Exception as e:
        # window.result_error("ERROR", str(e))
        print("ERRORRRR", str(e))


if __name__ == "__main__":
    main()
