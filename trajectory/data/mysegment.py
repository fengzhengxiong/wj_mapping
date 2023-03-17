#!/usr/bin/env python
# -*- coding: utf-8 -*-


from trajectory.data.pointpin import PointPin
from trajectory.manager.common_mode import SegMode


class MySegment(object):

    def __init__(self):
        self.pin1 = PointPin()
        self.pin2 = PointPin()

        self.pin1.set_scale(1.2)
        self.pin2.set_scale(1.2)

        self.pin1.set_silhouette_color((1, 0, 0))
        self.pin2.set_silhouette_color((0, 0, 1))

        self._seg_mode = SegMode.SEG_NONE

    def check_seg_mode(self, maxid=100):
        """
        检验段含义
        :return:
        """
        self._seg_mode = SegMode.SEG_NONE
        if None in [self.pin1.get_id, self.pin2.get_id]:
            pass
        elif self.pin1.get_id == -1 and self.pin2.get_id == 0:
            self._seg_mode = SegMode.SEG_HEAD
        elif self.pin1.get_id == maxid and self.pin2.get_id == -1:
            self._seg_mode = SegMode.SEG_TAIL
        elif self.pin2.get_id - self.pin1.get_id == 1:
            self._seg_mode = SegMode.SEG_CLOSE
        elif -1 in [self.pin1.get_id, self.pin2.get_id]:
            pass
        else:
            self._seg_mode = SegMode.SEG_NORMAL

        return self._seg_mode

    def set_pin1(self, ren, pointid=-1, pos=(0, 0, 0), rgb=(1, 0, 0)):
        """
        设置图钉1 位置，及显示它
        """
        self.pin1.set_id(pointid)
        self.pin1.remove_by_render(ren)
        if pointid >= 0:
            self.pin1.set_position(pos)
            self.pin1.set_property(color=rgb)
            self.pin1.add_by_render(ren)

    def set_pin2(self, ren, pointid=-1, pos=(0, 0, 0), rgb=(1, 0, 0)):
        """
        设置图钉2 位置，及显示它
        """
        self.pin2.set_id(pointid)
        self.pin2.remove_by_render(ren)
        if pointid >= 0:
            self.pin2.set_position(pos)
            self.pin2.set_property(color=rgb)
            self.pin2.add_by_render(ren)

    def create_pin1(self, ren, pointid=-1, pos=(0, 0, 0), rgb=(1, 0, 0)):
        """
        手动点击图钉1，若图钉2 id是-1，则归置为None
        """
        self.set_pin1(ren, pointid, pos, rgb)
        if self.pin2.get_id is not None and self.pin2.get_id < 0:
            self.pin2.set_id(None)
            self.pin2.remove_by_render(ren)
        return True

    def create_pin2(self, ren, pointid=-1, pos=(0, 0, 0), rgb=(1, 0, 0)):
        """
        鼠标点击生成图钉，需要进行判定
        """
        if self.pin1.get_id is not None and self.pin1.get_id >= 0:
            self.set_pin2(ren, pointid, pos, rgb)
            return True
        else:
            print("起始点的图钉非使能，请先确定起点图钉")
            return False

    def cancel(self, ren):
        """
        点击取消，装钉不显示，非使能。
        :param ren:
        :return:
        """
        self.reset()
        self.remove_by_render(ren)

    def reset(self):
        self.pin1.set_id(None)
        self.pin2.set_id(None)
        self.check_seg_mode()

    def remove_by_render(self, ren):
        self.pin1.remove_by_render(ren)
        self.pin2.remove_by_render(ren)



