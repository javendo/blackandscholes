#! /usr/bin/python2

import sys, os
import socket
import time
import threading
import matplotlib
import numpy as np
from matplotlib.lines import Line2D
import matplotlib.pyplot as plt
import matplotlib.animation as animation

def main(argv):
    thread_feeder = feeder(int(argv[1]))
    thread_feeder.start()
    oscope = scope(thread_feeder)
    ani = animation.FuncAnimation(oscope.fig, oscope.update, interval=250, blit=False)
    plt.show()

class scope:
    def __init__(self, feeder):
        self.fig = plt.figure()
        self.ax = plt.axes(xlim=(0, 100), ylim=(0.5, 200))
        self.xdata = np.linspace(0, 100, 100)
        self.ydata = np.zeros(100)
        self.line, = self.ax.plot(self.xdata, self.ydata, lw=2)
        self.feeder = feeder
        self.ymin = 0
        self.ymax = 0
        self.ax.set_ylim(self.ymin, self.ymax + 100)

    def update(self, y):
        data_new = np.array(self.feeder.emitter()).astype(int)
        data_len = len(data_new)
        self.ydata = np.append(self.ydata[data_len:], data_new)
        self.ymin = min(self.ydata)
        self.ymax = max(self.ydata) + 100
        self.ax.set_ylim(self.ymin, self.ymax)
        self.ax.figure.canvas.draw()
        self.line.set_xdata(self.xdata)
        self.line.set_ydata(self.ydata)
        return self.line,

class feeder(threading.Thread):
    def __init__(self, port_socket):
        self.value = []
        self.port_socket = port_socket
        self.connect()
        self.is_alive = True
        threading.Thread.__init__(self)

    def connect(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('', self.port_socket))
        sock.listen(1)
        self.conn, self.addr = sock.accept()

    def emitter(self):
        return self.value

    def run(self):
        while self.is_alive:
            data = self.conn.recv(1024).split('#')
            self.value = [] if len(data) == 0 else data[:-1]
            time.sleep(1)
        self.conn.close()

try:
    main(sys.argv)
    while True:
        time.sleep(2)
except KeyboardInterrupt:
    thread_throughput.is_alive = False
    thread_sniff_network.is_alive = False
    sys.exit()
