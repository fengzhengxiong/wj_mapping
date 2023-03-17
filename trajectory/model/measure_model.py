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

from trajectory.local_utils.vtk_util import get_distance_widget
from PyQt5.QtCore import QObject, pyqtSignal


class MeasureModel(QObject):
    showDistance = pyqtSignal(tuple)

    def __init__(self, ren=None, window=None):
        super(MeasureModel, self).__init__()

        # actor的修改需要渲染器配合使用
        self.ren = ren
        self.window = window
        self.iren = self.window.GetInteractor() if self.window else None
        self.dis_wid = None

        if self.iren:
            self.__init_dis_wid()

    def __init_dis_wid(self):
        self.dis_wid = get_distance_widget(self.iren)
        self.dis_wid.AddObserver(vtk.vtkCommand.InteractionEvent, self.dis_wid_interacting)
        self.dis_wid.AddObserver(vtk.vtkCommand.EndInteractionEvent, self.dis_wid_interact_end)

    def dis_wid_interacting(self, obj, event):
        """
        控件触发中，持续更新端点
        :param obj:
        :param event:
        :return:
        """
        # print('行:', sys._getframe().f_lineno, ' ', sys._getframe().f_code.co_name)
        # print(obj, ' ', event)
        # dian1 = [0.0]*3
        # obj.GetRepresentation().GetPoint1DisplayPosition(dian1)
        # print(dian1)
        wp1 = obj.GetRepresentation().GetPoint1WorldPosition()
        wp2 = obj.GetRepresentation().GetPoint2WorldPosition()

        # wp1 = np.asarray(wp1)
        # wp2 = np.asarray(wp2)
        # L = np.linalg.norm(wp2 - wp1)
        # print('dain1 = ', obj.GetRepresentation().GetPoint1WorldPosition())
        # print('dain2 = ', obj.GetRepresentation().GetPoint2WorldPosition())
        # print('dis = ', obj.GetRepresentation().GetDistance())
        # print('L = ', L)
        # vtk.vtkDistanceRepresentation3D().SetRulerDistance()
        self.showDistance.emit((wp1, wp2))

    def dis_wid_interact_end(self, obj, event):
        """
        测距控件松手后，触发
        :param obj:
        :param event:
        :return:
        """
        pass

    def set_distance_wid(self, handle, pos):
        """
        设置控件端点位置
        :param handle: 端点号
        :param pos: 位置
        :return:
        """
        if self.dis_wid is None:
            return

        _f = self.dis_wid.GetRepresentation().SetPoint1WorldPosition \
            if handle == 1 else self.dis_wid.GetRepresentation().SetPoint2WorldPosition
        try:
            _f(pos)
            self.dis_wid_interacting(self.dis_wid, 'EndInteractionEvent')
            self.window.Render()
        except Exception as e:
            print("set_distance_wid error ", e)

    def get_enabled(self):
        if self.dis_wid is None:
            return False
        if self.dis_wid.GetEnabled() > 0:
            return True
        else:
            return False

    def set_enabled(self, enabel=True):
        if self.dis_wid is None:
            return

        if enabel:
            self.dis_wid.SetWidgetStateToStart()
            self.dis_wid.EnabledOn()
            self.dis_wid.On()
        else:
            self.dis_wid.EnabledOff()
            self.dis_wid.Off()

    def reset(self):
        self.set_enabled(False)







