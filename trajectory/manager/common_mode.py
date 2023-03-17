#!/usr/bin/env python
# -*- coding: utf-8 -*-


# 通用模式枚举设定

class AppMode():
    # 应用模式
    DEFULT = 0          # 普通默认模式
    AREA_PICK = 1       # 区域选取模式
    ADD_POINT = 2       # 添加点模式
    ADD_POINT_AUTO = 3  # 自动插值模式


class SegMode():
    """
    段属性设定
    种类有 首段-1,0 ； 尾段 max，-1 ； 邻段 x，x+1 ； 其他; 非法
    """

    SEG_HEAD = 1
    SEG_TAIL = 2
    SEG_CLOSE = 3
    SEG_NORMAL = 0
    SEG_NONE = None


class AreaPickMode():
    # 应用模式
    DEFULT = 0  # 普通默认模式
    ADD_PICK = 1  # 加选
    SUB_PICK = 2  # 减选
    INVERSE_PICK = 3  # 反选


class ActionMode():
    ADD = 0
    SUB = 1
    EDIT = 2


class GetItemMode():
    """用于获取列表 item 模式"""
    ALL = 0  # 所有item
    SELECTED = 1  # 获取选中item
    CHECKED = 2  # 获取勾选item


