from scapy.all import *
import CTA_ETA

def arp_display(pkt):
    if pkt[ARP].op == 1: #who-has (request)
        # print pkt[ARP].psrc
        # if pkt[ARP].psrc == '192.168.1.149': # ARP Probe
        if pkt[ARP].hwsrc == '50:f5:da:cc:4d:3e':
            print "ARP Probe from: " + pkt[ARP].hwsrc
            CTA_ETA.main()

print sniff(prn=arp_display, iface='wlan0', filter="arp", store=0, count=0)
