#!/usr/bin/env python
# -*- coding: utf-8 -*-


from trajectory.control.main_controller import MainController
from trajectory.config import __appname__, __version__
from PyQt5.QtWidgets import QApplication
import sys

from trajectory.local_utils.qt_util import newIcon


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("{}-{}".format(__appname__, __version__))
    app.setWindowIcon(newIcon('wanji64'))
    c = MainController()
    c.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
