__author__ = 'CoYe'

import re

from cloudshell.networking.cisco.cisco_handler_base import CiscoHandlerBase
from qualipy.common.libs.connection_manager import expected_actions

class CiscoNXOSHandler(CiscoHandlerBase):
    def __init__(self, connection_manager, logger=None):
        CiscoHandlerBase.__init__(self, connection_manager, logger)
        self.supported_os = ['NXOS', 'NX-OS']

    def _default_actions(self):
        """Send default commands to configure/clear session outputs
        :return:
        """
        self._session.set_unsafe_mode(True)

        output = self._send_command('')

        if re.search('> *$', output):
            output = self._send_command('enable',
                                        expected_map={'[Pp]assword': expected_actions.send_default_password})

        if re.search('> *$', output):
            raise Exception('Cisco OS', "Can't set enable mode!")

        self._set_terminal_length(0)

        self._enter_configuration_mode()
        self._send_command('no logging console')
        self._exit_configuration_mode()