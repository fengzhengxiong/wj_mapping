#!/usr/bin/env python
# -*- coding: utf-8 -*-


from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import *
# from PyQt5.QtCore import pyqtSignal, Qt


class BtnAreaView(QtWidgets.QWidget):
    """
    按钮控制区
    """
    def __init__(self, parent=None):
        super(BtnAreaView, self).__init__()
        self._parent = parent
        self.__init_ui()

    def __init_ui(self):
        if self._parent:
            self.setParent(self._parent)

        # 核心按钮-------------------
        self.btn_clear_select = QPushButton('clear')
        self.btn_area_pick = QPushButton('area_pick')
        self.btn_del = QPushButton('del')
        self.btn_undo = QPushButton('undo')
        self.btn_redo = QPushButton('redo')

        # 布局------------------
        self.gbx_area = QtWidgets.QGroupBox(self)
        self.gbx_area.setTitle("")
        self.gbx_area.setFlat(False)
        self.gbx_area.setObjectName("gbx_area")

        hbox = QHBoxLayout(self.gbx_area)
        hbox.setContentsMargins(1, 1, 1, 1)
        hbox.setSpacing(3)

        for btn in self.btn_list:
            btn.setParent(self)
            hbox.addWidget(btn)
        self.gbx_area.setLayout(hbox)

        self.hlay = QHBoxLayout(self)
        self.hlay.setContentsMargins(1, 1, 1, 1)
        self.hlay.setSpacing(0)
        self.hlay.addWidget(self.gbx_area)

    @property
    def btn_list(self):
        return [
            self.btn_clear_select,
            self.btn_area_pick,
            self.btn_del,
            self.btn_undo,
            self.btn_redo,
        ]


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    _view = BtnAreaView()
    _view.show()
    sys.exit(app.exec_())













