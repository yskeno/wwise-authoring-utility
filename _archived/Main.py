#! python3.9

import sys
import threading

from WAU_Interface import WwiseUtilityClient, CannotConnectToWaapiException
import WAU_GUI

help_text = """
usage: Wwise Authoring Utility help you to control Wwise.

arguments:
    remote  Connect to / Disconnect from Localhost console.
            If found more than one Localhost, give priority to one not containing "edit" in console name.
    rename  Auto rename containers by common prefix of children's name.
            Incremental numbers at the end of name are allowed.
                ex.) OK: NewRandomContainer -> Footsteps
                            |- Footsteps_01
                            |- Footsteps_02
                            |- Footsteps_02
                     NG: NewRundomContainer
                            |- WeakFootsteps_01
                            |- NormalFootsteps_01
                            |- StrongFootsteps_01
    switch  Auto assign object to Switch container.
            It is necessary common words between object and State.
            Also objects needs common prefix.
                ex.)     |  Children's Name   | State Name |
                     OK: | Footsteps_Rock_01  |    Rock    |
                         | Footsteps_Wood_01  |    Wood    |
                         | Footsteps_Metal_01 |    Metal   |
                     NG: | Rock_Footsteps_01  |    Rock    |
                         | Wood_Footsteps_01  |    Wood    |
                         | Metal_Footsteps_01 |    Metal   |

options:
    help    show this help message and exit.
"""


class InterruptedWAU(Exception):
    pass


def main():
    window = WAU_GUI.MainWindow()
    if len(sys.argv) <= 1 or sys.argv[1] == "help":
        print(help_text)
        window.show_simple_info("Wwise Authoring Utility", help_text)
        window.quit()
        return

    if sys.argv[1] == "print":
        print(sys.argv)
        return

    try:
        with WwiseUtilityClient() as client:
            waapi_thread: threading.Thread = None
            if sys.argv[1] == "remote":
                waapi_thread = threading.Thread(
                    target=client.connect_to_localhost,
                    kwargs={
                        "window": window,
                    },
                )
            elif sys.argv[1] == "rename":
                waapi_thread = threading.Thread(
                    target=client.auto_rename_container,
                    kwargs={
                        "window": window,
                    },
                )
            elif sys.argv[1] == "switch_auto":
                waapi_thread = threading.Thread(
                    target=client.auto_assign_switch_container,
                    kwargs={
                        "window": window,
                    },
                )
            elif sys.argv[1] == "switch_custom":
                switch_info: dict = client.get_stateandswitch_info()
                window.open_custom_switchassign_setting(switch_info)
                window.mainloop()

                if not window.assigned_keywords:
                    raise InterruptedWAU("Not Assigned Switch/State Keywords.")
                waapi_thread = threading.Thread(
                    target=client.custom_assign_switch_container,
                    kwargs={
                        "window": window,
                        "stategrouptoassign": window.stategroup_name,
                        "assigned_keywords": window.assigned_keywords,
                    },
                )
            else:
                raise Exception("Not valid sys.argv[1]")

            waapi_thread.start()
            window.mainloop()

    except InterruptedWAU as e:
        print(f"InterruptedWAU: {str(e)}")

    except CannotConnectToWaapiException as e:
        window.result_error(
            "CannotConnectToWaapiException", f"{str(e)}\nIs Wwise running and Wwise Authoring API enabled?"
        )

    except Exception as e:
        window.result_error("ERROR", str(e))


if __name__ == "__main__":
    main()
