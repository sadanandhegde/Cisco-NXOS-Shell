# __author__ = 'CoYe'

# from cloudshell.shell.core.driver_builder_wrapper import DriverFunction
# from cloudshell.networking.resource_driver.networking_generic_resource_driver import networking_generic_resource_driver
#
# class cisco_generic_nxos_resource_driver(networking_generic_resource_driver):
#     @DriverFunction(extraMatrixRows={"resource": ["User", "Password", "Enable Password", "Console Server IP Address",
#                                                   "Console User", "Console Password", "Console Port", "Connection Type",
#                                                   "SNMP Version", "SNMP Read Community", "SNMP V3 User", "SNMP V3 Password",
#                                                   "SNMP V3 Private Key"]})
#     def Init(self, matrixJSON):
#         self.handler_name = 'nxos'
#         networking_generic_resource_driver.Init(self, matrixJSON)
#         print self.handler_name
#
# if __name__ == '__main__':
#
#     data_json = str("""{
#             "resource" : {
#                     "ResourceAddress": "192.168.42.235",
#                     "User": "root",
#                     "Password": "Password1",
#                     "Console User": "",
#                     "Console Password": "",
#                     "Console Server IP Address": "",
#                     "CLI Connection Type": "",
#                     "Enable Password": "cisco",
#                     "Console Port": "",
#                     "Connection Type": "auto",
#                     "SNMP Community": "stargate",
#                     "SNMP Version": "2",
#                     "SNMP Password": "Password1",
#                     "SNMP User": "QUALI",
#                     "SNMP Private Key": "Live4lol",
#                     "SNMP V3 User": "",
#                     "SNMP V3 Password": "",
#                     "SNMP V3 Private Key": "",
#                     "SNMP Read Community": "stargate"
#                 }
#             }""")
#     resource_driver = cisco_generic_nxos_resource_driver('77', data_json)
#     # resource_driver.Add_VLAN(data_json, '192.168.42.235/0/24', '34', 'trunk', '')
#     resource_driver.GetInventory(data_json)

__author__ = "shms"

from cisco_nxos_driver_bootstrap import CiscoNXOSBootstrap
from cloudshell.shell.core.context.context_utils import context_from_args
import cisco_nxos_driver_config as config
import inject
from cloudshell.shell.core.cli_service.cli_service import CliService


class CiscoNXOSDriver:
    def __init__(self):
        bootstrap = CiscoNXOSBootstrap()
        bootstrap.add_config(config)
        bootstrap.initialize()
        # self.config = inject.instance('config')

    @context_from_args
    def initialize(self, context):
        """
        :type context: cloudshell.shell.core.driver_context.InitCommandContext
        """
        return 'Finished initializing'

    # Destroy the driver session, this function is called everytime a driver instance is destroyed
    # This is a good place to close any open sessions, finish writing to log files
    def cleanup(self):
        pass

    @context_from_args
    @inject.params(logger='logger', context='context')
    def simple_command(self, context, command, logger=None):
        # ss = 'dsd'
        # for i in range(0, int(command)):
        #     logger.info('Resource: ' + context.resource.name)
        #     time.sleep(1)
        # return logger.log_path
        cli = CliService()
        out = cli.send_command('ls')
        logger.info('Command completed')
        return out