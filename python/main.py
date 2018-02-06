# -*- coding: utf-8 -*-

import sys

import qtapp
from PyQt4.QtGui import *


def main():
    app = QApplication(sys.argv)
    main_app = qtapp.App()
    main_app.init_worker()
    main_app.showFullScreen()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
