# -*- coding: utf-8 -*-

import sys

import serial
from PyQt4.QtCore import *


class RotaryEncoder(QThread):
    signal = pyqtSignal(str)  # メインスレッドとやりとりする際に使用する

    def __init__(self, parent=None, port='', baud=9600):
        super(RotaryEncoder, self).__init__(parent)
        self.__port = port
        self.__baud = baud
        try:
            self.__ser = serial.Serial(self.__port, self.__baud)
        except Exception as exc:
            sys.stderr.write(exc)
            sys.exit(1)

    def run(self):
        """
        ワーカーの開始時に実行する内容を記述
        :return:  None
        """
        # while True でひたすら受信しつづける
        while True:
            self.recv_command(self.__ser)

    def recv_command(self, ser):
        """
        シリアルで 1byte 受信する
        :param ser: Serial
        :return: None
        """
        byte = ser.read()
        self.__evalbyte(byte)

    def __evalbyte(self, byte):
        """
        バイト文字の判定
        :param byte: 受信した byte 文字
        :return: None
        """
        if byte == b'R':
            self.signal.emit('R')
        elif byte == b'L':
            self.signal.emit('L')
        else:
            sys.stderr.write('evalbyte: 不正な値です')
            exit(1)

    def close_serial(self):
        """
        シリアルポートを閉じる
        :return: None
        """
        self.__ser.close()
