# -*- coding: utf-8 -*-

from datetime import datetime

import bitalino
import emotiv
import numpy as np
import os
import rotaryencoder
from PyQt4.QtCore import *
from PyQt4.QtGui import *


class App(QMainWindow):
    __fig_number = 0
    __is_updated_image = False

    def __init__(self, window_title='test'):
        super(App, self).__init__()
        self.setWindowTitle(window_title)

        # ウィジェットの上にいろいろ配置する感じで
        self.__widget = QWidget()
        # 画像配置用
        self.__view = QGraphicsView()
        # 垂直方向にウィジェットを配置
        self.__boxlay = QVBoxLayout()

        # 現在のパスを取得
        # Windows の場合，バックスラッシュになってるのでスラッシュに変換
        self.__file_path = os.getcwd().replace(os.path.sep, '/')

        # Scene 初期化
        self.__scene = QGraphicsScene()
        self.__item = None  # __item に画像データを格納する

        self.set_images(is_point=True)
        self.__setVBoxLay()
        self.__widget.setLayout(self.__boxlay)
        self.setCentralWidget(self.__widget)

        self.bitalino_measurement = BitalinoMeasurement(macAddress='COM30', Fs=1000, acq=[0, 1, 2, 3])

    def init_worker(self, com_emotiv='COM4', com_rotary='COM6'):
        """
        ワーカーの初期化
        ロータリーエンコーダは別スレッドで動かす
        :return: None
        """
        self.__emo = emotiv.Emotiv(port=com_emotiv)
        self.__rotary = rotaryencoder.RotaryEncoder(port=com_rotary)
        self.__rotary.started.connect(self.start_worker)
        self.__rotary.signal.connect(self.event_rotary)
        self.start_worker()
        self.bitalino_measurement.start()
        self.countdown(sec=10)

    def start_worker(self):
        """
        ワーカーの開始
        :return: None
        """
        self.__rotary.start()

    def close_worker(self):
        """
        ワーカーの一時停止
        :return: None
        """
        self.__rotary.wait()

    def event_rotary(self, rot):
        """
        signal.connect したときの処理
        :param rot: ロータリーエンコーダの回転方向 'R' または 'L'
        :return:
        """
        self.update_fignumber_by_rotary(rot)
        self.set_images()
        self.__emo.send_command(App.__fig_number)

    def countdown(self, sec=10):
        """
        画像呈示前の注視点配置から画像に切替えるまでのカウントダウンを設定する
        :param sec: 秒数 [s]
        :return: None
        """
        self.timer = QTimer()
        self.timer.setInterval(sec * 1000)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.stop_initimage)
        self.timer.start()

    def stop_initimage(self):
        """
        countdown() で呼ばれる，set_images() によって写真呈示に変えるメソッド
        :return: None
        """
        self.set_images(is_point=False)
        self.__emo.send_command(29)

    def set_images(self, width=1590, height=1060, is_point=False):
        """
        画像を表示させる
        :return: None
        """
        # すでに画像がセットされてたらリセット (メモリ確保)
        if self.__get_item():
            self.__remove_item()
        img_filepath = self.__fetch_img_filepath()
        if is_point == True:
            item = QGraphicsPixmapItem(QPixmap('point.png').scaled(100, 100,
                                                                    Qt.KeepAspectRatio,
                                                                    Qt.SmoothTransformation))
        else:
            item = QGraphicsPixmapItem(QPixmap(img_filepath).scaled(width, height,
                                                                    Qt.KeepAspectRatio,
                                                                    Qt.SmoothTransformation))
        self.__scene.addItem(item)
        self.__set_item(item)

    def __fetch_img_filenames(self, dir_picture='picture'):
        """
        画像ディレクトリのファイル名をリストで取得
        :param dir_picture: 画像が格納されたディレクトリ名
        :return: ファイル名の list (フルパスは含まれない)
        """
        return os.listdir(self.__file_path + '/' + dir_picture)

    def __fetch_img_filepath(self, dir_picture='picture'):
        """
        画像のファイルパスを返す
        :param dir_picture: 画像が格納されたディレクトリ名
        :return: ファイルのフルパス
        """
        return self.__file_path + '/' + dir_picture + '/' \
               + self.__fetch_img_filenames()[App.__fig_number]

    def __set_item(self, item):
        self.__item = item

    def __get_item(self):
        return self.__item

    def __remove_item(self):
        self.__scene.removeItem(self.__get_item())

    def __transition_range(self):
        """
        画像遷移の範囲を決定する (画像枚数 - 1 を計算)
        :return: 遷移する範囲 (int)
        """
        return len(self.__fetch_img_filenames()) - 1

    def update_fignumber_by_rotary(self, rot):
        """
        ロータリーエンコーダの回転に応じて画像番号の更新を行なう
        :param rot: 'R'または'L'
        :return: None
        """
        if rot == 'R' and App.__fig_number < self.__transition_range():
            App.__fig_number += 1
        elif rot == 'L' and App.__fig_number > 0:
            App.__fig_number -= 1

    def __setVBoxLay(self):
        """
        垂直方向に用意したウィジェットを配置する
        :return: None
        """
        self.__view.setScene(self.__scene)
        self.__view.setStyleSheet("background:transparent; border:none;")
        self.__view.setWindowFlags(Qt.FramelessWindowHint)
        self.__boxlay.addWidget(self.__view)

    def keyPressEvent(self, event):
        """
        キー入力が行われたときのイベント処理
        :param event: Qt のイベント
        :return: None
        """
        if event.key() == Qt.Key_Return:
            self.bitalino_measurement.stop()
            self.close()

    def closeEvent(self, event):
        """
        画面を閉じて終了する際の処理
        :param event: Qt のイベント
        :return: None
        """
        self.__emo.send_command(30)
        self.__emo.close_serial()
        # self.bitalino_measurement.stop()
        QApplication.quit()


class BitalinoMeasurement(QThread):
    """
    Qt のスレッドを立てて BITalino を走らせる
    """

    def __init__(self, parent=None, macAddress='00:00:00:00:00:00', Fs=100, acq=[0, 1]):
        super(BitalinoMeasurement, self).__init__(parent)
        self.__Fs = None
        self.__analog_ch = None
        self.__mac_address = macAddress
        self.set_bitalino_sampling_rate(Fs)
        self.set_acq_analog_channels(acq)
        self.device = bitalino.BITalino(self.__mac_address)

    def set_bitalino_sampling_rate(self, fs):
        self.__Fs = fs

    def get_bitalino_sampling_rate(self):
        return self.__Fs

    def set_acq_analog_channels(self, lst):
        self.__analog_ch = lst

    def get_acq_analog_channels(self):
        return self.__analog_ch

    def run(self):
        """
        ここに start() を呼び出したときに実行する内容を記述する
        :return: None
        """
        self.device.start(self.get_bitalino_sampling_rate(), self.get_acq_analog_channels())
        save_file_path = os.path.dirname(__file__) + '/../log/' + datetime.now().strftime('%Y%m%d-%H-%M-%S') + '.csv'
        # バイナリでないと記録できない
        self.f = open(save_file_path, 'ab')
        while (True):
            # read() は "シーケンス番号, D0, D1, D2, D3, 指定したアナログ入力" の順に
            # 出力される
            data = self.device.read(10)
            np.savetxt(self.f, data, delimiter=',', fmt='%.0f')

    def stop(self):
        """
        スレッドの終了処理
        :return: None
        """
        self.device.stop()
        self.device.close()
        self.f.close()
        self.finished.emit()
