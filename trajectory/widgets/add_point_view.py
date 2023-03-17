#!/usr/bin/env python
# -*- coding: utf-8 -*-


from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import *
from trajectory.UI.add_point_ui import Ui_Form
from trajectory.local_utils.qt_util import *

class AddPointView(QtWidgets.QWidget, Ui_Form):
    """
    按钮控制区
    """
    def __init__(self, parent=None):
        super(AddPointView, self).__init__()
        self._parent = parent
        self.setupUi(self)
        self.__init_ui()

    def __init_ui(self):
        if self._parent:
            self.setParent(self._parent)

        # 核心部件--------------
        # 自动插值控件设计----
        self.btn_auto_add_enable = QPushButton('插值')
        self.lbl_space = QLabel('点间距')
        self.spbx_space = QDoubleSpinBox()
        self.btn_preview = QPushButton('预览')
        self.btn_cancel_auto = QPushButton('取消')
        self.btn_finish_auto = QPushButton("完成")
        self.lbl_auto_add_point_num = QLabel('增加点个数')
        self.lbl_distance = QLabel('')

        # 布局--------------

        self.auto_wid = QWidget()
        lay = QHBoxLayout(self.tabWidgetPage2)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        lay.addWidget(self.auto_wid)

        gridLayout = QGridLayout(self.auto_wid)
        gridLayout.setContentsMargins(1, 1, 1, 1)
        gridLayout.setHorizontalSpacing(6)
        gridLayout.setVerticalSpacing(6)
        gridLayout.setObjectName("gridLayout")
        #
        # 控件网格布局设置  控件，占用行列
        grid_wids = [
            [(self.btn_auto_add_enable, 1, 1), (self.lbl_auto_add_point_num, 1, 1), (self.lbl_distance, 1, 1)],
            [(self.lbl_space, 1, 1), (self.spbx_space, 1, 1), (self.btn_preview, 1, 1)],
            [None,                    (self.btn_cancel_auto, 1, 1), (self.btn_finish_auto, 1, 1)],
        ]
        fill_grid_layout(gridLayout, grid_wids)


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    _view = AddPointView()
    _view.show()
    # _view.auto_wid.show()
    sys.exit(app.exec_())













