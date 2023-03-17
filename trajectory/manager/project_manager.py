#!/usr/bin/env python
# -*- coding: utf-8 -*-

import copy


class ProjectManager():
    def __init__(self):
        self.__dic_dirty = {}  # key 文件，value: True 代表文件有改动； False 代表clean状态。
        self.enable_file = None  # 当前的使能文件
        self.hover_file = None  # 当前悬浮的文件名
        self.selected_list = []  # 选中点的id列表

        self.on_selected = False  # 鼠标是否悬浮于 被选中的点位上

    def set_dirty(self, file):
        self.__dic_dirty[file] = True

    def set_clean(self, file):
        self.__dic_dirty[file] = False

    def get_dirty(self, file):
        return self.__dic_dirty.get(file, False)

    def is_dirty(self):
        return True in list(self.__dic_dirty.values())

    def get_all_state(self):
        return copy.deepcopy(self.__dic_dirty)

    def remove_file(self, file):
        if file in self.__dic_dirty:
            self.__dic_dirty.pop(file)

    def reset_file_state(self):
        self.__dic_dirty = {}

    def reset(self):
        self.reset_file_state()
        self.enable_file = None
        self.hover_file = None
        self.selected_list = []


class Singleton(ProjectManager):
    def foo(self):
        pass


project_manager = Singleton()  # 单例