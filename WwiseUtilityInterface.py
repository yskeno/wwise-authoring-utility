#! python3
import os
import re

from waapi import WaapiClient, CannotConnectToWaapiException
from WwiseUtilityGUI import MainWindow


class WwiseUtilityClient(WaapiClient):

    def _get_selected_objects_guid(self, type=''):
        selected = self.call("ak.wwise.ui.getSelectedObjects", {
            'options': {'return': ['id', 'type']}})['objects']
        if type == '':
            return tuple(v for d in selected for k, v in d.items() if k == 'id')
        else:
            return tuple(v for d in selected if d['type'] == type
                         for k, v in d.items() if k == 'id')

    def _get_name_from_guid(self, guids: tuple):
        objects = self.call("ak.wwise.core.object.get",
                            {"from": {"id": list(guids)},
                             "options": {"return": ['name']}})['return']
        return tuple(obj['name'] for obj in objects)

    def connect_to_localhost(self, window: MainWindow):
        window.after_idle(lambda: window.set_current_process(
            20, 'Get Connection Status...'))
        connection_status: dict = self.call(
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

        # --- Disconnect from Localhost ---
        else:
            window.after_idle(lambda: window.set_current_process(
                50, 'Disconnect from remote pratform...'))
            self.call('ak.wwise.core.remote.disconnect')
            window.after_idle(lambda: window.set_current_process(
                100, 'Disconnected.'))

        window.close_window()

    def auto_rename_container(self, window: MainWindow):
        guids = self._get_selected_objects_guid()

        failed_ids = set()
        for guid in guids:
            children = self.call("ak.wwise.core.object.get",
                                 {"from": {"id": [guid]},
                                  "transform": [{"select": ['children']}],
                                  "options": {"return": ['name']}})['return']
            if children is None:
                failed_ids.add(guid)
                continue

            names = list(map(lambda object: object['name'], children))
            common_name = os.path.commonprefix(names).rstrip('_ -0')
            if not common_name:
                failed_ids.add(guid)
                continue

            self.call("ak.wwise.core.object.setName", {
                      "object": guid, "value": common_name})

        if len(failed_ids) > 0:
            if len(failed_ids) == len(guids):
                window.result_error(
                    'Auto rename failed', f"Could not rename object(s):\n\n Check using common words between children's object.")
            else:
                failed_names = '\n'.join(
                    self._get_name_from_guid(tuple(failed_ids)))
                window.result_warning(
                    'Complete with Warning', f"Complete but following container(s) wasn\'t renamed:\n\n{failed_names}")
        else:
            window.close_window()

    def auto_assign_switch_container(self, window: MainWindow):
        guids = self._get_selected_objects_guid(type='SwitchContainer')

        failed_ids = set()
        for guid in guids:
            isassigned = False
            stategroup = self.call("ak.wwise.core.object.get",
                                   {"from": {"id": [guid]},
                                    "options": {"return": ['@SwitchGroupOrStateGroup']}}
                                   )['return'][0]['@SwitchGroupOrStateGroup']
            if stategroup is None or stategroup['id'] == '{00000000-0000-0000-0000-000000000000}':
                failed_ids.add(guid)
                continue

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
            if not common_name:
                failed_ids.add(guid)
                continue
            if not common_name.endswith(('_', ' ', '-')):
                common_name = common_name[:common_name.rfind('_ -')]

            assignments = self.call(
                'ak.wwise.core.switchContainer.getAssignments', {'id': guid})['return']

            for child in children:
                target_name = re.sub(
                    '[_ -]*[0-9]+$', '', child['name'].replace(common_name, ""))
                for state in states:
                    if state['name'] == 'None':
                        continue
                    if target_name in state['name']:
                        for assignment in assignments:
                            if assignment['child'] == child['id'] and assignment['stateOrSwitch'] == state['id']:
                                break
                        else:
                            self.call('ak.wwise.core.switchContainer.addAssignment',
                                      {"child": child['id'], "stateOrSwitch": state['id']})
                            isassigned = True
                            continue
            if not isassigned:
                failed_ids.add(guid)

        if len(failed_ids) > 0:
            if len(failed_ids) == len(guids):
                window.result_error(
                    'Switch Assignment Not Complete', f"Could not assign object(s):\n\n Check SwitchContainer's State/Switch Group\n and use common words between object and state.")
            else:
                failed_names = '\n'.join(
                    self._get_name_from_guid(tuple(failed_ids)))
                window.result_warning(
                    'Complete with Warning', f"Finished but following object(s) wasn't assigned:\n\n{failed_names}")
        else:
            window.close_window()

    def custom_assign_switch_container(self, window):
        # TODO:Write function.
        pass

    def auto_trim_wavefile(self, window):
        # TODO:Write function.
        pass
