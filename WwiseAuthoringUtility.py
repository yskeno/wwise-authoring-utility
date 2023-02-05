from waapi import WaapiClient, CannotConnectToWaapiException
import argparse


def main():
    parser = argparse.ArgumentParser(
        usage="WwiseAuthoringUtility help you to control Wweise.", description="Add arg.",)
    parser.add_argument(
        "-r", "--remote", help="Connect/Disconnect to localhost.")

    # args = parser.parse_args()
    # if args is None:
    #     return

    try:
        with WaapiClient() as client:

            connect_to_localhost(client)

    except CannotConnectToWaapiException:
        print(
            "Could not connect to Waapi: Is Wwise running and Wwise Authoring API enabled?")

    except Exception as e:
        print(str(e))


def connect_to_localhost(client):
    connection_status = client.call(
        "ak.wwise.core.remote.getConnectionStatus")
    # --- Connect to Localhost ---
    if connection_status.get('isConnected', None) == False:
        available_consoles: dict = client.call(
            "ak.wwise.core.remote.getAvailableConsoles")

        # Search Localhosts.
        local_consoles = [
            item for item in available_consoles['consoles'] if item['host'] == "127.0.0.1"]
        if len(local_consoles) == 0:
            raise Exception('Localhost was not found.')

        # Select Localhost to connect.
        # If multiple Localhost was found, choose one not including "Edit"
        target_console = {}
        if len(local_consoles) == 1:
            target_console = local_consoles[0]
        else:
            for local_console in local_consoles:
                if local_console['appName'].lower() not in "edit":
                    target_console = local_console
                    break
            if target_console == {}:
                target_console = local_consoles[0]

        client.call("ak.wwise.core.remote.connect", {
                    'host': target_console.get('host', ""), 'appName': target_console.get('appName', "")})

    # --- Disconnect from Localhost ---
    else:
        client.call("ak.wwise.core.remote.disconnect")


if __name__ == "__main__":
    main()
