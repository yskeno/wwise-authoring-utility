import os
import re

from waapi import WaapiClient, CannotConnectToWaapiException, WaapiRequestFailed
from WwiseUtilityGUI import MainWindow


class WwiseUtilityClient(WaapiClient):
    @staticmethod
    def waapi_call(func):
        def wrapper(self, *args, **kwargs):
            window: MainWindow = None
            if kwargs.get('window', None):
                window = kwargs['window']

            try:
                func(self, *args, **kwargs)
                window.result_success(
                    'Complete', f'Complete successfully.')
            except CannotConnectToWaapiException as e:
                window.result_error('CannotConnectToWaapiException',
                                    f'{str(e)}\nIs Wwise running and Wwise Authoring API enabled?')
            except WaapiRequestFailed as e:
                window.result_error('WaapiRequestFailed', f'{e}')
            except RuntimeError as e:
                window.result_error('RuntimeError', f'{e}')
            except RuntimeWarning as e:
                window.result_warning('RuntimeWarning', f'{e}')
            except Exception as e:
                import traceback
                window.result_error(
                    'Error', f'{e}\n\n{traceback.format_exc()}')
            finally:
                self.disconnect()
                window.close_window()
        return wrapper

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

    @waapi_call
    def connect_to_localhost(self, window: MainWindow):
        window.show_progress_window()
        window.after_idle(lambda: window.set_current_process(
            20, 'Get Connection Status...'))
        connection_status: dict = self.call(
            'ak.wwise.core.remote.getConnectionStatus')
        print(f'*** ConnectionStatus= {connection_status}')

        # --- Connect to Localhost ---
        if connection_status.get('isConnected', None) == False:
            window.after_idle(lambda: window.set_current_process(
                30, 'Get Available Consoles...'))
            available_consoles: list = self.call(
                'ak.wwise.core.remote.getAvailableConsoles')['consoles']

            # Search Localhosts.
            window.after_idle(lambda: window.set_current_process(
                50, 'Search localhosts...'))
            local_consoles = [
                console for console in available_consoles if console['host'] == '127.0.0.1']
            if len(local_consoles) == 0:
                raise RuntimeError('Localhost was not found.')

            # Select Localhost to connect.
            # If multiple Localhost was found, choose one not including 'Edit'
            window.after_idle(lambda: window.set_current_process(
                70, 'Set target console...'))
            target_console: dict = {}
            if len(local_consoles) == 1:
                target_console = local_consoles[0]
            else:
                for local_console in local_consoles:
                    if 'edit' not in local_console['appName'].lower():
                        target_console = local_console
                        break
                else:
                    target_console = local_consoles[0]

            print(f'*** Connect to {target_console}')
            window.after_idle(lambda: window.set_current_process(
                85, f'Connect to {target_console["appName"]}...'))
            self.call('ak.wwise.core.remote.connect', {
                'host': target_console['host'], 'appName': target_console['appName']})
            window.after_idle(lambda: window.set_current_process(
                100, 'Connected.'))

        # --- Disconnect from Localhost ---
        else:
            window.after_idle(lambda: window.set_current_process(
                50, 'Disconnect from remote pratform...'))
            self.call('ak.wwise.core.remote.disconnect')
            window.after_idle(lambda: window.set_current_process(
                100, 'Disconnected.'))

    @waapi_call
    def auto_rename_container(self, window: MainWindow):
        guids: tuple = self._get_selected_objects_guid()

        failed_ids = set()
        for guid in guids:
            children: list = self.call("ak.wwise.core.object.get",
                                       {"from": {"id": [guid]},
                                        "transform": [{"select": ['children']}],
                                        "options": {"return": ['name']}})['return']
            if children is None:
                failed_ids.add(guid)
                continue

            names = list(map(lambda object: object['name'], children))
            common_name: str = os.path.commonprefix(names).rstrip('_ -0')
            if not common_name:
                failed_ids.add(guid)
                continue
            print(f'*** CommonName= {common_name}')

            self.call("ak.wwise.core.object.setName", {
                      "object": guid, "value": common_name})

        if len(failed_ids) > 0:
            if len(failed_ids) == len(guids):
                raise RuntimeError(
                    f'Auto rename failed:\n\n Could not rename object(s).\n Check using common words between children\'s object.')
            else:
                failed_names = '\n    '.join(
                    self._get_name_from_guid(tuple(failed_ids)))
                print(f'*** FailedName= {failed_names}')
                raise RuntimeWarning(
                    f'Complete with Warning.\n\n Following container(s) wasn\'t renamed:\n    {failed_names}')

    @waapi_call
    def auto_assign_switch_container(self, window: MainWindow):
        guids: tuple = self._get_selected_objects_guid(type='SwitchContainer')

        failed_ids = set()
        for guid in guids:
            isassigned = False
            stategroup: dict = self.call("ak.wwise.core.object.get",
                                         {"from": {"id": [guid]},
                                          "options": {"return": ['@SwitchGroupOrStateGroup']}}
                                         )['return'][0]['@SwitchGroupOrStateGroup']
            if stategroup is None or stategroup['id'] == '{00000000-0000-0000-0000-000000000000}':
                failed_ids.add(guid)
                continue

            states: list = self.call("ak.wwise.core.object.get",
                                     {"from": {"id": [stategroup['id']]},
                                      "transform": [{"select": ['children']}],
                                      "options": {"return": ['id', 'name']}}
                                     )['return']

            children: list = self.call("ak.wwise.core.object.get",
                                       {"from": {"id": [guid]},
                                        "transform": [{"select": ['children']}],
                                        "options": {"return": ['id', 'name']}}
                                       )['return']

            common_name: str = os.path.commonprefix(
                list(map(lambda object: object['name'], children)))
            if not common_name:
                failed_ids.add(guid)
                continue
            if not common_name.endswith(('_', ' ', '-')):
                common_name = common_name[:common_name.rfind('_ -')]
            print(f'*** CommonName= {common_name}')

            assignments: list = self.call(
                'ak.wwise.core.switchContainer.getAssignments', {'id': guid})['return']

            for child in children:
                target_name: str = re.sub(
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
                raise RuntimeError(
                    f'Could not assign object(s):\n\n Check setting SwitchContainer\'s Switch \n and use common words between object and switch.')
            else:
                failed_names = '\n    '.join(
                    self._get_name_from_guid(tuple(failed_ids)))
                raise RuntimeWarning(
                    f'Complete with Warning.\n\n Following SwitchContainer(s) wasn\'t assigned:\n    {failed_names}')

    def custom_assign_switch_container(self, window):
        # TODO:Write function.
        pass

    def auto_trim_wavefile(self, window):
        # TODO:Write function.
        pass
