#!/usr/bin/env python
# -*- coding: utf-8 -*-


from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import *
# from PyQt5.QtCore import pyqtSignal, Qt

from trajectory.widgets.edit_widget_ import EditWidget_


class ParaEditAreaView(QtWidgets.QWidget):
    """
    编辑区
    """

    def __init__(self, parent=None):
        super(ParaEditAreaView, self).__init__()
        self._parent = parent
        self.__init_ui()

    def __init_ui(self):
        if self._parent:
            self.setParent(self._parent)
        # 核心按钮 -----------
        # self._wid_attr = EditWidget_('属性', 'QComboBox')
        # self._wid_speed = EditWidget_('速度', 'QDoubleSpinBox')
        # self._wid_lane = EditWidget_('车道状态', 'QComboBox')
        # self._wid_merge = EditWidget_('并道属性', 'QComboBox')
        # self._wid_road = EditWidget_('道路状态', 'QComboBox')
        # self._wid_road = EditWidget_('道路状态', 'QComboBox')
        # self._wid_road = EditWidget_('道路状态', 'QComboBox')
        # self._wid_road = EditWidget_('道路状态', 'QComboBox')
        # self._wid_road = EditWidget_('道路状态', 'QComboBox')

        # 布局 ------------------
        self.wid_ = QWidget()

        self.scrollArea = QScrollArea(self)
        self.scrollArea.setWidgetResizable(True)  # 设置为true，则滚动区域部件将自动调整，以避免可以不显示的滚动条，或者利用额外的空间；
        self.scrollArea.setStyleSheet("QScrollArea{border:none; background:white;}")
        self.scrollArea.setWidget(self.wid_)

        lay = QHBoxLayout(self)
        lay.addWidget(self.scrollArea)
        lay.setContentsMargins(0, 0, 0, 0)

        self.vbox = QVBoxLayout(self.wid_)
        self.vbox.setContentsMargins(2, 2, 2, 2)
        self.vbox.setSpacing(3)

        # for wid in self.wid_list:
        #     self.vbox.addWidget(wid)

    # @property
    # def wid_list(self):
    #     return [
    #         self._wid_attr,
    #         self._wid_speed,
    #         self._wid_lane,
    #         self._wid_merge,
    #         self._wid_road,
    #     ]


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    _view = ParaEditAreaView()
    _view.show()
    sys.exit(app.exec_())
