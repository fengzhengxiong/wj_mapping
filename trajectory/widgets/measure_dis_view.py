#!/usr/bin/env python
# -*- coding: utf-8 -*-


from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import *
from trajectory.UI.measure_ui import Ui_Form


class MeasureDisView(QtWidgets.QWidget, Ui_Form):
    """
    按钮控制区
    """
    def __init__(self, parent=None):
        super(MeasureDisView, self).__init__()
        self._parent = parent
        self.setupUi(self)
        self.__init_ui()

    def __init_ui(self):
        if self._parent:
            self.setParent(self._parent)

        # 核心部件--------------
        pass


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    _view = MeasureDisView()
    _view.show()
    sys.exit(app.exec_())













