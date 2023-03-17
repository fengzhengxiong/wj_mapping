#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .common_mode import AreaPickMode


class AreaPickManager():
    def __init__(self):
        self.__pick_mode = AreaPickMode.DEFULT

    def set_pick_mode(self, mode):
        self.__pick_mode = mode

    def get_pick_mode(self):
        return self.__pick_mode


class Singleton(AreaPickManager):
    def foo(self):
        pass

area_pick_manager = Singleton()  # 单例
