UniFlex Handover App for WIFI
===============================

This app implements an infrastructure-initiated handover scheme for 
IEEE 802.11 infrastructure networks. It supports hard and a novel soft 
handover scheme. It was developed as part of BigAP.

The paper and slides describing BigAP can be found here:
[full paper](https://www2.informatik.hu-berlin.de/~zubow/bigap_noms2016_zubow.pdf "Full paper")
[slides](https://www2.informatik.hu-berlin.de/~zubow/BIGAP_talk_noms.pdf "Talk slides")

## Installation
To install UniFlex framework with all available modules, please go through all steps in [manifest](https://github.com/uniflex/manifests) repository.

You have to use our patched version of hostapd and iw. Please install 
them from src/ or use the binaries from bin/

## Usage

In order to trigger an infrastructure-initiated handover a control 
program has to send a <code>upis.wifi.WiFiTriggerHandoverRequestEvent</code>
event. This module will reply with an <code>upis.net_func.TriggerHandoverReplyEvent</code>
event.

## Example

See examples/handover2/

## How to reference to?

Just use the following bibtex:

    @INPROCEEDINGS{7502842, 
    author={A. Zubow and S. Zehl and A. Wolisz}, 
    booktitle={NOMS 2016 - 2016 IEEE/IFIP Network Operations and Management Symposium}, 
    title={BIGAP #x2014; Seamless handover in high performance enterprise IEEE 802.11 networks}, 
    year={2016}, 
    pages={445-453}, 
    keywords={business communication;cloud computing;mobility management (mobile radio);quality of experience;quality of service;radio spectrum management;resource allocation;BIGAP;MAC-layer handover;QoE;QoS;cloud storage;dynamic frequency selection capability;handover operation;high network performance;high performance enterprise IEEE 802.11 networks;load balancing;mobile HD video;mobility support;network outage duration;radio spectrum;seamless handover;seamless mobility;wireless clients;Handover;IEEE 802.11 Standard;Load management;Radio frequency;Switches;Wireless communication;Handover;Mobility;SDN;Wireless}, 
    doi={10.1109/NOMS.2016.7502842}, 
    month={April},}
