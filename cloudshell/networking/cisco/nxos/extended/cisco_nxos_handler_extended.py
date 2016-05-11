__author__ = 'CoYe'

from cloudshell.networking.cisco.cisco_handler_base import CiscoHandlerBase
import re


class CiscoNXOSHandlerExtended(CiscoHandlerBase):
    def __init__(self, connection_manager, logger=None):
        CiscoHandlerBase.__init__(self, connection_manager, logger)
        self.supported_os = ['NXOS', 'NX-OS']

    def add_vlan(self, vlan_range, port_list, port_mode, additional_info):
        self.save_port_config(port_list)
        self._logger.info('Starting add_vlan in extended with {} , {}'.format(port_list, port_mode))
        # self.configure_port_channel(port_channel_id='0', port_list=port_list)
        result = CiscoHandlerBase.add_vlan(self, vlan_range, port_list, port_mode, additional_info)
        self.configure_interface_speed(port_list)
        self.configure_interface_mtu(port_list)
        return result

    def remove_vlan(self, vlan_range, port_list, port_mode, additional_info):
        result = CiscoHandlerBase.remove_vlan(self, vlan_range, port_list, port_mode, additional_info)
        self.restore_port_config(port_list)
        return result

    def get_service_attr_val(self, port, attr_name):
        """ Get value of speed attribute on the VLAN service
        Get the DUT port, get the service name, service attrs
        :param port:
        :return:
        """
        self._logger.info('Looking for {} in service {}'.format(attr_name, port))

        if '/' not in port:
            self._logger.error('Interface was not found')
            raise Exception('Interface was not found')
        port_name = port.split('/')[-1].replace('-', '/')

        try:
            dut_port = self.cloud_shell_api.GetResourceDetails(port).Connections[0].FullPath
        except:
            self._logger.info('No DUT connected to port {}'.format(port_name))
            return "No DUT connected"

        vlan_serv = ''
        for conn in self.cloud_shell_api.GetReservationDetails(self.reservation_dict['ReservationId']).ReservationDescription.Connectors:
            if conn.Source in dut_port:
                vlan_serv = conn.Target
                break
            elif conn.Target in dut_port:
                vlan_serv = conn.Source
                break
        if vlan_serv == '':
            self._logger.info('Could not find a connected service to {0}'.format(port_name))
            return "No service connected"

        for serv in self.cloud_shell_api.GetReservationDetails(self.reservation_dict['ReservationId']).ReservationDescription.Services:
            if serv.Alias == vlan_serv:
                for attr in serv.Attributes:
                    if attr.Name.lower() == attr_name.lower():
                        return attr.Value

        return "Cound not find {}".format(attr_name)

    def get_link_attr_val(self, port, attr_name):
        """ Get value of speed attribute on the VLAN service
        Get the DUT port, get the service name, service attrs
        :param port:
        :return:
        """
        self._logger.info('Looking for {} in service {}'.format(attr_name, port))

        if '/' not in port:
            self._logger.error('Interface was not found')
            raise Exception('Interface was not found')
        port_name = port.split('/')[-1].replace('-', '/')

        try:
            dut_port = self.cloud_shell_api.GetResourceDetails(port).Connections[0].FullPath
        except:
            self._logger.info('No DUT connected to port {}'.format(port_name))
            return "No DUT connected"

        for conn in self.cloud_shell_api.GetReservationDetails(self.reservation_dict['ReservationId']).ReservationDescription.Connectors:
            if conn.Source in dut_port or conn.Target in dut_port:
                for attr in conn.Attributes:
                    if attr.Name == attr_name:
                        return attr.Value


        self._logger.info('Could not find a connected service to {0}'.format(port_name))
        return "No {} found".format(attr_name)




    # def configure_interface_speed(self, speed, port_list):
    def configure_interface_speed(self, port_list):
        """
        Configure speed on each interface
        :param port_list: List of interfaces Resource Full Address
        :param speed: speed to be configured
        :return: success message
        :rtype: string
        """
        self._logger.info('Speed Configuration Started')
        if len(port_list) < 1:
            raise Exception('Port list is empty')

        port_resource_map = self.cloud_shell_api.GetResourceDetails(self.attributes_dict['ResourceName'])

        for port in port_list.split('|'):
            temp_port_name = self._get_resource_full_name(port, port_resource_map)
            speed = self.get_link_attr_val(temp_port_name, 'Link speed')
            if not re.match('\d+', speed):
                self._logger.info('Could not find speed for {}'.format(temp_port_name))
                continue

            if '/' not in temp_port_name:
                self._logger.error('Interface was not found')
                raise Exception('Interface was not found')
            port_name = temp_port_name.split('/')[-1].replace('-', '/')
            if 'channel' in port_name.lower():
                port_name = port_name.replace('/', '-')

            # Update speed on device
            if not re.search('^speed', (self._send_command('show running-config interface ' + port_name)).lower()):
                self.send_commands_list(['interface ' + port_name, 'speed ' + speed])
                self._exit_configuration_mode()
            self._logger.info('Interface {0} was configured for speed {1}'.format(port_name, speed))

            # Update speed on RM
            # self.cloud_shell_api.SetAttributeValue(temp_port_name, 'Bandwidth', int(speed)*1000*1000)
        return 'Interface Speed Configuration Completed'

    # def configure_interface_mtu(self, mtu, port_list):
    def configure_interface_mtu(self, port_list):
        """
        Configure MTU on each interface
        :param port_list: List of interfaces Resource Full Address
        :return: success message
        :rtype: string
        """
        self._logger.info('MTU Configuration Started')
        if len(port_list) < 1:
            raise Exception('Port list is empty')

        port_resource_map = self.cloud_shell_api.GetResourceDetails(self.attributes_dict['ResourceName'])

        # No MTU configuration on NxOS
        if port_resource_map.ResourceModelName == 'Cisco NXOS Switch':
            return 'No Interface MTU Configuration for Nexus OS'

        for port in port_list.split('|'):
            temp_port_name = self._get_resource_full_name(port, port_resource_map)
            mtu = self.get_link_attr_val(temp_port_name, 'Link MTU')
            if not re.match('\d', mtu):
                self._logger.info('Could not find MTU for {}'.format(temp_port_name))
                continue

            if '/' not in temp_port_name:
                self._logger.error('Interface was not found')
                raise Exception('Interface was not found')
            port_name = temp_port_name.split('/')[-1].replace('-', '/')
            self._logger.info('Interface {0} will be configured for MTU {1}'.format(port_name, mtu))
            if 'channel' in port_name.lower():
                port_name = port_name.replace('/', '-')

            # Update mtu on device
            if not re.search('^mtu', (self._send_command('show running-config interface ' + port_name)).lower()):
                self.send_commands_list(['interface ' + port_name, 'mtu ' + mtu])
                self._exit_configuration_mode()
            self._logger.info('Interface {0} was configured for MTU {1}'.format(port_name, mtu))

            # Update mtu on RM
            # self.cloud_shell_api.SetAttributeValue(temp_port_name, 'MTU', mtu)
        return 'Interface MTU Configuration Completed'


    # def configure_port_channel(self, port_channel_id, port_list):
    def create_portchannel(self, port_list, port_channel_id='0'):
        """
        Create a port-channel and adds interfaces to the port-channel
        :param port_channel_id: Find a port-channel if port-channel-id == 0
        :param port_list: listof ports separated by "|"
        :return:
        """

        self._logger.info('Port-Channel Configuration Started')
        self._logger.info(self.reservation_dict)

        # get root resource info
        port_resource_map = self.cloud_shell_api.GetResourceDetails(self.attributes_dict['ResourceName'])

        # default values work for IOS
        max_port_chann = 65
        port_chann_str = 'Port-channel'

        # Values specific to NxOS
        if port_resource_map.ResourceModelName == 'Cisco NXOS Switch':
            max_port_chann = 4095
            port_chann_str = 'port-channel'

        # Exit if port channel id is invalid
        if int(port_channel_id) > max_port_chann:
            self._logger.error('Incorrect Port Channel Id {}'.format(port_channel_id))
            raise Exception('Incorrect Port Channel Id {}'.format(port_channel_id))

        # Create list of existing port channel on switch
        port_channels = [line.strip('interface ' + port_chann_str) for line in
                         self._send_command('show running-config | include ' + port_chann_str).splitlines()
                         if line.startswith('interface')]

        # if port-channel id is not provided, find next available port-channel
        # if port-channel exists dont create, just update attribute
        if port_channel_id == '0':
            for port_chann in range(1, max_port_chann):
                if str(port_chann) not in port_channels:
                    port_channel_id = str(port_chann)
                    break
            if port_channel_id == '0':
                self._logger.error('Could not find availabe Port channel')
                raise Exception('Could not find availabe Port channel')

        # Create port channel on switch
        if port_channel_id not in port_channels:
            commands_list = list()
            commands_list.append('interface port-channel ' + port_channel_id)
            commands_list.append('switchport')
            commands_list.append('description "{0}"'.format(self.reservation_dict['ReservationId']))
            self.send_commands_list(commands_list)
            self._exit_configuration_mode()
            self._logger.info('{0} was created'.format(port_channel_id))

        # Add interfaces to port channel
        exclude_list = list() # Ports do not have L2 connection
        for port in port_list.split(';'):
            # Get the connected L2 port
            try:
                temp_port_name = self.cloud_shell_api.GetResourceDetails(port).Connections[0].FullPath
            except:
                self._logger.info('Could not find L2 port connected to Interface {0}'.format(port))
                exclude_list.append(port)
                continue


            if '/' not in temp_port_name:
                self._logger.error('Interface was not found')
                raise Exception('Interface was not found')
            port_name = self._get_resource_full_name(port.split('/')[-1], port_resource_map)
            # port_name = temp_port_name.split('/')[-1].replace('-', '/')
            self._logger.info('Interface {0} will be added to channel group {1}'.format(port_name, port_channel_id))

            # Cant add port to port-channel if it has a vlan already
            vlan_id = self._send_command('show running-config interface ' + port.split('/')[-1].replace('-', '/') + ' | include vlan')
            vlan_id = re.search('switchport.*vlan.*\d+', self._send_command('show running-config interface ' + port.split('/')[-1].replace('-', '/') + ' | include vlan'))
            if vlan_id:
                self._logger.info('Interface {0} has vlan, so cannot add to port-channel'.format(port.split('/')[-1].replace('-', '/')))
                # raise Exception('Interface {0} has VLAN, cannot be added to port-channel'.format(port.split('/')[-1].replace('-', '/')))
                exclude_list.append(port)
                continue

            # run no shutdown and then add to the port-channel
            commands_list = list()
            commands_list.append('interface ' + port.split('/')[-1].replace('-', '/'))
            commands_list.append('no shutdown')
            commands_list.append('switchport ')
            if port_resource_map.ResourceModelName == 'Cisco NXOS Switch':
                commands_list.append('channel-group {0} mode active'.format(port_channel_id))
            else:
                commands_list.append('channel-group {0} mode auto'.format(port_channel_id))
            self.send_commands_list(commands_list)
            self._exit_configuration_mode()
            self._logger.info('Interface {0} was added to channel-group {1}'.format(port_name, port_channel_id))


        # Create port-channels on Resource Manager
        res_name = port_chann_str + port_channel_id
        new_port_list = list(set(port_list.split(';')) - set(exclude_list))

        # Add if does not exists
        port_channel_exists = self.cloud_shell_api.FindResources('Port Channel', 'Generic Port Channel',
                                            resourceFullName=port_resource_map.Name + '/' + res_name).Resources
        if len(port_channel_exists) == 1 and port_channel_exists[0].Name == None:
            # Create port channel on Resource Manager
            try:
                self.cloud_shell_api.CreateResource(
                    resourceFamily='Port Channel',
                    resourceModel='Generic Port Channel',
                    resourceName=res_name,
                    resourceAddress='PC'+port_channel_id,
                    folderFullPath=port_resource_map.FolderFullPath,
                    resourceDescription='Created for VLAN',
                    parentResourceFullPath=port_resource_map.FolderFullPath + '/' + port_resource_map.Name,
                )
            except:
                self._logger.error('Could not create Port channel {} on resource manager'.format(res_name))
                raise Exception('Could not create Port channel {} on resource manager'.format(res_name))

        # Get current Associated-ports attribute
        port_name_list = filter(None, self.cloud_shell_api.GetAttributeValue(port_resource_map.Name + '/' + res_name,
                                                                             'Associated Ports').Value.split(';'))

        port_name_list += new_port_list
        # Why is Associated ports read only ?
        self.cloud_shell_api.SetAttributeValue(
                resourceFullPath = '/'.join([port_resource_map.FolderFullPath, port_resource_map.Name, res_name]),
                attributeName = 'Associated Ports',
                attributeValue = ','.join(port_name_list)
                )

        return 'Port-Channel {} Configuration Completed'.format(port_channel_id)

    def delete_portchannel(self, port_list):
        """
        Remove a port-channel
        :param port_channel_id:
        :return:
        """
        self._logger.info('Port-Channel Removal Started')

        # get root resource info
        port_resource_map = self.cloud_shell_api.GetResourceDetails(self.attributes_dict['ResourceName'])

        # default values work for IOS
        port_chann_str = 'Port-channel'

        # Values specific to NxOS
        if port_resource_map.ResourceModelName == 'Cisco NXOS Switch':
            port_chann_str = 'port-channel'

        for port in port_list.split(';'):
            port_name = port.split('/')[-1].replace('-','/')
            port_channel = [re.search('channel.*\s(\d+)', line.strip()) for line in self._send_command('show running-config interface ' + port_name + ' | include channel').splitlines() if line.strip().startswith('channel')]
            # port_channel = re.search('channel(\d+)', self._send_command('show running-config interface ' + port_list + ' | include channel'))
            if port_channel:
                port_channel_id = port_channel[0].group(1)
                break

        if not port_channel_id:
            self._logger.info('could not find port channel on {}'.format(str(port_list)))
            return ('could not find port channel on {}'.format(str(port_list)))


        # Remove port channel on switch
        vlan_id = [line for line in self._send_command('show running-config interface port-channel ' + port_channel_id + ' | include vlan').splitlines() if re.search('switchport.*vlan.*\d+', line)]
        if vlan_id:
            self.send_commands_list(['interface port-channel ' + port_channel_id, 'no ' + vlan_id[0]])
        self.send_commands_list(['interface port-channel ' + port_channel_id, 'no switchport', 'shutdown'])
        self.send_commands_list(['no interface port-channel ' + port_channel_id])
        self._logger.info('{0} was removed'.format(port_channel_id))

        # Remove port channel on Resource Manager
        res_name = self.cloud_shell_api.GetResourceDetails(
            self.attributes_dict['ResourceName']).Name + '/' + port_chann_str + port_channel_id
        self.cloud_shell_api.DeleteResource(res_name)
        return 'Port-Channel {0} Configuration Removed'.format(port_channel_id)

    def save_port_config(self, port_list):
        """
        Saves configuration of a interface in a file on execution server
        :param port_list:
        :return:
        """
        if len(port_list) < 1:
            raise Exception('Port list is empty')

        for port in port_list.split('|'):
            port_resource_map = self.cloud_shell_api.GetResourceDetails(self.attributes_dict['ResourceName'])
            temp_port_name = self._get_resource_full_name(port, port_resource_map)
            if '/' not in temp_port_name:
                self._logger.error('Interface was not found')
                raise Exception('Interface was not found')
            port_name = temp_port_name.split('/')[-1].replace('-', '/')
            if 'channel' in port_name.lower():
                port_name = port_name.replace('/', '-')

            speed = ''
            mtu = ''
            port_config = self.send_command('show running-config interface ' + port_name)
            mtu_r = re.search('mtu (\d+)', port_config)
            if mtu_r:
                mtu = mtu_r.group(1)

            speed_r  = re.search('speed (\d+)', port_config)
            if speed_r:
                speed = speed_r.group(1)

            description = ';'.join(['speed={}'.format(speed),'mtu={}'.format(mtu)])
            commands_list = list()
            commands_list.append('interface ' + port_name)
            commands_list.append('no shutdown')
            commands_list.append('description ' + description)
            self.send_commands_list(commands_list)
            self._exit_configuration_mode()


        return "Save ports configuration complete"

    def restore_port_config(self, port_list):
        """Restore configuration of each specified port from provided configuration file
        Restore configuration from local file system or ftp/tftp server into 'running-config' or 'startup-config'.
        :param source_file: relative path to the file on the remote host tftp://server/sourcefile
        :param clear_config: override current config or not
        :return:
        """
        if len(port_list) < 1:
            raise Exception('Port list is empty')

        for port in port_list.split('|'):
            port_resource_map = self.cloud_shell_api.GetResourceDetails(self.attributes_dict['ResourceName'])
            temp_port_name = self._get_resource_full_name(port, port_resource_map)
            if '/' not in temp_port_name:
                self._logger.error('Interface was not found')
                raise Exception('Interface was not found')
            port_name = temp_port_name.split('/')[-1].replace('-', '/')
            if 'channel' in port_name.lower():
                port_name = port_name.replace('/', '-')

            # Look for MTU and speed in description and put those values back to the interface
            port_config = self.send_command('show running-config interface ' + port_name)
            port_descr = re.search('description\s(.*)', port_config)

            command_list = list()

            command_list.append('interface ' + port_name)
            try:
                speed = re.search('speed=(.*?);', port_descr.group(0)).group(1)
            except:
                command_list.append('no speed')
            else:
                command_list.append('speed ' + speed)

            try:
                mtu = re.search('mtu=(.*?)', port_descr.group(0)).group(1)
            except:
                 command_list.append('no mtu')
            else:
                command_list.append('mtu ' + mtu)

            command_list.append('no shutdown')
            self.send_commands_list(command_list)
            self._exit_configuration_mode()


        self._exit_configuration_mode()
        return 'Restore port configuration complete'
