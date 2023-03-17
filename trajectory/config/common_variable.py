#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 点大小显示
point_actor_size = {
    "normal": 3,
    "selected": 8,
    "hover": 12,
    "new": 5,
}

# 点旋转速率， 度
point_rot_speed = {
    "normal": 1.0,
    "slow": 0.5,
    "fast": 5.0
}

# VTK鼠标拖动视野灵敏度 , 取值 1 ~ 10
vtk_move_sensitivity = 2


from PyQt5.QtGui import QColor, QBrush, QFont

NORMAL_COLOR = QColor(0, 0, 0, 255)
ENABLE_COLOR = QColor(34, 139, 34, 200)
NORMAL_FONT = QFont()
ENABLE_FONT = QFont()
ENABLE_FONT.setFamily("微软雅黑")
ENABLE_FONT.setBold(True)

NORMAL_BG_COLOR = QColor(255, 255, 255, 255)  # 背景色
HOVER_BG_COLOR = QColor(100, 100, 200, 180)

shortcut_explain = \
    "拖动视野 - 左键、中键\n"\
    "选中单点 - 右键单击\n" \
    "悬浮段 - shift\n"\
    "选中段 - shift + 左键\n"\
    "标签选段 - ctrl+left/right\n"\
    "移动选中点 - 中键拖动(光标十字)\n"\
    "旋转选中点 - A/D键\n"\
    "增加点 - 左键(插值模式)"