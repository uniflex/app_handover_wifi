import logging
import wishful_framework as wishful_module
import wishful_upis as upis
from wishful_framework.classes import exceptions

__author__ = "Piotr Gawlowicz, Anatolij Zubow"
__copyright__ = "Copyright (c) 2015, Technische Universitat Berlin"
__version__ = "0.1.0"
__email__ = "{gawlowicz, zubow}@tkn.tu-berlin.de"

class HandoverTypes:
    Hard_BL, Soft_CSA = range(2)

'''
    This is IEEE 802.11 specific -> todo: rename it into handover_wifi
'''
@wishful_module.build_module
class HandoverModule(wishful_module.ControllerModule):
    def __init__(self, controller):
        super(HandoverModule, self).__init__(controller)
        self.log = logging.getLogger('wifi_handover_module.main')

    @wishful_module.bind_function(upis.net_func.perform_handover)
    def perform_handover(self, wifi_intf, servingAP, targetAP, sta_mac_addr, **kwargs):

        """
        Performing an infrastructure-initiated handover of a client STA using either:
        - ho_type = 0: hard HO scheme,
        - ho_type = 1: soft HO scheme
        """

        wlan_inject_iface = kwargs.get('wlan_inject_iface')
        sta_ip_addr = kwargs.get('sta_ip_addr')
        servingAP_ip_addr = kwargs.get('servingAP_ip_addr')
        servingAP_channel = kwargs.get('servingAP_channel')
        servingAP_bssid = kwargs.get('servingAP_bssid')
        targetAP_ip_addr = kwargs.get('targetAP_ip_addr')
        targetAP_channel = kwargs.get('targetAP_channel')
        gateway = kwargs.get('gateway')
        ho_type = kwargs.get('ho_type')

        self.log.debug("Handover of station: {} from {} to {}".format(sta_mac_addr, servingAP_ip_addr, targetAP_ip_addr))

        #if not (isinstance(servingAP, Node) or isinstance(targetAP, Node)):
        #    raise exceptions.InvalidArgumentException(func_name='nf.perform_STA_handover')

        if ho_type == HandoverTypes.Soft_CSA:
            # register STA in target AP
            UPIargs = {'iface' : wifi_intf, 'sta_mac_addr' : sta_mac_addr}

            # exec on each node
            res = self.controller.nodes(targetAP).iface(wifi_intf).blocking(True).net.register_new_device(UPIargs)
            self.log.debug('registerNewSTAInAP::result: %s', str(res))
        else:
            pass

        # Set ARP entry for STA on target AP
        UPIargs = {'iface' : wifi_intf, 'mac_addr' : sta_mac_addr, 'ip_addr' : sta_ip_addr}

        res = self.controller.nodes(targetAP).blocking(True).net.set_ARP_entry(UPIargs)
        self.log.info('setARPEntry::result: %s', str(res))

        # change routing in backhaul by adapting routing on gateway
        UPIargs = {'servingAP_ip_addr' : servingAP_ip_addr, 'targetAP_ip_addr' : targetAP_ip_addr, 'sta_ip_addr' : sta_ip_addr}

        # exec on gateway node
        res = self.controller.nodes(gateway).blocking(True).net.change_routing(UPIargs)
        self.log.info('changeRouting::result: %s', str(res))

        if ho_type == HandoverTypes.Soft_CSA:

            # send CSA packet to client STA
            self.log.warn('Send CSA by serving AP %s to STA %s to switch channel to %s.' % (
                servingAP, sta_mac_addr, str(targetAP_channel)))

            # exec on servingAP node
            res = self.controller.nodes(servingAP).iface(wifi_intf).blocking(True).net.trigger_channel_switch_in_device(
                wlan_inject_iface, sta_mac_addr, targetAP_channel, servingAP_channel, bssid=servingAP_bssid)
            self.log.info('sendCSABeaconToSTA::result: %s', str(res))

        else:
            # unblacklist STA on target AP
            self.log.debug('UN-Blacklist STA %s on target  AP %s.' % (sta_mac_addr, targetAP))

            # exec on targetAP
            res = self.controller.nodes(targetAP).iface(wifi_intf).blocking(True).net.remove_device_from_blacklist(wifi_intf, sta_mac_addr)
            self.log.info('removeSTAFromAPBlacklist::result: %s', str(res))

            # blacklist STA on serving AP
            self.log.info('Blacklist STA %s on serving  AP %s ' % (sta_mac_addr, servingAP))

            # exec on targetAP
            res = self.controller.nodes(servingAP).iface(wifi_intf).blocking(True).net.add_device_to_blacklist(wifi_intf, sta_mac_addr)
            self.log.info('addSTAtoAPBlacklist::result: %s', str(res))

            # disassociate with current AP
            self.log.info('Send Disassociation Frame by serving AP %s to STA %s.' % (servingAP, sta_mac_addr))

            # exec on serving
            res = self.controller.nodes(servingAP).iface(wifi_intf).blocking(True).net.disconnect_device(sta_mac_addr)
            self.log.info('transmitDisassociationRequestToSTA::result: %s', str(res))

        return True


    @wishful_module.bind_function(upis.net_func.get_servingAP)
    def is_associated_with(self, nodes, wifi_intf, sta_mac_addr):
        """
        Estimates the AP which serves the given STA. Note: if an STA is associated with multiple APs the one with the
        smallest inactivity time is returned.
        """

        self.log.debug('Function: is_associated_with')

        try:
            nodes_with_sta = {}

            for node in nodes:
                res = self.controller.nodes(node).iface(wifi_intf).blocking(True).radio.get_inactivity_time_of_connected_devices()

                if sta_mac_addr in res:
                    self.log.debug(res[sta_mac_addr])
                    nodes_with_sta[node] = int(res[sta_mac_addr][0])

                    # dictionary of aps where station is associated
                    self.log.debug("STA found on the following APs with the following idle times:")
                    self.log.debug(str(nodes_with_sta))

            if not bool(nodes_with_sta):
                # If no serving AP was found; return None
                return None

            # serving AP is the one with minimal STA idle value
            servingAP = min(nodes_with_sta, key=nodes_with_sta.get)
            self.log.info("STA %s is served by AP %s " % (sta_mac_addr, servingAP))

            return servingAP

        except Exception as e:
            self.log.fatal("An error occurred in get_servingAP: %s" % e)
            raise e
