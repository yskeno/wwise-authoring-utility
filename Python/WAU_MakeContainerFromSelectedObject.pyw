from waapi import WaapiClient, CannotConnectToWaapiException
import concurrent.futures, re, sys
import WAU_GUI


def make_container_from_selected_obj(client: WaapiClient, root: WAU_GUI.MainWindow):
    selected_objects: list = client.call(
        "ak.wwise.ui.getSelectedObjects", {"options": {"return": ["id", "name", "type", "parent"]}}
    )["objects"]

    suffix = re.compile(r"[\s\d_\-,\(\)\[\]\{\}!\+=;]*$")
    target_containers = []

    for obj in selected_objects:
        target_containers.append({"name": re.sub(suffix, "", obj["name"]), "parent_id": obj["parent"]["id"]})
    tmp_seen = []
    target_containers = [x for x in target_containers if x not in tmp_seen and not tmp_seen.append(x)]

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

    number_of_created_container = 0
    for container in target_containers:
        container_children = []
        for obj in selected_objects:
            if container["name"] in obj["name"] and container["parent_id"] == obj["parent"]["id"]:
                container_children.append(obj)

        if len(container_children) <= 1:
            continue

        if type == "RandomSequenceContainer":
            created_container = client.call(
                "ak.wwise.core.object.create",
                {
                    "parent": container["parent_id"],
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
                    "parent": container["parent_id"],
                    "onNameConflict": "rename",
                    "type": type,
                    "name": container["name"],
                },
            )
            number_of_created_container += 1

        for container_child in container_children:
            client.call(
                "ak.wwise.core.object.move",
                {"object": container_child["id"], "parent": created_container["id"], "onNameConflict": "fail"},
            )


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
