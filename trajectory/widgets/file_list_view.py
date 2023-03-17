#!/usr/bin/env python
# -*- coding: utf-8 -*-


from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import *

from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon

from trajectory.widgets.custom_list_widget import CustomListWidget
from trajectory.local_utils.qt_util import *
from trajectory.UI.filelist_ui import Ui_Form


class FileListView(QtWidgets.QWidget, Ui_Form):
    """
    按钮控制区
    """
    def __init__(self, parent=None):
        super(FileListView, self).__init__()
        self._parent = parent
        self.setupUi(self)
        self.__init_ui()

    def __init_ui(self):
        if self._parent:
            self.setParent(self._parent)

        # 核心组件-------------------

        self.clw_up = CustomListWidget(self.frm_file)
        self.clw_down = CustomListWidget(self.frm_file_sub)
        self.clw_json = CustomListWidget(self.frm_json_file)
        self.clw_down.lw_content.setSelectionMode(QAbstractItemView.MultiSelection)
        # self.clw_up = CustomListWidget()
        # self.clw_down = CustomListWidget()
        self.clw_up.set_title("文件列表")
        self.clw_down.set_title("加载列表")
        self.clw_json.set_title("json列表")

        fill_widget(self.frm_file, 1, [self.clw_up], (0, 0, 0, 0))
        fill_widget(self.frm_file_sub, 1, [self.clw_down], (0, 0, 0, 0))
        fill_widget(self.frm_json_file,1,[self.clw_json],(0,0,0,0))

        self.btn_add_file = QPushButton(self.frm_btn_area)
        self.btn_add_file.setText("添加↓")
        self.btn_remove_file = QPushButton(self.frm_btn_area)
        self.btn_remove_file.setText("删除↑")
        self.btn_load_file = QPushButton(self.frm_btn_area)
        self.btn_load_file.setText("加载>>")
        self.btn_show = QPushButton(self.frm_btn_area)
        self.btn_show.setText("显示")
        self.btn_hide = QPushButton(self.frm_btn_area)
        self.btn_hide.setText("隐藏")
        self.btn_inverse_show = QPushButton(self.frm_btn_area)
        self.btn_inverse_show.setText("反显")

        gridLayout = QGridLayout(self.frm_btn_area)
        gridLayout.setContentsMargins(1, 1, 1, 1)
        gridLayout.setHorizontalSpacing(2)
        gridLayout.setVerticalSpacing(2)
        gridLayout.setObjectName("gridLayout")
        #
        # 控件网格布局设置  控件，占用行列
        grid_wids = [
            [(self.btn_add_file, 1, 1), (self.btn_remove_file, 1, 1), (self.btn_load_file, 1, 1)],
            [(self.btn_show, 1, 1), (self.btn_hide, 1, 1), (self.btn_inverse_show, 1, 1)],
        ]
        fill_grid_layout(gridLayout, grid_wids)

    def reset(self):
        self.clw_up.reset()
        self.clw_down.reset()


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    _view = FileListView()
    _view.show()
    sys.exit(app.exec_())

