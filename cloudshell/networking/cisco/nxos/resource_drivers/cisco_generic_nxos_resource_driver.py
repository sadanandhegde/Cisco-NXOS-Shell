__author__ = 'CoYe'

import cloudshell.networking.cisco.nxos.resource_drivers
from cloudshell.shell.core.driver_builder_wrapper import DriverFunction
from cloudshell.networking.resource_driver.networking_generic_resource_driver import networking_generic_resource_driver

class cisco_generic_nxos_resource_driver(networking_generic_resource_driver):
    @DriverFunction(extraMatrixRows={"resource": ["User", "Password", "Enable Password", "Console Server IP Address",
                                                  "Console User", "Console Password", "Console Port", "Connection Type",
                                                  "SNMP Version", "SNMP Read Community", "SNMP V3 User", "SNMP V3 Password",
                                                  "SNMP V3 Private Key"]})
    def Init(self, matrixJSON):
        self.handler_name = 'nxos'
        networking_generic_resource_driver.Init(self, matrixJSON)
        print self.handler_name

if __name__ == '__main__':

    data_json = str("""{
            "resource" : {
                    "ResourceAddress": "192.168.42.235",
                    "User": "admin",
                    "Password": "cisco",
                    "Console User": "",
                    "Console Password": "",
                    "Console Server IP Address": "",
                    "Enable Password": "cisco",
                    "Console Port": "",
                    "Connection Type": "ssh",
                    "SNMP Community": "Cisco",
                    "SNMP Version": "3",
                    "SNMP Password": "Password1",
                    "SNMP User": "QUALI",
                    "SNMP Private Key": "Live4lol"
                }
            }""")
    resource_driver = cisco_generic_nxos_resource_driver('77', data_json)
    resource_driver.Add_VLAN(data_json, '192.168.42.235/0/24', '34', 'trunk', '')