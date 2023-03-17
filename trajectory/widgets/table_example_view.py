#!/usr/bin/env python
# -*- coding: utf-8 -*-


from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import QtCore

from trajectory.local_utils.qt_util import *

import copy

import sys
import numpy as np


class TableExampleView(QWidget):
    def __init__(self, parent=None):
        super(TableExampleView, self).__init__(parent)

        self.__init_ui()

        # filename = r'D:\py_project\collisionpath\maping1.txt'
        # self.table_sitting(filename)

        # self.__init_connect()


    def __init_ui(self):
        self.table = QTableWidget()
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)  # 设置表格的选取方式是行选取
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 不可编辑
        fill_widget(self, 1, [self.table], margin=(0, 0, 0, 0))

        # self.addItem=QPushButton("添加数据")
        # self.deleteItem = QPushButton("删除数据")
        # self.editItem=QPushButton("确认编辑")
        # self.saveItem=QPushButton("保存数据")


    def __init_connect(self):
        self.addItem.clicked.connect(self._addItem)
        self.deleteItem.clicked.connect(self._deleteItem)
        self.editItem.clicked.connect(self._editItem)
        self.saveItem.clicked.connect(self._saveItem)

    def table_sitting(self, filename):
        self.oriArray = np.loadtxt(filename, delimiter=',', dtype=float)
        self.table.setRowCount(self.oriArray.shape[0])
        self.table.setColumnCount(self.oriArray.shape[1])
        # self.table.setHorizontalHeaderLabels(
        #     ["经度", "纬度", "地图属性", "设定速度", "车道状态", "并道属性", "道路状态", "转向灯状态",
        #      "右侧临时停车偏移距离", "自车道宽度", "左车道宽度", "右车道宽度", "轨迹左侧安全距离", "轨迹右侧安全距离",
        #      "航向角", "Gps时间", "卫星个数"])
        # for row in range(self.oriArray.shape[0]):
        #     for col in range(self.oriArray.shape[1]):
        #         self.table.setItem(row, col, QTableWidgetItem(str(self.oriArray[row][col])))

    def _addItem(self):
        row_select = self.table.selectedItems()
        if len(row_select) == 0:
            return
        num = row_select[0].row() + 1
        self.table.insertRow(num)
        for i in range(len(row_select)):
            self.table.setItem(num, i, QTableWidgetItem(str(row_select[i].text())))
        self.oriArray = np.insert(self.oriArray, num, self.oriArray[num - 1], axis=0)
        self.update()

    def _deleteItem(self):
        row_select = self.table.selectedItems()
        if len(row_select) == 0:
            return
        selected_rows = []  # 求出所选择的行数(从0开始)
        for i in row_select:
            row = i.row()
            if row not in selected_rows:
                selected_rows.append(row)
        for r in range(len(sorted(selected_rows))):
            self.table.removeRow(selected_rows[r] - r)  # 删除行
            self.oriArray = np.delete(self.oriArray, selected_rows[r] - r, axis=0)
        self.update()

    def _editItem(self):
        row_select = self.table.selectedItems()
        if len(row_select) == 0:
            return
        odd_data = self.oriArray[row_select[0].row()][row_select[0].column()]
        new_data = row_select[0].text()
        if odd_data != new_data:
            self.oriArray[row_select[0].row()][row_select[0].column()] = new_data
        self.update()

    def _saveItem(self):
        myfmt = ['%4.7f', '%4.7f', '%d', '%d', '%d', '%d', '%d', '%d', '%.2f', '%.2f', '%.2f', '%.2f', '%.2f', '%.2f',
                 '%.2f', '%d', '%d']
        np.savetxt('1.txt', self.oriArray, fmt=myfmt, delimiter=',')

    def _clearItem(self):
        self.table.setRowCount(0)
        self.table.setColumnCount(0)
        self.table.clearContents()


def main():
    print('========原始数据==========')
    x = np.array(np.arange(0, 16).reshape(4, 4))
    print(x)

    # 删除行：
    print('========删除第二行后==========')
    x1 = np.delete(x, 3, axis=0)
    print(x1)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    dlg = TableExampleView()
    dlg.show()
    sys.exit(app.exec_())
