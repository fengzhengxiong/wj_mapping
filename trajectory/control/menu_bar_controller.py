#!/usr/bin/env python
# -*- coding: utf-8 -*-

from functools import partial

from PyQt5.QtWidgets import *

from trajectory.local_utils.qt_util import *
from trajectory.local_utils.pub import *
import trajectory.config.resource


class MenuBarController(object):
    def __init__(self, mainwindow=None, *args, **kwargs):
        super(MenuBarController, self).__init__()
        self._mainwindow = mainwindow

        self._bar = QMenuBar(self._mainwindow)
        self.__init_actions()
        self.__init_menu()
        if isinstance(self._mainwindow, QMainWindow):
            self._mainwindow.setMenuBar(self._bar)

    def __init_actions(self):
        action = partial(newAction, self._bar)
        quit = action(
            text="退出",
            slot=None,
            shortcut="Ctrl+Shift+Q",
            tip="quit",
            icon="quit",
        )
        opendir = action(
            text='打开文件夹',
            slot=None,
            shortcut='Ctrl+U',
            tip='打开txt文件夹',
            icon='opendir',
        )

        openfile = action(
            text='打开文件',
            slot=None,
            shortcut='Ctrl+O',
            tip='打开车道线txt文件',
        )

        openjsonfile = action(
            text='打开json文件夹',
            slot=None,
            shortcut='Ctrl+K',
            tip='打开高精度地图json文件',
        )

        savefile = action(
            text='保存',
            slot=None,
            shortcut='Ctrl+S',
            tip='保存',
            icon='save_all'
        )

        enablefile = action(
            text='使能文件',
            slot=None,
            shortcut='B',
            tip='切换使能文件',
        )

        undo = action(
            text='undo',
            slot=None,
            shortcut='Ctrl+Z',
            tip='撤回',
            icon='undo',
        )

        redo = action(
            text='redo',
            slot=None,
            shortcut='Ctrl+Shift+Z',
            tip='redo',
            icon='redo',
        )

        shortcutExplain = action(
            text='使用说明',
            slot=None,
            tip='快捷键使用',
            # icon='redo',
        )

        about = action(
            text='关于',
            slot=None,
            tip='关于软件',
            icon='wanji32',
        )


        self.actions = struct(
            quit=quit, opendir=opendir, openfile=openfile,  openjsonfile=openjsonfile, savefile=savefile, enablefile=enablefile,
            undo=undo, redo=redo, shortcutExplain=shortcutExplain, about=about,
        )

    def __init_menu(self):
        # self.menus = struct(
        #     file=self.menu('&文件'),
        #     edit=self.menu('&编辑'),
        # )
        # addActions(self.menus.file, (self.actions.openfile, self.actions.savefile, None, self.actions.quit))

        self.file = self._bar.addMenu('&文件')
        self.edit = self._bar.addMenu("&编辑")
        self.help = self._bar.addMenu("&帮助")
        addActions(self.file, (self.actions.opendir, self.actions.openfile,  self.actions.openjsonfile, self.actions.savefile, None, self.actions.quit))
        addActions(self.edit, (self.actions.enablefile, self.actions.undo, self.actions.redo,))
        addActions(self.help, (self.actions.shortcutExplain, None, self.actions.about))

    def menu(self, title, actions=None):
        menu = self._bar.addMenu(title)
        if actions:
            addActions(menu, actions)
        return menu

    @property
    def menubar(self):
        return self._bar

    def show(self):
        if self._mainwindow:
            self._mainwindow.show()
        else:
            self.wid_menu = QWidget()
            self.wid_menu.setFixedHeight(30)
            self._bar.setParent(self.wid_menu)
            fill_widget(self.wid_menu, 1, [self._bar], (0,0,0,0))
            self.wid_menu.show()


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    win = QMainWindow()
    c = MenuBarController()
    c.show()
    sys.exit(app.exec_())

