from waapi import WaapiClient, CannotConnectToWaapiException
import concurrent.futures, functools
import WAU_GUI


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

    selected_sw_containers = []
    assigned_sw_groups = []

    # target for SwitchContainer with child and assigned SwitchGroup
    for obj in selected_objects:
        if (
            obj["type"] == "SwitchContainer"
            and obj["childrenCount"] != 0
            and obj["@SwitchGroupOrStateGroup"]["id"] != "{00000000-0000-0000-0000-000000000000}"
        ):
            selected_sw_containers.append(obj)
            assigned_sw_groups.append(
                {"id": obj["@SwitchGroupOrStateGroup"]["id"], "name": obj["@SwitchGroupOrStateGroup"]["name"]}
            )
    # Remove duplicate
    assigned_sw_groups = list({switch["id"]: switch for switch in assigned_sw_groups}.values())

    # make switch container dict
    selected_sw_container_children = client.call(
        "ak.wwise.core.object.get",
        {
            "from": {"id": [i.get("id") for i in selected_sw_containers]},
            "transform": [{"select": ["children"]}],
            "options": {"return": ["id", "name", "parent"]},
        },
    )["return"]

    for selected_sw_container_child in selected_sw_container_children:
        for selected_sw_container in selected_sw_containers:
            if selected_sw_container_child["parent"]["id"] == selected_sw_container["id"]:
                selected_sw_container.setdefault("children", [])
                selected_sw_container["children"].append(
                    {"id": selected_sw_container_child["id"], "name": selected_sw_container_child["name"]}
                )
                break
            else:
                continue
    for selected_sw_container in selected_sw_containers:
        selected_sw_container["prefix"] = common_substring(
            [n.get("name") for n in selected_sw_container.get("children")]
        )

    # make switch group dict
    assigned_sw_children = client.call(
        "ak.wwise.core.object.get",
        {
            "from": {"id": [i.get("id") for i in assigned_sw_groups]},
            "transform": [{"select": ["children"]}],
            "options": {"return": ["id", "name", "parent"]},
        },
    )["return"]

    for assigned_sw_child in assigned_sw_children:
        for assigned_sw_group in assigned_sw_groups:
            if assigned_sw_child["parent"]["id"] == assigned_sw_group["id"]:
                assigned_sw_group.setdefault("children", [])
                assigned_sw_group["children"].append(
                    {"id": assigned_sw_child["id"], "name": assigned_sw_child["name"]}
                )
                break
            else:
                continue
    for assigned_sw_group in assigned_sw_groups:
        assigned_sw_group["prefix"] = common_substring([n.get("name") for n in assigned_sw_group.get("children")])

    # assign sounds to each switch
    import re

    suffix = re.compile(r"[\s\d_\-,\(\)\[\]\{\}!\+=;]*$")

    for selected_sw_container in selected_sw_containers:
        sw_group_in_selected = {}
        for assigned_sw_group in assigned_sw_groups:
            if selected_sw_container["@SwitchGroupOrStateGroup"]["id"] == assigned_sw_group["id"]:
                sw_group_in_selected = assigned_sw_group
                break
            else:
                continue
        assigned_container_children = client.call(
            "ak.wwise.core.switchContainer.getAssignments", {"id": selected_sw_container["id"]}
        )["return"]
        assigned_container_children = [id.get("child") for id in assigned_container_children]
        for selected_sw_container_child in selected_sw_container["children"]:
            # skip sound if it's already assigned
            if selected_sw_container_child["id"] in assigned_container_children:
                continue
            for switch in sw_group_in_selected["children"]:
                if (
                    re.sub(suffix, "", selected_sw_container_child["name"])
                    .removeprefix(selected_sw_container["prefix"])
                    .lower()
                    in switch["name"].removeprefix(sw_group_in_selected["prefix"]).lower()
                ):
                    client.call(
                        "ak.wwise.core.switchContainer.addAssignment",
                        {"child": selected_sw_container_child["id"], "stateOrSwitch": switch["id"]},
                    )
                    break
                else:
                    continue


def main():
    root = WAU_GUI.MainWindow()

    try:
        with WaapiClient() as client, concurrent.futures.ThreadPoolExecutor() as executor:
            client.call("ak.wwise.core.undo.beginGroup")
            try:
                thread = executor.submit(assign_switch_object, client, root)
                result = thread.result()
                if result is not None:
                    raise result
            except Exception as e:
                root.show_error("Exception", str(e))
            else:
                client.call("ak.wwise.core.undo.endGroup", {"displayName": "Auto assign objects to switches"})
    except CannotConnectToWaapiException as e:
        root.show_error(
            "Cannot Connect To Waapi Exception", f"{str(e)}\n\nIs Wwise running and Wwise Authoring API enabled?"
        )
    except Exception as e:
        root.show_error("Exception", str(e))


if __name__ == "__main__":
    main()
