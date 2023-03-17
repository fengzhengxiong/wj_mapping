#!/usr/bin/env python
# -*- coding: utf-8 -*-


from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import *
from trajectory.UI.smooth_process import Ui_Form
from trajectory.local_utils.qt_util import *

class SmoothProcessView(QtWidgets.QWidget, Ui_Form):
    def __init__(self, parent=None):
        super(SmoothProcessView, self).__init__()
        self._parent = parent
        self.setupUi(self)
        self.__init_ui()

    def __init_ui(self):
        pass
        if self._parent:
            self.setParent(self._parent)

        #核心部件，没有在ui界面中设计,只是直接手敲出界面设计


        ################路径平滑####################
        self.lbl_smooth_path = QLabel("Path:")
        self.lbl_smooth_path_ = QLabel("None")
        self.lbl_start_id = QLabel("起始id :")
        self.lbl_start_id_ = QLabel("None")
        self.lbl_end_id = QLabel("结束id: ")
        self.lbl_end_id_ = QLabel("None")
        self.lbl_point_dis = QLabel("相邻两点间距和总点数 :")
        self.spbx_space = QDoubleSpinBox()
        self.lbl_add_point_num = QLabel("None")
        self.btn_start_smooth = QPushButton("预览")
        self.btn_end_smooth = QPushButton("完成")



        self.wid_p_smooth = QWidget()
        lay = QHBoxLayout(self.tab)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        lay.addWidget(self.wid_p_smooth)
        gridLayout = QGridLayout(self.wid_p_smooth)
        gridLayout.setContentsMargins(1, 1, 1, 1)
        gridLayout.setHorizontalSpacing(6)
        gridLayout.setVerticalSpacing(6)
        gridLayout.setObjectName("gridLayout")

        grid_wids = [
            [(self.lbl_smooth_path, 1, 1), (self.lbl_smooth_path_, 1, 1), None],
            [(self.lbl_start_id, 1, 1), (self.lbl_start_id_, 1, 1), (self.btn_start_smooth, 1, 1)],
            [(self.lbl_end_id, 1, 1), (self.lbl_end_id_, 1, 1), (self.btn_end_smooth, 1, 1), ],
            [(self.lbl_point_dis, 1, 1), (self.spbx_space, 1, 1), (self.lbl_add_point_num, 1, 1), ],
        ]
        fill_grid_layout(gridLayout, grid_wids)

        ################速度平滑####################
        self.lbl_smooth_path_v = QLabel("Path:")
        self.lbl_smooth_path_v_ = QLabel("None")
        self.lbl_start_id_v=QLabel("起始id :")
        self.lbl_start_id_v_=QLabel("None")
        self.lbl_end_id_v=QLabel("结束id: ")
        self.lbl_end_id_v_=QLabel("None")
        self.btn_start_smooth_v=QPushButton("完成")

        self.wid_v_smooth = QWidget()
        lay1 = QHBoxLayout(self.tab_2)
        lay1.setContentsMargins(0, 0, 0, 0)
        lay1.setSpacing(0)
        lay1.addWidget(self.wid_v_smooth)
        gridLayout1 = QGridLayout(self.wid_v_smooth)
        gridLayout1.setContentsMargins(1, 1, 1, 1)
        gridLayout1.setHorizontalSpacing(6)
        gridLayout1.setVerticalSpacing(6)
        gridLayout1.setObjectName("gridLayout")

        grid_wids1 = [
            [(self.lbl_smooth_path_v,1,1),(self.lbl_smooth_path_v_,1,1),None],
            [(self.lbl_start_id_v, 1, 1), (self.lbl_start_id_v_,1,1), None],
            [(self.lbl_end_id_v, 1, 1), (self.lbl_end_id_v_,1,1), None],
            [(self.btn_start_smooth_v, 1, 1), None,None],
        ]
        fill_grid_layout(gridLayout1, grid_wids1)

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    _view = SmoothProcessView()
    _view.show()
    sys.exit(app.exec_())