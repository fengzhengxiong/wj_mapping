#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import numpy as np
import copy
import os
import os.path as osp
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import *
from trajectory.widgets.table_example_view import TableExampleView
from trajectory.manager.action_manager import ActionData, ActionMode, action_manager
from trajectory.config.file_type import ID_PROPERTY, save_dir, file_fmt
from trajectory.model.data_model import DataModel
from trajectory.local_utils.qt_util import *


class TableListView(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(TableListView, self).__init__()
        self._parent = parent
        self.files = {}  # key 文件名， value tab名
        self.datas = {}  # key 文件名 value datas(np数组)
        self.filetable_index=[]  #用来关闭table时候用的列表
        self._init_ui()
        self.Data_Model = DataModel()

    def _init_ui(self):
        if self._parent:
            self.setParent(self._parent)
        self.tab_edit_widget = QTabWidget(self)
        self.tab_edit_widget.setTabPosition(QTabWidget.South)
        self.tab_edit_widget.tabCloseRequested.connect(self.close_table)
        fill_widget(self, 1, [self.tab_edit_widget], (0,0,0,0))

    def close_table(self,file):
        index=self.filetable_index.index(file)
        if index is None:
            return False
        self.tab_edit_widget.removeTab(index)
        del self.filetable_index[index]
        # print(index,"=============================",self.filetable_index)

    def clear_table(self):
        self.tab_edit_widget.clear()

    def create_table(self, filenames, datas):
        self.files.clear()
        self.datas.clear()
        self.filetable_index.clear()
        try:
            for i in range(len(filenames)):
                data = datas[i]

                aa = TableExampleView(self)
                aa.setParent(self.tab_edit_widget)

                strname = filenames[i].split("\\")[1]
                self.tab_edit_widget.addTab(aa, strname)

                self.files[filenames[i]] = aa
                self.datas[filenames[i]] = data
                self.filetable_index.append(filenames[i])

                aa.table.setRowCount(data.shape[0])
                aa.table.setColumnCount(data.shape[1])
                aa.table.setHorizontalHeaderLabels(
                    ["经度", "纬度", "地图属性", "设定速度", "车道状态", "并道属性", "道路状态", "转向灯状态",
                     "右侧临时停车偏移距离", "自车道宽度", "左车道宽度", "右车道宽度", "轨迹左侧安全距离",
                     "轨迹右侧安全距离",
                     "航向角", "Gps时间", "卫星个数"])
                for row in range(data.shape[0]):
                    for col in range(data.shape[1]):
                        aa.table.setItem(row, col, QTableWidgetItem(str(data[row][col])))
        except Exception as e:
            print('行:', sys._getframe().f_lineno, ' ', sys._getframe().f_code.co_name)
            print(e)

    def edit_row_tble(self, file, row_idx, datas):
        enable_tab = self.files[file]
        if enable_tab is None:
            return False
        enable_data = self.datas[file]
        if enable_data is None:
            return False
        for i in range(len(row_idx)):
            for j in range(datas.shape[1]):
                enable_tab.table.setItem(row_idx[i], j, QTableWidgetItem(str(datas[i][j])))
            enable_data[row_idx[i]] = datas[i]
        self.datas[file] = enable_data
        self.update()

    def del_row_table(self, file, row_idx):
        print(file, " ============", row_idx)
        if len(row_idx) == 0:
            return
        enable_tab = self.files[file]
        if enable_tab is None:
            return False
        enable_data = self.datas[file]
        if enable_data is None:
            return False
        for i in range(len(row_idx)):
            enable_tab.table.removeRow(row_idx[i] - i)
            enable_data = np.delete(enable_data, row_idx[i] - i, axis=0)
        self.datas[file] = enable_data
        self.update()
        pass

    def add_row_table(self, file, row_idx, datas):
        enable_tab = self.files[file]
        if enable_tab is None:
            return  False
        enable_data = self.datas[file]
        if enable_data is None:
            return False
        for i in range(datas.shape[0]):
            enable_tab.table.insertRow(row_idx)
            for j in range(datas.shape[1]):
                enable_tab.table.setItem(row_idx, j, QTableWidgetItem(str(datas[i][j])))
            enable_data = np.insert(enable_data, row_idx, datas[i], axis=0)
            row_idx = row_idx + 1
        self.datas[file] = enable_data
        self.update()

    def get_row_table_info(self, file, row_idx):
        enable_data = self.datas[file]
        if enable_data is None:
            return False
        return enable_data[row_idx]

    def restore_data(self, action_obj, undo):
        if not isinstance(action_obj, ActionData):
            return False
        print('=======行:', sys._getframe().f_lineno, ' ', sys._getframe().f_code.co_name)
        try:
            this_file = action_obj.get_other_data().get('file', None)
            if not this_file:
                print('data model restore_data error ')
                return False
            this_tab = self.files[this_file]
            if this_tab is None:
                return False
            this_data = self.datas[this_file]
            if this_data is None:
                return False

            if action_obj.action == ActionMode.ADD:
                self._restore_add(this_file, action_obj.data, action_obj.ids, undo)
                pass
            elif action_obj.action == ActionMode.SUB:
                self._restore_sub(this_file, action_obj.data, action_obj.ids, undo)
                pass
            elif action_obj.action == ActionMode.EDIT:
                self._restore_edit(this_file, action_obj.data, action_obj.ids, undo)
                pass

        except Exception as e:
            print('=======行:', sys._getframe().f_lineno, ' ', sys._getframe().f_code.co_name)
            print(e)

    def _restore_add(self, file, data, ids, undo):
        print('_restore_add --------')
        enable_tab = self.files[file]
        if enable_tab is None:
            return False
        enable_data = self.datas[file]
        if enable_data is None:
            return False
        if undo:
            for i in range(data.shape[0]):
                enable_tab.table.removeRow(ids[0])
                enable_data = np.delete(enable_data, ids[0], axis=0)
            self.datas[file] = enable_data
            self.update()
        else:
            for i in range(data.shape[0]):
                enable_tab.table.insertRow(ids[0] + i)
                for j in range(data.shape[1]):
                    enable_tab.table.setItem(ids[0] + i, j, QTableWidgetItem(str(data[i][j])))
                enable_data = np.insert(enable_data, ids[0] + i, data[i], axis=0)
            self.datas[file] = enable_data
            self.update()

    def _restore_sub(self, file, data, ids, undo):
        print('_restore_sub --------')
        enable_tab = self.files[file]
        if enable_tab is None:
            return False
        enable_data = self.datas[file]
        if enable_data is None:
            return False
        if undo:
            for i in range(len(ids)):
                enable_tab.table.insertRow(ids[i])
                for j in range(data.shape[1]):
                    enable_tab.table.setItem(ids[i], j, QTableWidgetItem(str(data[i][j])))
                enable_data = np.insert(enable_data, ids[i], data[i], axis=0)
            self.datas[file] = enable_data
            self.update()
        else:
            for i in range(len(ids)):
                enable_tab.table.removeRow(ids[i] - i)
                enable_data = np.delete(enable_data, ids[i] - i, axis=0)
            self.datas[file] = enable_data
            self.update()

    def _restore_edit(self, file, data, ids, undo):
        print('_restore_edit --------')
        enable_tab = self.files[file]
        if enable_tab is None:
            return False
        enable_data = self.datas[file]
        if enable_data is None:
            return False
        _data = np.copy(data[0]) if undo else np.copy(data[1])  # 新数据 旧数据
        for i in range(len(ids)):
            for j in range(_data.shape[1]):
                enable_tab.table.setItem(ids[i], j, QTableWidgetItem(str(_data[i][j])))
            enable_data[ids[i]] = _data[i]
        self.datas[file] = enable_data
        self.update()

    def save_file(self, file):
        enable_data = self.datas[file]
        if enable_data is None:
            print("save_file  not exist={}".format(file))
            return False
        tardir = osp.join(osp.dirname(file), save_dir)
        if not osp.exists(tardir):
            os.makedirs(tardir)
        tarfile = osp.join(tardir, osp.basename(file))
        print('tarfile=', tarfile)
        try:
            np.savetxt(tarfile, enable_data, fmt=file_fmt, delimiter=',')
        except Exception as e:
            print(e)


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    _view = TableListView()
    _view.show()
    sys.exit(app.exec_())
