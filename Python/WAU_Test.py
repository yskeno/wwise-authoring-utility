from waapi import WaapiClient, CannotConnectToWaapiException
import sys, pprint


def main():
    print("=== sys.argv ===")
    print(sys.argv)
    print("================")
    try:
        with WaapiClient() as client:
            selected = client.call(
                "ak.wwise.ui.getSelectedObjects", {"options": {"return": ["id", "name", "type", "parent"]}}
            )["objects"]
            pprint.pprint(selected)

    except CannotConnectToWaapiException as e:
        print("CannotConnectToWaapiException", f"{str(e)}\nIs Wwise running and Wwise Authoring API enabled?")


if __name__ == "__main__":
    main()


[
    "C:\\Users\\yusuke.enomoto\\AppData\\Roaming\\Audiokinetic\\Wwise\\Add-ons\\Commands\\wwise-authoring-utility\\Python\\WAU_Test.py",
    "{65E2BE3B-48A9-4073-BE5D-0C628D73F1EE}",
    "Footstep_Crouching_Hardwood+{06}",
    "Sound",
    "\\Actor-Mixer Hierarchy\\Default Work Unit\\Footstep_Types\\FS_Crouching\\Footstep_Crouching_Hardwood+{06}",
]
