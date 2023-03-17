#!/usr/bin/env python
# -*- coding: utf-8 -*-


import time
import numpy as np
import sys
import os
import os.path as osp

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from PyQt5.QtGui import QColor, QBrush, QFont

from trajectory.widgets.file_list_view import FileListView
from trajectory.manager.common_mode import *
from trajectory.manager.action_manager import action_manager
from trajectory.config.common_variable import NORMAL_COLOR, ENABLE_COLOR, NORMAL_FONT, ENABLE_FONT, NORMAL_BG_COLOR, HOVER_BG_COLOR

last_hover_file = None  # 记录上一次悬浮文件


class FileListController(QObject):
    fileUpToDown = pyqtSignal()
    downDoubleClicked = pyqtSignal(str)
    removeFile = pyqtSignal()
    toggleCheck = pyqtSignal()
    showFile = pyqtSignal(int)  # -1 0 1

    def __init__(self, view=None, model=None, *args, **kwargs):
        super(FileListController, self).__init__()
        self._view = view
        self.__init_connect()

    def __init_connect(self):
        if not isinstance(self._view, FileListView):
            return

        self._view.btn_add_file.clicked.connect(self.add_file_up_to_down)  # 添加↓
        self._view.clw_down.lw_content.itemDoubleClicked.connect(self.down_double_clicked)  # 下列表 双击
        self._view.btn_remove_file.clicked.connect(lambda: self.removeFile.emit())  # 删除
        self._view.clw_down.checkStateChange.connect(lambda: self.toggleCheck.emit())  # 勾选状态切换 隐藏/显示
        self._view.btn_show.clicked.connect(lambda: self.showFile.emit(1))  # 显示
        self._view.btn_hide.clicked.connect(lambda: self.showFile.emit(0))  # 隐藏
        self._view.btn_inverse_show.clicked.connect(lambda: self.showFile.emit(-1))  # 反显示

    def set_view(self, view):
        if isinstance(view, FileListView):
            self._view = view

    def get_view(self):
        return self._view

    def set_model(self, model):
        pass

    def run(self):
        self._app = QApplication(sys.argv)
        self._view.show()
        return self._app.exec_()

    def show(self):
        self._view.show()

    def load_file_list(self, filelist, dirpath):
        if not isinstance(self._view, FileListView):
            return
        for file in filelist:
            self._view.clw_up.add_item(osp.relpath(file, dirpath), data=file)

    def load_json_file(self, filelist, dirpath):
        if not isinstance(self._view, FileListView):
            return
        for file in filelist:
            self._view.clw_json.add_item(osp.relpath(file, dirpath), data=file)

    def count(self, up=True):
        return self._view.clw_up.count if up else self._view.clw_down.count

    def add_file_up_to_down(self):
        if not isinstance(self._view, FileListView):
            return

        up_items = self._view.clw_up.get_selected_items()
        up_files = [item.data(Qt.UserRole) for item in up_items]
        up_texts = [item.text() for item in up_items]

        json_items = self._view.clw_json.get_selected_items()
        json_files = [item.data(Qt.UserRole) for item in json_items]
        json_texts = [item.text() for item in json_items]

        down_items = self._view.clw_down.get_all_items()
        down_files = [item.data(Qt.UserRole) for item in down_items]

        selected_files=up_files+json_files
        selected_texts=up_texts+json_texts
        delta_files = list(set(selected_files) - set(down_files))

        for file in delta_files:
            text = selected_texts[selected_files.index(file)]
            self._view.clw_down.add_item(text, data=file, checkable=True)

        self.fileUpToDown.emit()

    def down_double_clicked(self, item):
        """
        双击item
        :param item:
        :return:
        """

        self.downDoubleClicked.emit(str(item.data(Qt.UserRole)))

    def get_files(self, up=True, choose=GetItemMode.ALL):
        """
        获取文件列表
        :param up: True 上边控件文件列表，False 下边的
        :param choose: 选择的模式
        :return:
        """
        wid = self._view.clw_up if up else self._view.clw_down

        items = []
        if choose == GetItemMode.ALL:
            items = wid.get_all_items()
        elif choose == GetItemMode.SELECTED:
            items = wid.get_selected_items()
        elif choose == GetItemMode.CHECKED:
            items = wid.get_checked_items()

        return [item.data(Qt.UserRole) for item in items]

    def get_json_files(self, up=True, choose=GetItemMode.ALL):
        wid = self._view.clw_json if up else self._view.clw_down
        items = []
        if choose == GetItemMode.ALL:
            items = wid.get_all_items()
        elif choose == GetItemMode.SELECTED:
            items = wid.get_selected_items()
        elif choose == GetItemMode.CHECKED:
            items = wid.get_checked_items()
        return [item.data(Qt.UserRole) for item in items]

    def set_file_state(self, file, dirty=True):
        """
        显示文件为改动状态
        :param file:
        :param dirty: True 加*
        :return:
        """
        if not isinstance(self._view, FileListView):
            return
        items = self._view.clw_down.get_all_items()

        files = self.get_files(False)
        index = files.index(file)

        edited = False
        if action_manager.is_restorable(file, True) or action_manager.is_restorable(file, True):
            edited = True  # 代表该文件被编辑过， 编辑过的文件 √

        if 0 <= index < len(items):
            if dirty:
                text = "   %s*" % osp.basename(file)
            elif edited:
                text = "   %s √" % osp.basename(file)
            else:
                text = "   %s" % osp.basename(file)
            items[index].setText(text)

    def set_enable_file(self, file):
        """
        设置使能文件，其他文件均为非使能
        :param file:
        :return:
        """
        if not isinstance(self._view, FileListView):
            return

        items = self._view.clw_down.get_all_items()

        for item in items:
            if item.data(Qt.UserRole) == file:
                item.setForeground(ENABLE_COLOR)
                item.setFont(ENABLE_FONT)
            else:
                item.setForeground(NORMAL_COLOR)
                item.setFont(NORMAL_FONT)

    def set_hover_file(self, file):
        if not isinstance(self._view, FileListView):
            return

        global last_hover_file

        if file == last_hover_file:
            return

        if last_hover_file == file:
            return

        # print('set_hover_file---- ', file, '   ', last_hover_file)

        items = self._view.clw_down.get_all_items()

        for item in items:
            if item.data(Qt.UserRole) == file:
                item.setBackground(HOVER_BG_COLOR)
            else:
                item.setBackground(NORMAL_BG_COLOR)

        last_hover_file = file

    def set_show_file(self, file, show=True):
        if not isinstance(self._view, FileListView):
            return
        items = self._view.clw_down.get_all_items()
        for item in items:
            if item.data(Qt.UserRole) == file:
                cbx = self._view.clw_down.lw_content.itemWidget(item)
                if hasattr(cbx, "setCheckState"):
                    cbx.setCheckState(Qt.Checked) if show else cbx.setCheckState(Qt.Unchecked)

    def remove_file(self, file):
        """
        删除文件
        :param file:
        :return:
        """
        if not isinstance(self._view, FileListView):
            return

        files = self.get_files(False, GetItemMode.ALL)
        idx = files.index(file)
        if idx is not None:
            self._view.clw_down.lw_content.takeItem(idx)



if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    _view = FileListView()
    c = FileListController(_view)
    c.show()
    sys.exit(app.exec_())
