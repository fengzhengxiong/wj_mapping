#!/usr/bin/env python
# -*- coding: utf-8 -*-

from functools import partial

from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QSize, QObject

from trajectory.local_utils.qt_util import *
from trajectory.local_utils.pub import *


class ToolBarController(QObject):
    def __init__(self, mainwindow=None, location=Qt.TopToolBarArea, *args, **kwargs):
        super(ToolBarController, self).__init__()
        self._mainwindow = mainwindow

        self._bar = QToolBar(self._mainwindow)

        if isinstance(self._mainwindow, QMainWindow):
            # self._mainwindow.toolBarArea(self._bar)
            self._mainwindow.addToolBar(location, self._bar)
            self._bar.setParent(self._mainwindow)
            self._bar.setFixedHeight(30)

    def add_action(self, action=None):
        if action is None:
            self._bar.addSeparator()
        else:
            self._bar.addAction(action)

    def add_widget(self, widget=None):
        if widget is None:
            self._bar.addSeparator()
        else:
            self._bar.addWidget(widget)

    def add_actions(self, actions):
        for action in actions:
            if action is None:
                self._bar.addSeparator()
            elif isinstance(action, QAction):
                self.add_action(action)
            elif isinstance(action, QWidget):
                self.add_widget(action)

    @property
    def toolbar(self):
        return self._bar


    def foo(self):
        action = partial(newAction, self._bar)
        opendir = action(text='打开文件夹',)
        openfile = action( text='打开文件',)
        savefile = action(text='保存',)
        self.add_action(opendir)
        self.add_action(openfile)
        self.add_action(None)
        self.add_action(savefile)

    def show(self):
        self.foo()
        if self._mainwindow:
            self._mainwindow.show()
        else:
            self.wid_menu = QWidget()
            # self.wid_menu.setFixedHeight(15)
            self._bar.setParent(self.wid_menu)
            fill_widget(self.wid_menu, 1, [self._bar], (0, 0, 0, 0))
            self.wid_menu.show()


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    win = QMainWindow()
    c = ToolBarController(win, Qt.TopToolBarArea)
    c.show()
    sys.exit(app.exec_())
