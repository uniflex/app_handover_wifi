import logging
from sbi.wifi.events import WiFiHandoverRequestEvent, WiFiHandoverReplyEvent
from uniflex.core import modules
from uniflex.core import events


__author__ = "Anatolij Zubow"
__copyright__ = "Copyright (c) 2015, Technische Universitat Berlin"
__version__ = "0.1.0"
__email__ = "{zubow}@tkn.tu-berlin.de"


'''
    Handover app for IEEE 802.11 infrastructure networks.
    Two modes are supported: i) soft handover (see BIGAP paper) and ii) hard handover.
'''

class WiFiHandoverModule(modules.ControlApplication):
    def __init__(self):
        super(WiFiHandoverModule, self).__init__()
        self.log = logging.getLogger('wifi_handover_module.main')
        self.nodes = {} # list of detected network nodes: uuid->node-obj


    @modules.on_start()
    def start_ho_module(self):
        self.log.debug("Start HO module".format())


    @modules.on_exit()
    def stop_ho_module(self):
        self.log.debug("Stop HO module".format())


    @modules.on_event(events.NewNodeEvent)
    def add_node(self, event):
        node = event.node

        self.log.info("Added new node: {}, Local: {}"
                      .format(node.uuid, node.local))
        self.nodes[node.uuid] = node


    @modules.on_event(events.NodeExitEvent)
    @modules.on_event(events.NodeLostEvent)
    def remove_node(self, event):
        self.log.info("Node lost".format())
        node = event.node
        reason = event.reason
        if node.uuid in self.nodes:
            del self.nodes[node.uuid]
            self.log.info("Node: {}, Local: {} removed reason: {}"
                          .format(node.uuid, node.local, reason))


    @modules.on_event(WiFiHandoverRequestEvent)
    def perform_handover(self, event):
        """
        Performing an infrastructure-initiated handover of a client STA.

        :param event: the event contains all required information to perform handover operation.
        """
        try:
            is_soft_ho = False
            if event.ho_scheme == 'Soft_CSA':
                is_soft_ho = True

            # from UUID to node object
            servingAP = self.nodes[event.serving_AP]
            targetAP = self.nodes[event.target_AP]
            gateway = self.nodes[event.gateway]
            sta_mac_addr = event.client_sta_id

            # from kwargs
            wlan_inject_iface = event.kwargs['wlan_inject_iface']
            sta_ip_addr = event.kwargs['sta_ip']
            servingAP_ip_addr = event.kwargs['servingAP_ip']
            servingAP_channel = event.kwargs['servingChannel']
            servingAP_bssid = event.kwargs['network_bssid']
            targetAP_ip_addr = event.kwargs['targetAP_ip']
            targetAP_channel = event.kwargs['targetChannel']
            wifi_intf = event.kwargs['wlan_iface']

            self.log.debug("Handover of station: {} from {} to {}".format(sta_mac_addr, servingAP_ip_addr, targetAP_ip_addr))

            if is_soft_ho:
                # register STA in target AP
                res = targetAP.iface(wifi_intf).blocking(True).net.register_new_device(wifi_intf, sta_mac_addr)
                self.log.debug('registerNewSTAInAP::result: %s', str(res))
            else:
                pass

            # Set ARP entry for STA on target AP
            res = targetAP.blocking(True).net.set_ARP_entry(wifi_intf, sta_mac_addr, sta_ip_addr)
            self.log.info('setARPEntry::result: %s', str(res))

            # change routing in backhaul by adapting routing on gateway
            res = gateway.blocking(True).net.change_routing(servingAP_ip_addr, targetAP_ip_addr, sta_ip_addr)
            self.log.info('changeRouting::result: %s', str(res))

            if is_soft_ho:
                # send CSA packet to client STA
                self.log.warn('Send CSA by serving AP %s to STA %s to switch channel to %s.' % (
                    servingAP, sta_mac_addr, str(targetAP_channel)))

                # exec on servingAP node
                res = servingAP.iface(wifi_intf).blocking(True).net.trigger_channel_switch_in_device(
                    wlan_inject_iface, sta_mac_addr, targetAP_channel, servingAP_channel, bssid=servingAP_bssid)
                self.log.info('sendCSABeaconToSTA::result: %s', str(res))

            else:
                # unblacklist STA on target AP
                self.log.debug('UN-Blacklist STA %s on target  AP %s.' % (sta_mac_addr, targetAP))

                # exec on targetAP
                res = targetAP.iface(wifi_intf).blocking(True).net.remove_device_from_blacklist(wifi_intf, sta_mac_addr)
                self.log.info('removeSTAFromAPBlacklist::result: %s', str(res))

                # blacklist STA on serving AP
                self.log.info('Blacklist STA %s on serving  AP %s ' % (sta_mac_addr, servingAP))

                # exec on targetAP
                res = servingAP.iface(wifi_intf).blocking(True).net.add_device_to_blacklist(wifi_intf, sta_mac_addr)
                self.log.info('addSTAtoAPBlacklist::result: %s', str(res))

                # disassociate with current AP
                self.log.info('Send Disassociation Frame by serving AP %s to STA %s.' % (servingAP, sta_mac_addr))

                # exec on serving
                res = servingAP.iface(wifi_intf).blocking(True).net.disconnect_device(sta_mac_addr)
                self.log.info('transmitDisassociationRequestToSTA::result: %s', str(res))

            # send reply event
            self.send_event(WiFiHandoverReplyEvent(True))

        except Exception as e:
            self.log.fatal("handover failed: err_msg: %s" % (str(e)))
            self.send_event(WiFiHandoverReplyEvent(False))
