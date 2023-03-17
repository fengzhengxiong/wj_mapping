#!/usr/bin/env python
# -*- coding: utf-8 -*-


from .common_mode import AppMode
from trajectory.config.common_variable import vtk_move_sensitivity


class AppManager():
    def __init__(self):
        self.__app_mode = AppMode.DEFULT

        self.vtk_move_sensitivity = vtk_move_sensitivity

    def set_app_mode(self, mode):
        self.__app_mode = mode

    def get_app_mode(self):
        return self.__app_mode


class Singleton(AppManager):
    def foo(self):
        pass

app_manager = Singleton()  # 单例
