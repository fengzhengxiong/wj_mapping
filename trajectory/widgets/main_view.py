#!/usr/bin/env python
# -*- coding: utf-8 -*-


from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QSize

from trajectory.widgets.seg_edit_view import SegEditView
from trajectory.widgets.add_point_view import AddPointView
from trajectory.widgets.btn_area_view import BtnAreaView
from trajectory.widgets.measure_dis_view import MeasureDisView
from trajectory.widgets.multi_select_choose_view import MultiSelectChooseView
from trajectory.widgets.para_edit_area_view import ParaEditAreaView
from trajectory.widgets.vtk_show_view import VtkShowView
from trajectory.widgets.file_list_view import FileListView
from trajectory.control.table_data_controller import TableDataController
from trajectory.widgets.smooth_process_view import SmoothProcessView
from trajectory.widgets.addition_work_view import AdditionWorkView
from functools import partial
from trajectory.local_utils.qt_util import *
from trajectory.local_utils.pub import struct
from trajectory.local_utils.qt_util import *


class MainView(QtWidgets.QMainWindow):
    """
    按钮控制区
    """
    def __init__(self):
        super(MainView, self).__init__()

        self.__init_child_wids()
        self.__init_ui()

    def __init_child_wids(self):
        """
        子模块
        :return:
        """
        # TODO 子模块设置parent为self  ， 有时候会解决 按钮显示过大的问题

        self.wid_vtkshow = VtkShowView(self)  # VTK窗口
        self.wid_addpoint = AddPointView(self)  # 添加点功能窗口
        self.wid_segedit = SegEditView()  # 段编辑窗口
        self.wid_btnarea = BtnAreaView()  # 按钮区域，清除、撤回等
        self.wid_multiselectchoose = MultiSelectChooseView()  # 多选选择按钮
        self.wid_paraedit = ParaEditAreaView()  # 参数编辑窗口
        self.wid_measuredis = MeasureDisView()  # 测量距离窗口
        self.wid_filelist = FileListView(self)  # 文件菜单列表控件
        self.wid_tabdata = TableDataController(self) #表格操作
        self.wid_smooth=SmoothProcessView()  #平滑处理窗口
        self.wid_additionwork=AdditionWorkView()    # 额外工作区，估计是暂时的

    def __init_ui(self):
        self.resize(1200, 700)
        self.centralwidget = QWidget(self)
        self.setCentralWidget(self.centralwidget)

        # 初始化控件，由大到小装载进入

        """
        centralwidget: 
        spl_main
            ├─frm_file
            │  ├─wid_filelist
            ├─spl_vbox
            │  ├─spl_hbox
            │  │  ├─frm_show
            │  │  │  ├─wid_vtkshow
            │  │  ├─frm_edit
            │  ├─frm_data
        """
        self.spl_main = QSplitter(Qt.Horizontal, self.centralwidget)
        fill_widget(self.centralwidget, 1, [self.spl_main], (8,8,8,8))

        self.frm_file = QFrame(self.spl_main)
        self.spl_vbox = QSplitter(Qt.Vertical, self.spl_main)

        self.spl_hbox = QSplitter(self.spl_vbox)
        self.frm_data = QFrame(self.spl_vbox)  # 点云显示 窗

        self.frm_show = QFrame(self.spl_hbox)  # 点云显示 窗
        self.frm_edit = QFrame(self.spl_hbox)  # 编辑区

        fill_widget(self.frm_show, 1, [self.wid_vtkshow], margin=(0, 0, 0, 0))  # 填充控件
        fill_widget(self.frm_file, 1, [self.wid_filelist])

        """
        ├─frm_edit
        │  ├─wid_btnarea
        │  ├─wid_multiselectchoose
        │  ├─wid_segedit
        │  ├─tab_edit_widget
        
        """
        self.tab_edit_widget = QTabWidget(self.frm_edit)

        childs = [
            self.wid_btnarea,
            self.wid_multiselectchoose,
            self.wid_segedit,
            self.tab_edit_widget,
        ]
        fill_widget(self.frm_edit, 2, childs, margin=(5, 5, 5, 5))

        self.wid_paraedit.setParent(self.tab_edit_widget)
        self.wid_measuredis.setParent(self.tab_edit_widget)  # 为了显示字体大小合理，设置父控件
        self.tab_edit_widget.addTab(self.wid_paraedit, "编辑")
        self.tab_edit_widget.addTab(self.wid_addpoint, "新增点")
        self.tab_edit_widget.addTab(self.wid_measuredis, "测量")
        self.tab_edit_widget.addTab(self.wid_smooth, "平滑处理")
        self.tab_edit_widget.addTab(self.wid_additionwork, "额外工作区")

        self.frm_file.setFrameShape(QFrame.Box)
        self.frm_file.setFrameShadow(QFrame.Plain)
        self.frm_data.setFrameShape(QFrame.Box)
        self.frm_data.setFrameShadow(QFrame.Plain)
        self.frm_data.setMinimumHeight(100)
		
        # ======================动态生成表格
        fill_widget(self.frm_data, 1, [self.wid_tabdata], (0, 0, 0, 0))
        # ======================动态生成表格


        self.frm_show.setMinimumSize(QtCore.QSize(200, 200))
        self.frm_show.setFrameShape(QFrame.Box)
        self.frm_show.setFrameShadow(QFrame.Raised)
        self.frm_edit.setFrameShape(QFrame.Box)
        self.frm_edit.setFrameShadow(QFrame.Raised)

        set_splitter_attr(self.spl_main, Qt.Horizontal)
        set_splitter_attr(self.spl_vbox, Qt.Vertical)
        self.tab_edit_widget.setTabPosition(QTabWidget.South)

        self.spl_main.setStretchFactor(0, 30)
        self.spl_main.setStretchFactor(1, 80)

        self.spl_hbox.setStretchFactor(0, 100)
        self.spl_hbox.setStretchFactor(1, 20)

        self.spl_vbox.setStretchFactor(0, 50)
        self.spl_vbox.setStretchFactor(1, 10)

        self.lbl_statusbar = QLabel('')
        self.statusBar().addPermanentWidget(self.lbl_statusbar)

    def release(self):
        self.wid_vtkshow.release()

    def closeEvent(self, event):
        self.release()
        super(MainView, self).closeEvent(event)


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    _view = MainView()
    _view.show()
    sys.exit(app.exec_())


