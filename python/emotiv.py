import sys

import serial


class Emotiv():
    def __init__(self, port='', baud=9600):
        self.__port = port
        self.__baud = baud
        try:
            self.__ser = serial.Serial(self.__port, self.__baud)
        except Exception as exc:
            sys.stderr.write(exc)
            sys.exit(1)
        self.send_command(28)

    def send_command(self, ascii_number):
        """
        シリアル通信で 1byte のコマンドを送信する
        :param ascii_number: int型の文字
        :return: None
        """
        try:
            self.__ser.write(ascii_number.to_bytes(1, 'big'))
        except Exception as exc:
            sys.stderr.write(exc)
            sys.exit(1)

    def close_serial(self):
        """
        シリアルポートを閉じる
        :return: None
        """
        self.__ser.close()
