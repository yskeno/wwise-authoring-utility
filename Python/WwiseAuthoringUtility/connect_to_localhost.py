import sys
import threading

from WwiseUtilityInterface import WwiseUtilityClient, CannotConnectToWaapiException
import WwiseAuthoringUtility.WwiseAuthoringUtilityUI as WwiseAuthoringUtilityUI

help_text = """usage: Wwise Authoring Utility help you to control Wwise."""


class InterruptedWAU(Exception):
    pass


def main():
    window = WwiseAuthoringUtilityUI.MainWindow()

    try:
        with WwiseUtilityClient() as client:
            waapi_thread: threading.Thread = threading.Thread(
                target=client.connect_to_localhost,
                kwargs={
                    "window": window,
                },
            )

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
