#!/usr/bin/env python
# -*- coding: utf-8 -*-

from trajectory.data.mysegment import MySegment
import time
import numpy as np

try:
    import vtkmodules.all as vtk
    from vtkmodules.util.numpy_support import vtk_to_numpy, numpy_to_vtk
    from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
except ImportError:
    import vtk
    from vtk.util.numpy_support import vtk_to_numpy, numpy_to_vtk
    from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor


"""
段显示模型，tag显示模块
"""


class SegModel(object):
    def __init__(self, ren=None, window=None):
        super(SegModel, self).__init__()

        # actor的修改需要渲染器配合使用
        self.ren = ren
        self.window = window

        # 核心数据------------
        self._seg_actor = MySegment()  # 段存储
        self.maxid = None  # 点的最大id号

    @property
    def ren_enable(self):
        return (self.ren is not None and self.window is not None)

    def set_max_id(self, val):
        self.maxid = val

    def set_pin_id(self, pin, id_val):
        """
        强制修改id
        :param pin:
        :param id_val:
        :return:
        """
        obj = self._seg_actor.pin1 if pin == 1 else self._seg_actor.pin2
        obj.set_id(id_val)

    def get_tag_info(self):
        return (self._seg_actor.pin1.get_id,
                self._seg_actor.pin2.get_id,
                self._seg_actor.check_seg_mode(maxid=self.maxid))

    def get_tag_position(self):
        return (self._seg_actor.pin1.get_position(), self._seg_actor.pin2.get_position())

    def create_tag(self, pin, point_id, xyz, rgb):
        """
        创建标签, 由鼠标点击触发
        :param pin: 1 2 图钉号
        :param point_id: 点id
        :param xyz:
        :param rgb:
        :return:
        """
        if not self.ren_enable:
            return False
        r, g, b = rgb[0] / 255, rgb[1] / 255, rgb[2] / 255

        if pin == 1:
            ret = self._seg_actor.create_pin1(self.ren, point_id, pos=xyz, rgb=(r, g, b))
        else:
            ret = self._seg_actor.create_pin2(self.ren, point_id, pos=xyz, rgb=(r, g, b))
        self._seg_actor.check_seg_mode(maxid=self.maxid)
        self.window.Render()

        return ret

    #  点击按钮创建段，区别是不做图钉pin位置合法性判断，直接赋值即可，用set_pin
    def set_tag_head_seg(self, xyz, rgb):
        """
        首段  -1,0  , 给第0个点的xyz 和 rgb
        :param xyz:
        :param rgb:
        :return:
        """

        if not self.ren_enable:
            return False

        r, g, b = rgb[0] / 255, rgb[1] / 255, rgb[2] / 255

        self._seg_actor.set_pin1(self.ren, -1)
        self._seg_actor.set_pin2(self.ren, 0, xyz, rgb=(r, g, b))
        self._seg_actor.check_seg_mode(maxid=self.maxid)
        self.window.Render()
        return True

    def set_tag_tail_seg(self, xyz, rgb):
        """
        首段  maxid,-1  , 给第maxid 点的xyz 和 rgb
        :param xyz:
        :param rgb:
        :return:
        """

        if not self.ren_enable:
            return False

        r, g, b = rgb[0] / 255, rgb[1] / 255, rgb[2] / 255

        self._seg_actor.set_pin1(self.ren, self.maxid, xyz, rgb=(r, g, b))
        self._seg_actor.set_pin2(self.ren, -1)
        self._seg_actor.check_seg_mode(maxid=self.maxid)
        self.window.Render()
        return True

    def set_tag_neighbor_seg(self, xyz, rgb):
        """
        已知pin1 ，自动添加pin2,  需要第二个点的 xyz 和 颜色
        :param xyz:
        :param rgb:
        :return:
        """

        if not self.ren_enable:
            return False

        if self._seg_actor.pin1.get_id is not None and 0 <= self._seg_actor.pin1.get_id < self.maxid:

            r, g, b = rgb[0] / 255, rgb[1] / 255, rgb[2] / 255
            self._seg_actor.set_pin2(self.ren, self._seg_actor.pin1.get_id + 1, xyz, rgb=(r, g, b))
            self._seg_actor.check_seg_mode(maxid=self.maxid)
            self.window.Render()
            return True
        else:
            print("图钉1非法，先设定图钉1位置")
            return False

    def cancel_tag(self):
        if not self.ren_enable:
            return
        self._seg_actor.cancel(self.ren)
        self.window.Render()
        return True

    def reset(self):
        self.cancel_tag()




