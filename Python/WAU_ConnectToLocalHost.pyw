from waapi import WaapiClient, CannotConnectToWaapiException
import concurrent.futures, time
import WAU_GUI


class NoAvailableLocalhostException(Exception):
    pass


def connect_to_localhost(client: WaapiClient, root: WAU_GUI.MainWindow) -> bool:
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

        root.prog_bar.step(20)

        localApps = []
        for console in availables:
            if console["host"] != "127.0.0.1":
                continue
            localApps.append(console)

        if len(localApps) == 0:
            root.proc_label["text"] = "No available consoles."
            root.quit()
            raise NoAvailableLocalhostException

        root.prog_bar.step(20)
        if len(localApps) != 1:
            targets = []
            for console in localApps:
                if "editor" in console["appName"].lower():
                    targets.append(console)
            if len(targets) > 0:
                localApps = targets

        root.proc_label["text"] = f"Connect to \"{targets[0]['appName']}\"..."
        root.prog_bar.step(20)

        client.call(
            "ak.wwise.core.remote.connect", {"host": targets[0]["host"], "commandPort": targets[0]["commandPort"]}
        )
        client.disconnect()

        root.proc_label["text"] = "Connected!"
        root.prog_bar.step(19.9)
        root.quit()
        return


def main():
    root = WAU_GUI.MainWindow()
    root.show_progress_bar()

    try:
        with WaapiClient() as client, concurrent.futures.ThreadPoolExecutor() as executor:
            thread = executor.submit(connect_to_localhost, client, root)

            root.mainloop()
            result = thread.result()
            if result is not None:
                raise result

    except NoAvailableLocalhostException as e:
        root.show_warning("NoAvailableLocalhostException", f"{str(e)}\nNo available consoles on localhost.")

    except CannotConnectToWaapiException as e:
        root.show_error(
            "Cannot Connect To Waapi Exception", f"{str(e)}\n\nIs Wwise running and Wwise Authoring API enabled?"
        )

    except Exception as e:
        root.show_error("Exception", str(e))


if __name__ == "__main__":
    main()
