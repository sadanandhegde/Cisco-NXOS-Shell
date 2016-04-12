from pkgutil import extend_path

from cloudshell.networking.cisco.resource_drivers_map import CISCO_RESOURCE_DRIVERS_MAP
from cloudshell.networking.platform_detector.hardware_platform_detector import HardwarePlatformDetector
from cloudshell.shell.core.handler_factory import HandlerFactory

from cloudshell.networking.cisco.nxos.extended.cisco_nxos_handler_extended import CiscoNXOSHandlerExtended

__path__ = extend_path(__path__, __name__)

HandlerFactory.handler_classes['NXOS_EXT'] = CiscoNXOSHandlerExtended
HandlerFactory.handler_classes['NXOS_5K'] = CiscoNXOSHandlerExtended
HardwarePlatformDetector.RESOURCE_DRIVERS_MAP = CISCO_RESOURCE_DRIVERS_MAP
