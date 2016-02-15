import logging
import wishful_upis as upis


__author__ = "Piotr Gawlowicz, Anatolij Zubow"
__copyright__ = "Copyright (c) 2015, Technische Universitat Berlin"
__version__ = "0.1.0"
__email__ = "{gawlowicz, zubow}@tkn.tu-berlin.de"


@wishful_module.build_module
class WiFiHandover(wishful_module.WishfulModule):
    def __init__(self, agentPort=None):
        super(WiFiHandover, self).__init__(agentPort)
        self.log = logging.getLogger('wifi_handover_module.main')


    @wishful_module.bind_function(upis.global_upi.perform_hard_handover)
    def perform_hard_handover(self, srcAp, dstAp, station):
        self.log.debug("Hard handover of station: {} from {} to {}".format(station, srcAp, dstAp))
        #call set of function here, like
        #self.controller.nodes(srcAp).radio.blacklist(station)
        #self.controller.nodes(dstAp).radio.whitelist(station)
        #...
        #...
        retVal = "OK"
        return retVal


    @wishful_module.bind_function(upis.global_upi.perform_soft_handover)
    def perform_soft_handover(self, srcAp, dstAp, station):
        self.log.debug("Soft handover of station: {} from {} to {}".format(station, srcAp, dstAp))
        #call set of function here, like
        #self.controller.nodes(srcAp).radio.blacklist(station)
        #self.controller.nodes(dstAp).radio.whitelist(station)
        #...
        #...
        retVal = "OK"
        return retVal