# -*- coding: utf-8 -*-

import time
import datetime

import numpy as np
import bitalino

def main(mac_addr, measuring_time):
    device = bitalino.BITalino(mac_addr)
    device.start(SamplingRate=1000, analogChannels=[0, 1, 2, 3])
    start = time.time()
    end = time.time()
    filename = datetime.datetime.now().strftime('%Y%m%d-%H-%M-%S-cal.csv')
    with open(filename, 'ab') as file:
        while end - start < measuring_time:
            np.savetxt(file, device.read(10), delimiter=',', fmt='%d')
            end = time.time()

if __name__ == '__main__':
    mac_addr = 'COM40'  # Toshiba のドングルは COM40 になる
    measuring_time = 150  # [sec]
    main(mac_addr, measuring_time)
