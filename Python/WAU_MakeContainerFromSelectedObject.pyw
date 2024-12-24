from waapi import WaapiClient, CannotConnectToWaapiException
import concurrent.futures, re, sys, functools
import WAU_GUI


class NoChildWithCommonPrefix(Exception):
    pass


def common_substring(str_list: list[str]):
    def common(a: str, b: str):
        idx = 0
        for i, j, _ in zip(a, b, range(len(a))):
            if i != j:
                break
            idx = _ + 1
        return a[:idx]

    return "".join(functools.reduce(common, str_list))


def make_container_from_selected_obj(client: WaapiClient, root: WAU_GUI.MainWindow):
    selected_objects: list = client.call(
        "ak.wwise.ui.getSelectedObjects", {"options": {"return": ["id", "name", "type", "parent"]}}
    )["objects"]

    # extract common prefix for the objects without numbering suffix
    targets_to_create = []
    for obj in selected_objects:
        if obj["parent"]["id"] in [i["parent"]["id"] for i in targets_to_create]:
            target = [p for p in targets_to_create if p["parent"]["id"] == obj["parent"]["id"]][0]
            target["children"].append({"name": obj["name"], "id": obj["id"]})
            target["numberedChild"] = False
            target["container"] = []
        else:
            targets_to_create.append(
                {
                    "parent": {"id": obj["parent"]["id"], "name": obj["parent"]["name"]},
                    "children": [{"name": obj["name"], "id": obj["id"]}],
                    "numberedChild": False,
                    "container": [],
                }
            )

    # switch container type from argument
    type = ""
    randomorsequence = 0
    if len(sys.argv) > 1:
        if sys.argv[1] == "switch":
            type = "SwitchContainer"
        elif sys.argv[1] == "blend":
            type = "BlendContainer"
        elif sys.argv[1] == "sequence":
            type = "RandomSequenceContainer"
        else:
            type = "RandomSequenceContainer"
            randomorsequence = 1
    else:
        type = "RandomSequenceContainer"

    # make common string with removing number for the objects with numbered suffix,
    # make common string from the longest common string for the objects without numbered suffix
    number_of_created_container = 0
    suffix = re.compile(r"[\d\s_\-,\(\)\[\]\{\}!\+=;]*$")
    for target in targets_to_create:
        for child in target["children"]:
            if (prefix := re.sub(suffix, "", child["name"])) != child["name"]:
                target["numberedChild"] = True

            if prefix in [n.get("name") for n in target["container"]]:
                container = [c for c in target["container"] if c["name"] == prefix][0]
                container["member"].append(child)
                continue
            else:
                target["container"].append({"name": prefix, "member": [child]})
                continue

        if target["numberedChild"] == False:
            target["container"] = [
                {
                    "name": re.sub(suffix, "", common_substring([n["name"] for n in target["container"]])),
                    "member": [m for c in target["container"] for m in c["member"]],
                }
            ]

        for container in target["container"]:
            # if container with no member, not create container
            if len(container["member"]) <= 1:
                continue

            if type == "RandomSequenceContainer":
                created_container = client.call(
                    "ak.wwise.core.object.create",
                    {
                        "parent": target["parent"]["id"],
                        "onNameConflict": "rename",
                        "type": type,
                        "name": container["name"],
                        "@RandomOrSequence": randomorsequence,
                    },
                )
                number_of_created_container += 1
            else:
                created_container = client.call(
                    "ak.wwise.core.object.create",
                    {
                        "parent": target["parent"]["id"],
                        "onNameConflict": "rename",
                        "type": type,
                        "name": container["name"],
                    },
                )
                number_of_created_container += 1

            for member in container["member"]:
                client.call(
                    "ak.wwise.core.object.move",
                    {"object": member["id"], "parent": created_container["id"], "onNameConflict": "fail"},
                )

    if number_of_created_container == 0:
        raise NoChildWithCommonPrefix


def main():
    root = WAU_GUI.MainWindow()

    try:
        with WaapiClient() as client, concurrent.futures.ThreadPoolExecutor() as executor:
            try:
                client.call("ak.wwise.core.undo.beginGroup")
                thread = executor.submit(make_container_from_selected_obj, client, root)
                result = thread.result()
                if result is not None:
                    raise result
            except NoChildWithCommonPrefix:
                root.show_error(
                    "Operation incompleted",
                    "Not found common name in selected objects.\nSelect objects with general suffix. (SAMPLE_01, SAMPLE_02 ...)",
                )
            except Exception as e:
                root.show_error("Exception", str(e))

            else:
                client.call("ak.wwise.core.undo.endGroup", {"displayName": "Create Container from selected objects"})
                client.disconnect()
    except CannotConnectToWaapiException as e:
        root.show_error(
            "Cannot Connect To Waapi Exception", f"{str(e)}\n\nIs Wwise running and Wwise Authoring API enabled?"
        )
    except Exception as e:
        root.show_error("Exception", str(e))


if __name__ == "__main__":
    main()
