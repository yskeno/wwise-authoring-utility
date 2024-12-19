from waapi import WaapiClient, CannotConnectToWaapiException
import concurrent.futures, re, sys, functools
import WAU_GUI
import pprint


def common_substring(str_list: list[str]):
    def common(a: str, b: str):
        idx = 0
        for i, j, _ in zip(a, b, range(len(a))):
            if i != j:
                break
            idx = _ + 1
        return a[:idx]

    return "".join(functools.reduce(common, str_list))


def assign_switch_object(client: WaapiClient, root: WAU_GUI.MainWindow):

    selected_objects = client.call(
        "ak.wwise.ui.getSelectedObjects",
        {"options": {"return": ["id", "name", "type", "childrenCount", "@SwitchGroupOrStateGroup"]}},
    )["objects"]

    selected_switch_containers = []
    assigned_switch_groups = []

    # target for SwitchContainer with child and assigned SwitchGroup
    for obj in selected_objects:
        if (
            obj["type"] == "SwitchContainer"
            and obj["childrenCount"] != 0
            and obj["@SwitchGroupOrStateGroup"]["id"] != "{00000000-0000-0000-0000-000000000000}"
        ):
            selected_switch_containers.append(obj)
            assigned_switch_groups.append(
                {"id": obj["@SwitchGroupOrStateGroup"]["id"], "name": obj["@SwitchGroupOrStateGroup"]["name"]}
            )
    # Remove duplicate
    assigned_switch_groups = list({switch["id"]: switch for switch in assigned_switch_groups}.values())

    # make switch container dict
    switch_container_children = client.call(
        "ak.wwise.core.object.get",
        {
            "from": {"id": [i.get("id") for i in selected_switch_containers]},
            "transform": [{"select": ["children"]}],
            "options": {"return": ["id", "name", "parent"]},
        },
    )["return"]

    for swct_chld in switch_container_children:
        for sel_swct in selected_switch_containers:
            if swct_chld["parent"]["id"] == sel_swct["id"]:
                sel_swct.setdefault("children", [])
                sel_swct["children"].append({"id": swct_chld["id"], "name": swct_chld["name"]})
                break
            else:
                continue
    for sel_swct in selected_switch_containers:
        sel_swct["prefix"] = common_substring([n.get("name") for n in sel_swct.get("children")])

    print("=== selected_switch_containers ===")
    pprint.pprint(selected_switch_containers)

    # make switch group dict
    assigned_switch_children = client.call(
        "ak.wwise.core.object.get",
        {
            "from": {"id": [i.get("id") for i in assigned_switch_groups]},
            "transform": [{"select": ["children"]}],
            "options": {"return": ["id", "name", "parent"]},
        },
    )["return"]

    for switch_chld in assigned_switch_children:
        for asgn_swg in assigned_switch_groups:
            if switch_chld["parent"]["id"] == asgn_swg["id"]:
                asgn_swg.setdefault("children", [])
                asgn_swg["children"].append({"id": switch_chld["id"], "name": switch_chld["name"]})
                break
            else:
                continue
    for asgn_swg in assigned_switch_groups:
        asgn_swg["prefix"] = common_substring([n.get("name") for n in asgn_swg.get("children")])

    # assign sounds to each switch
    import re

    suffix = re.compile(r"[\s\d_\-,\(\)\[\]\{\}!\+=;]*$")

    for sel_swct in selected_switch_containers:
        swgp_in_swct = {}
        for asgn_swg in assigned_switch_groups:
            if sel_swct["@SwitchGroupOrStateGroup"]["id"] == asgn_swg["id"]:
                swgp_in_swct = asgn_swg
                break
            else:
                continue
        ssc_assigned = client.call("ak.wwise.core.switchContainer.getAssignments", {"id": sel_swct["id"]})["return"]
        ssc_assigned = [id.get("child") for id in ssc_assigned]
        for swct_chld in sel_swct["children"]:
            # skip sound if it's already assigned
            if swct_chld["id"] in ssc_assigned:
                continue
            for switch in swgp_in_swct["children"]:
                if (
                    re.sub(suffix, "", swct_chld["name"]).removeprefix(sel_swct["prefix"]).lower()
                    in switch["name"].removeprefix(swgp_in_swct["prefix"]).lower()
                ):
                    client.call(
                        "ak.wwise.core.switchContainer.addAssignment",
                        {"child": swct_chld["id"], "stateOrSwitch": switch["id"]},
                    )
                    break
                else:
                    continue


def main():
    root = WAU_GUI.MainWindow()

    with WaapiClient() as client, concurrent.futures.ThreadPoolExecutor() as executor:
        client.call("ak.wwise.core.undo.beginGroup")
        try:
            thread = executor.submit(assign_switch_object, client, root)

            # root.mainloop()
            result = thread.result()
            if result is not None:
                raise result

        except CannotConnectToWaapiException as e:
            root.show_error(
                "Cannot Connect To Waapi Exception", f"{str(e)}\n\nIs Wwise running and Wwise Authoring API enabled?"
            )

        except Exception as e:
            print("ERROR", str(e))

        finally:
            client.call("ak.wwise.core.undo.endGroup", {"displayName": "Auto assign objects to switches"})


if __name__ == "__main__":
    main()
