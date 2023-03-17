#!/usr/bin/env python
# -*- coding: utf-8 -*-


from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSignal, Qt


class MultiSelectChooseView(QtWidgets.QWidget):
    """
    多选选项，选择切换按钮
    """
    btn_toggle_signal = pyqtSignal()

    def __init__(self, parent=None):
        super(MultiSelectChooseView, self).__init__()
        self._parent = parent
        self.__init_ui()
        self.__init_slot()

    def __init_ui(self):
        if self._parent:
            self.setParent(self._parent)

        # 核心按钮 -----------
        self.btn_select = QRadioButton()
        self.btn_select.setText('选中')
        self.btn_add_select = QRadioButton()
        self.btn_add_select.setText('加选')
        self.btn_sub_select = QRadioButton()
        self.btn_sub_select.setText('减选')
        self.btn_inverse_select = QRadioButton()
        self.btn_inverse_select.setText('反选')

        # 布局 ------------------
        self.gbx_area = QtWidgets.QGroupBox(self)
        self.gbx_area.setTitle("")
        self.gbx_area.setFlat(False)
        self.gbx_area.setObjectName("gbx_area")

        hbox = QHBoxLayout(self.gbx_area)
        hbox.setContentsMargins(1, 1, 1, 1)
        hbox.setSpacing(3)
        for btn in self.btn_list:
            hbox.addWidget(btn)
        self.gbx_area.setLayout(hbox)

        self.hlay = QHBoxLayout(self)
        self.hlay.setContentsMargins(1, 1, 1, 1)
        self.hlay.setSpacing(0)
        self.hlay.addWidget(self.gbx_area)

    @property
    def btn_list(self):
        return [
            self.btn_select,
            self.btn_add_select,
            self.btn_sub_select,
            self.btn_inverse_select,
        ]

    def __init_slot(self):
        self.btn_select.toggled.connect(lambda: self.btn_toggle_signal.emit())
        self.btn_add_select.toggled.connect(lambda: self.btn_toggle_signal.emit())
        self.btn_sub_select.toggled.connect(lambda: self.btn_toggle_signal.emit())
        self.btn_inverse_select.toggled.connect(lambda: self.btn_toggle_signal.emit())


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    _view = MultiSelectChooseView()
    _view.show()
    sys.exit(app.exec_())













