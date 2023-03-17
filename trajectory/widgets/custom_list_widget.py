#!/usr/bin/env python
# -*- coding: utf-8 -*-


from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon,QColor,QPalette

from trajectory.UI.listwid_ui import Ui_Form


class CustomListWidget(QtWidgets.QWidget, Ui_Form):
    """
    按钮控制区
    """
    checkStateChange = pyqtSignal()

    def __init__(self, parent=None):
        super(CustomListWidget, self).__init__()
        self._parent = parent
        self.setupUi(self)
        self.__init_ui()
        self.__init_connect()

        self.btn_group = QButtonGroup(self)

    def __init_ui(self):
        if self._parent:
            self.setParent(self._parent)
        self.lw_content.setSelectionMode(QAbstractItemView.ExtendedSelection)  # 多选
        # self.lw_content.setSelectionMode(QAbstractItemView.MultiSelection)  # 多选

    def __init_connect(self):
        self.btn_yes.clicked.connect(lambda: self.change_select(1))
        self.btn_no.clicked.connect(lambda: self.change_select(0))
        self.btn_inverse.clicked.connect(lambda: self.change_select(-1))

    def set_title(self, text):
        self.dok_container.setWindowTitle(text)

    def reset_group_btn(self):
        for btn in self.btn_group.buttons():
            self.btn_group.removeButton(btn)

    def add_item(self, text, data=None, icon=None, checkable=False, checked=Qt.Checked):
        """
        添加item
        :param text: 文本显示
        :param data: 记录的数据
        :param icon: 图标
        :param checkable:是否可勾选
        :param checked: 勾选与否
        :return:
        """
        item = QListWidgetItem()
        item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        # item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
        # item.setFlags(item.flags() | Qt.ItemIsEditable | Qt.ItemIsDropEnabled)

        if data is not None:
            item.setData(Qt.UserRole, data)
            item.setToolTip(str(data))
        if icon:
            item.setIcon(QIcon(icon))

        # 不用item 自带的勾选功能，为了触发方便。
        # if checkable:
        #     checked = Qt.Checked if checked not in [0, 1, 2] else checked
        #     item.setCheckState(checked)
        #     # item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
        #     # item.setFlags(item.flags() | Qt.ItemIsEditable | Qt.ItemIsDropEnabled)

        item.setText(text)
        self.lw_content.addItem(item)
        if checkable:
            cbx_ = QCheckBox()
            cbx_.setCheckState(Qt.Checked)
            cbx_.stateChanged.connect(lambda: self.checkStateChange.emit())
            item.setText("   %s" % text)
            self.lw_content.setItemWidget(item, cbx_)

        self.lw_content.sortItems(Qt.AscendingOrder)

    @property
    def count(self):
        return self.lw_content.count()

    def change_select(self, mode):
        """
        列表选中变化，
        :param mode: 1 全选， 0 不选， -1 反选
        :return:
        """
        if self.count == 0:
            return

        if mode == 0:
            self.lw_content.clearSelection()
        elif mode == 1:
            self.lw_content.selectAll()
        elif mode == -1:
            for i in range(self.count):
                item = self.lw_content.item(i)
                item.setSelected(bool(1 - item.isSelected()))

        # lis = self.lw_content.selectedItems()
        # for i in lis:
        #     print(self.lw_content.indexFromItem(i).row())

    def get_selected_items(self):
        return self.lw_content.selectedItems()

    def get_all_items(self):
        return [self.lw_content.item(i) for i in range(self.count)]

    def get_checked_items(self):
        res = []
        for i in range(self.count):
            item = self.lw_content.item(i)
            widget = self.lw_content.itemWidget(item)
            if hasattr(widget, 'checkState'):
                if widget.checkState() == Qt.Checked:
                    res.append(item)
            # if item.checkState() == Qt.Checked:
            #     res.append(item)
        return res

    def keyPressEvent(self, ev):
        modifiers = ev.modifiers()
        key = ev.key()
        if key == Qt.Key_Escape:
            self.lw_content.clearSelection()

        super(CustomListWidget, self).keyPressEvent(ev)

    def reset(self):
        self.lw_content.clear()



def slot_func(flg):

    print("slot_func --  ", flg)


def slot_btn(val):
    print("slot_btn")
    print(val)

def slot_check():
    print('slot_check ---- ')



if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    _view = CustomListWidget()
    _view.set_title("asdg")

    _view.lw_content.activated.connect(lambda: slot_func(1))
    _view.lw_content.itemActivated.connect(lambda: slot_func(2))
    _view.lw_content.itemChanged.connect(lambda: slot_func(3))
    _view.lw_content.currentTextChanged.connect(lambda: slot_func(4))

    _view.btn_group.buttonToggled.connect(slot_btn)

    _view.checkStateChange.connect(slot_check)

    _view.add_item("adfg", "56", checkable=True)
    _view.add_item("edgh", "56", checkable=True, checked=0)
    _view.add_item("chgh", "56", checkable=True, checked=0)

    print(_view.btn_group.buttons())




    print(_view.count)
    _view.show()

    sys.exit(app.exec_())






