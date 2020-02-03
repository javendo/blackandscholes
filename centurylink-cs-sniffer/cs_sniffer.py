#! /usr/bin/python2

import sys, os
from scapy.all import *
import threading
import time
import socket

filter = None
lfilter = None
thread_throughput = None
thread_sniff_network = None

def main(argv):
    ip_src = argv[1]
    ip_dst = argv[2]
    port_dst = argv[3]
    ip_socket = argv[4]
    port_socket = argv[5]
    filter = "src %s and dst %s and dst port %s" % (ip_src, ip_dst, port_dst)
    lfilter = lambda x: x['IP'].src == ip_src
    thread_throughput = throughput(ip_socket, port_socket)
    thread_sniff_network = sniff_network(filter, lfilter, thread_throughput)
    thread_throughput.start()
    thread_sniff_network.start()

class throughput(threading.Thread):
    lock = threading.Lock()
    
    def __init__(self, ip_socket, port_socket):
        self.socket_connected = False
        self.bytes_per_second = 0
        self.is_alive = True
        self.ip_socket = ip_socket
        self.port_socket = int(port_socket)
        self.connect();
        threading.Thread.__init__(self)

    def connect(self):
        try:
            print("Trying to connect using %s:%s." % (self.ip_socket, self.port_socket))
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.ip_socket, self.port_socket))
            self.socket_connect = True
        except:
            print("Error. Could not established socket connection")
            self.socket_connect = False

    def update_bytes_per_second(self, value):
        throughput.lock.acquire()
        self.bytes_per_second += value
        throughput.lock.release()
        
    def clean_bytes_per_second(self):
        throughput.lock.acquire()
        self.bytes_per_second = 0
        throughput.lock.release()

    def send_data(self):
        try:
            if self.socket_connect:
                self.sock.sendall(str(self.bytes_per_second) + '#')
            else:
                self.connect()
        except:
            self.socket_connect = False
            print("Error. Problem to send value.")

    def run(self):
        while self.is_alive:
            self.send_data()
            print("%s ====> %s" % (time.strftime("%a, %d %b %Y %H:%M:%S"), self.bytes_per_second))
            self.clean_bytes_per_second()
            time.sleep(1)

class sniff_network(threading.Thread):
    def __init__(self, filter, lfilter, throughput_thread):
        threading.Thread.__init__(self)
        self.is_alive = True
        self.filter = filter
        self.lfilter = lfilter
        self.throughput_thread = throughput_thread

    def info(self, pkt):
        #info_map = {}
        #info_map['ip_src'] = pkt['IP'].src
        #info_map['ip_dst'] = pkt['IP'].dst
        #info_map['port_src'] = pkt['TCP'].sport
        #info_map['port_dst'] = pkt['TCP'].dport
        #info_map['data'] = "" if not pkt.haslayer('Raw') else pkt['Raw'].load
        #info_map['len'] = int(pkt['IP'].len)
        #str_ret = "%s:%s -> %s:%s [%s]" % (info_map['ip_src'], info_map['port_src'], info_map['ip_dst'], info_map['port_dst'], info_map['len'])
        #return str_ret
        self.throughput_thread.update_bytes_per_second(int(pkt['IP'].len))

    def run(self):
        sniff(filter=self.filter, lfilter=self.lfilter, prn=self.info)


try:
    main(sys.argv)
    while True:
        try:
            time.sleep(2)
        except KeyboardInterrupt, e:
            thread_throughput.is_alive = False
            thread_sniff_network.is_alive = False
            sys.exit()
except:
    print("Error. Invalid number of arguments.")

