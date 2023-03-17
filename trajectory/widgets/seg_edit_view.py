#!/usr/bin/env python
# -*- coding: utf-8 -*-


from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import *


class SegEditView(QtWidgets.QWidget):
    """
    按钮控制区
    """
    def __init__(self, parent=None):
        super(SegEditView, self).__init__()
        self._parent = parent
        self.__init_ui()

    def __init_ui(self):
        if self._parent:
            self.setParent(self._parent)

        # 核心部件--------------
        self.btn_head = QPushButton('首段')
        self.btn_tail = QPushButton('尾段')
        self.btn_neighbor = QPushButton('邻段')
        self.btn_cancel = QPushButton('取消')

        # sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        # sizePolicy.setHorizontalStretch(0)
        # sizePolicy.setVerticalStretch(0)
        # sizePolicy.setHeightForWidth(self.btn_cancel.sizePolicy().hasHeightForWidth())
        self.btn_cancel.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        self.lbl_pin1 = QLabel()
        self.lbl_pin1.setText('pin1')
        self.lbl_pin2 = QLabel()
        self.lbl_pin2.setText('pin2')

        self.lbl_seg_type = QLabel()
        self.lbl_seg_type.setText('段类型')
        self.lbl_seg_type_val = QLabel()
        self.lbl_seg_type_val.setText('')

        self.sbx_pin1 = QSpinBox()
        self.sbx_pin2 = QSpinBox()

        # 布局--------------

        self.gbx_area = QtWidgets.QGroupBox(self)
        self.gbx_area.setTitle("")
        self.gbx_area.setFlat(False)
        self.gbx_area.setObjectName("gbx_area")

        gridLayout = QGridLayout(self.gbx_area)
        gridLayout.setHorizontalSpacing(6)
        gridLayout.setVerticalSpacing(6)
        gridLayout.setObjectName("gridLayout")

        # 控件网格布局设置  控件，占用行列
        grid_wids = [
            [(self.btn_cancel, 3, 1), (self.btn_head, 1, 1), (self.lbl_pin1, 1, 1), (self.sbx_pin1, 1, 1)],
            [None,                    (self.btn_tail, 1, 1), (self.lbl_pin2, 1, 1), (self.sbx_pin2, 1, 1)],
            [None,                    (self.btn_neighbor, 1, 1), (self.lbl_seg_type, 1, 1), (self.lbl_seg_type_val, 1, 1)],
        ]

        self.fill_grid_layout(gridLayout, grid_wids)

        self.gbx_area.setLayout(gridLayout)

        self.hlay = QVBoxLayout(self)
        self.hlay.setContentsMargins(1, 1, 1, 1)
        self.hlay.setSpacing(0)
        self.hlay.addWidget(self.gbx_area)
        self.hlay.addWidget(QLabel('Ctrl+L/R button'))

    def fill_grid_layout(self, lay, wids):
        """
        填充网格布局
        :param lay: QGridLayout
        :param wids: 二维列表，元素为元组=(控件，占行，占列)
        :return:
        """
        for i in range(len(wids)):
            for j in range(len(wids[i])):
                # 第i行 j 列
                w = wids[i][j]
                if w is None:
                    continue
                wid, a, b = w
                lay.addWidget(wid, i, j, a, b)

    def show_seg_info(self, p1, p2, seg_mode):
        self.sbx_pin1.setValue(p1)
        self.sbx_pin2.setValue(p2)
        self.lbl_seg_type_val.setText(str(seg_mode))

    def reset(self):
        self.show_seg_info(0, 0, '')



if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    _view = SegEditView()
    _view.show()
    sys.exit(app.exec_())













