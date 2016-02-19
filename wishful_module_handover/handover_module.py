import logging
import wishful_controller
import wishful_upis as upis

__author__ = "Piotr Gawlowicz, Anatolij Zubow"
__copyright__ = "Copyright (c) 2015, Technische Universitat Berlin"
__version__ = "0.1.0"
__email__ = "{gawlowicz, zubow}@tkn.tu-berlin.de"


@wishful_controller.build_module
class HandoverModule(wishful_controller.ControllerUpiModule):
    def __init__(self, controller):
        super(HandoverModule, self).__init__(controller)
        self.log = logging.getLogger('wifi_handover_module.main')


    @wishful_controller.bind_function(upis.global_upi.perform_hard_handover)
    def perform_hard_handover(self, srcAp, dstAp, station):
        self.log.debug("Hard handover of station: {} from {} to {}".format(station, srcAp, dstAp))
        #call set of function here, like
        #self.controller.nodes(srcAp).radio.blacklist(station)
        #self.controller.nodes(dstAp).radio.whitelist(station)
        #...
        #...
        retVal = "OK"
        return retVal


    @wishful_controller.bind_function(upis.global_upi.perform_soft_handover)
    def perform_soft_handover(self, srcAp, dstAp, station):
        self.log.debug("Soft handover of station: {} from {} to {}".format(station, srcAp, dstAp))
        #call set of function here, like
        #self.controller.nodes(srcAp).radio.blacklist(station)
        #self.controller.nodes(dstAp).radio.whitelist(station)
        #...
        #...
        retVal = "OK"
        return retVal


    """
    Estimates the AP which serves the given STA. Note: if an STA is associated with multiple APs the one with the
    smallest inactivity time is returned.
    """
    @wishful_controller.bind_function(upis.global_upi.get_servingAP)
    def get_servingAP(self, nodes, wifi_intf, sta_mac_addr):

        self.log.debug('Function: get_servingAP')

        try:
            nodes_with_sta = {}

            for node in nodes:
                res = self.controller.nodes(node).iface(wifi_intf).blocking(True).radio.get_inactivity_time_of_associated_STAs()

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
