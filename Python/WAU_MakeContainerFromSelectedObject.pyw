from waapi import WaapiClient, CannotConnectToWaapiException
import concurrent.futures, re, sys
import WAU_GUI


def make_container_from_selected_obj(client: WaapiClient, root: WAU_GUI.MainWindow):
    selected_objects: list = client.call(
        "ak.wwise.ui.getSelectedObjects", {"options": {"return": ["id", "name", "type", "parent"]}}
    )["objects"]

    if selected_objects == None:
        raise Exception

    suffix = re.compile(r"[\s\d_\-,\(\)\[\]\{\}!\+=;]*$")
    container_list = []

    for selected in selected_objects:
        container_list.append({"name": re.sub(suffix, "", selected["name"]), "parent_id": selected["parent"]["id"]})
    tmp_seen = []
    container_list = [x for x in container_list if x not in tmp_seen and not tmp_seen.append(x)]

    for container in container_list:
        container_members = []
        for selected in selected_objects:
            if container["name"] in selected["name"] and container["parent_id"] == selected["parent"]["id"]:
                container_members.append(selected)

        if len(container_members) <= 1:
            continue

        created_container = client.call(
            "ak.wwise.core.object.create",
            {
                "parent": container["parent_id"],
                "onNameConflict": "rename",
                "type": "RandomSequenceContainer",
                "name": container["name"],
            },
        )
        for member in container_members:
            client.call(
                "ak.wwise.core.object.move",
                {"object": member["id"], "parent": created_container["id"], "onNameConflict": "fail"},
            )


def main():
    print(sys.argv[1])
    root = WAU_GUI.MainWindow()

    try:
        with WaapiClient() as client, concurrent.futures.ThreadPoolExecutor() as executor:
            thread = executor.submit(make_container_from_selected_obj, client, root)

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


if __name__ == "__main__":
    main()
