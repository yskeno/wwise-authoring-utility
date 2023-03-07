#! python3
import os
import re

from waapi import WaapiClient, CannotConnectToWaapiException


class WwiseUtilityClient(WaapiClient):
    def _get_selected_objects_guid(self):
        selected = self.call("ak.wwise.ui.getSelectedObjects")['objects']
        return tuple(v for d in selected
                     for k, v in d.items() if k == 'id')

    def connect_to_localhost(self, window):
        window.after_idle(lambda: window.set_current_process(
            20, 'Get Connection Status...'))
        connection_status = self.call(
            'ak.wwise.core.remote.getConnectionStatus')

        # --- Connect to Localhost ---
        if connection_status.get('isConnected', None) == False:
            window.after_idle(lambda: window.set_current_process(
                30, 'Get Available Consoles...'))
            available_consoles: dict = self.call(
                'ak.wwise.core.remote.getAvailableConsoles')

            # Search Localhosts.
            window.after_idle(lambda: window.set_current_process(
                50, 'Search localhosts...'))
            local_consoles = [
                item for item in available_consoles['consoles'] if item['host'] == '127.0.0.1']
            if len(local_consoles) == 0:
                window.show_error('Error', 'Localhost was not found.')
                return

            # Select Localhost to connect.
            # If multiple Localhost was found, choose one not including 'Edit'
            window.after_idle(lambda: window.set_current_process(
                70, 'Set target console...'))
            target_console = {}
            if len(local_consoles) == 1:
                target_console = local_consoles[0]
            else:
                for local_console in local_consoles:
                    if 'edit' not in local_console['appName'].lower():
                        target_console = local_console
                        break
                else:
                    target_console = local_consoles[0]

            window.after_idle(lambda: window.set_current_process(
                85, 'Connect to localhost...'))

            self.call('ak.wwise.core.remote.connect', {
                'host': target_console.get('host', ''), 'appName': target_console.get('appName', '')})

            window.after_idle(lambda: window.set_current_process(
                100, 'Connected.'))
            window.after_idle(window.process_complete)

        # --- Disconnect from Localhost ---
        else:
            window.after_idle(lambda: window.set_current_process(
                50, 'Disconnect from remote pratform...'))

            self.call('ak.wwise.core.remote.disconnect')
            window.after_idle(lambda: window.set_current_process(
                100, 'Disconnected.'))
            window.after_idle(window.process_complete)

    def auto_rename_container(self, window, *guids):
        if len(guids) == 0:
            guids = self._get_selected_objects_guid()

        failed_results = []
        for guid in guids:
            children = self.call("ak.wwise.core.object.get",
                                 {"from": {"id": [guid]},
                                  "transform": [{"select": ['children']}],
                                  "options": {"return": ['name']}})['return']

            names = list(map(lambda object: object['name'], children))
            common_name = os.path.commonprefix(names).rstrip('_ -0')

            if not common_name:
                container = self.call("ak.wwise.core.object.get",
                                      {"from": {"id": [guid]},
                                       "options": {"return": ['name']}})['return']
                failed_results.append(container[0]['name'])
                continue

            self.call("ak.wwise.core.object.setName", {
                      "object": guid, "value": common_name})

        if len(failed_results) > 0:
            window.show_warning(
                'Partially Complete', f'Complete but following container(s) wasn\'t renamed:\n No common prefix found.\n{failed_results}')
        window.after_idle(window.process_complete)

    def auto_assign_switch_container(self, window, *guids):
        if len(guids) == 0:
            guids = self._get_selected_objects_guid()

        failed_results = []
        for guid in guids:
            stategroup = self.call("ak.wwise.core.object.get",
                                   {"from": {"id": [guid]},
                                    "options": {"return": ['SwitchGroupOrStateGroup']}}
                                   )['return'][0]['SwitchGroupOrStateGroup']
            states = self.call("ak.wwise.core.object.get",
                               {"from": {"id": [stategroup['id']]},
                                "transform": [{"select": ['children']}],
                                "options": {"return": ['id', 'name']}}
                               )['return']

            children = self.call("ak.wwise.core.object.get",
                                 {"from": {"id": [guid]},
                                  "transform": [{"select": ['children']}],
                                  "options": {"return": ['id', 'name']}}
                                 )['return']
            common_name = os.path.commonprefix(
                list(map(lambda object: object['name'], children)))

            for child in children:
                target_name = re.sub(
                    '[_ -]*[0-9]+$', '', child['name'].replace(common_name, ""))
                for state in states:
                    if target_name in state['name']:
                        self.call('ak.wwise.core.switchContainer.addAssignment',
                                  {"child": child['id'], "stateOrSwitch": state['id']})
                        break
                else:
                    failed_results.append(child['name'])

        if len(failed_results) > 0:
            window.show_warning(
                'Partially Complete', f'Finished but following object(s) wasn\'t assigned:\n No common words between object and state.\n{failed_results}')
        window.after_idle(window.process_complete)

    def auto_trim_wavefile(self, window, *guid):
        # TODO:Write function.
        pass
