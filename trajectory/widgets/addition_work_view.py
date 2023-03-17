#!/usr/bin/env python
# -*- coding: utf-8 -*-


from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import *
from trajectory.local_utils.qt_util import fill_grid_layout


class AdditionWorkView(QtWidgets.QWidget):
    """
    按钮控制区
    """
    def __init__(self, parent=None):
        super(AdditionWorkView, self).__init__()
        self._parent = parent
        self.__init_ui()

    def __init_ui(self):
        if self._parent:
            self.setParent(self._parent)

        # 核心按钮-------------------
        self.lbl_name0=QLabel('选中颜色: ')
        self.lbl_name1=QLabel('单独改变地图颜色:  ')
        self.lbl_name2 = QLabel('取消单独改变地图颜色:  ')

        self.btn_color_change_ok = QPushButton('ok')
        self.btn_color_change_esc = QPushButton('esc')

        self.combobox=QComboBox(self)
        self.model=QtGui.QStandardItemModel()
        self.combobox.setModel(self.model)
        self.strlist=['普通道路','路口','环岛','匝道','水平泊车',
                 '垂直泊车','隧道','路口中转','路口后段','预留']
        self.colorlist=[[10,240,10],[255,255,10],[65,105,200],[10,255,230],[127,250,200],
                   [160,32,230],[244,164,98],[255,0,10],[255,97,3],[112,128,100]]
        for i in range(len(self.colorlist)):
            self.combobox.addItem(self.strlist[i])
            c=self.colorlist[i]
            self.model.item(i).setBackground(QColor(c[0],c[1],c[2]))

        # 布局------------------
        gridLayout=QGridLayout(self)
        gridLayout.setContentsMargins(1,1,1,1)
        gridLayout.setHorizontalSpacing(2)
        gridLayout.setVerticalSpacing(2)
        gridLayout.setObjectName("gridLayout")
        grid_wids=[
            [(self.lbl_name1,1,1),(self.combobox,1,1),(self.btn_color_change_ok,1,1)],
            [(self.lbl_name2,1,1),None,(self.btn_color_change_esc,1,1)],
        ]
        fill_grid_layout(gridLayout,grid_wids)


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    _view = AdditionWorkView()
    _view.show()
    sys.exit(app.exec_())













