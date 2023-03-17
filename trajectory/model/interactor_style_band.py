#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
VTK 交互逻辑 , 用于框选情况
"""

# from PyQt5.QtCore import pyqtSignal, Qt, QObject

from trajectory.local_utils.vtk_util import *
from trajectory.manager.common_mode import AppMode
from trajectory.manager.app_manager import app_manager
from trajectory.manager.event_type import *


# vtkInteractorStyleRubberBandPick
# vtkInteractorStyleRubberBand2D   右键移动 缩放视野
# vtkInteractorStyleRubberBand3D   右键移动 移动视角


class InteractorStyleBand(vtk.vtkInteractorStyleRubberBand2D):
    """
    切换到框选模式才会进入该类   AppMode.AREA_PICK
    """

    def __init__(self, ren=None, renWin=None, callback=None):
        super(InteractorStyleBand, self).__init__()
        self.callback = callback
        self.ren = ren
        self.renWin = renWin
        # self.SetInteractor(self.renWin.GetInteractor())
        self.__init_picker()
        self.__init_observer()

        # self.StartSelect()
        self.left_press_pos = None  # 左键按下时记录的坐标，送开后置为None

        self._left_pressing = False
        self._mid_pressing = False


    def __init_picker(self):
        # picker
        self.pointPicker = vtk.vtkPointPicker()  # 点拾取
        self.pointPicker.AddObserver(vtk.vtkCommand.PickEvent, self.point_pick)
        self.pointPicker.SetUseCells(1)
        # print(self.pointPicker.GetTolerance())
        self.pointPicker.SetTolerance(0.015)

        self.areaPicker = vtk.vtkAreaPicker()  # 多点拾取
        self.renWin.GetInteractor().SetPicker(self.areaPicker)
        self.areaPicker.AddObserver(vtk.vtkCommand.EndPickEvent, self.area_end_pick)

    def __init_observer(self):
        self.AddObserver(vtk.vtkCommand.LeftButtonPressEvent, self.left_button_press_event)
        self.AddObserver(vtk.vtkCommand.LeftButtonReleaseEvent, self.left_button_release_event)
        self.AddObserver(vtk.vtkCommand.MouseMoveEvent, self.mouse_move_event)
        # self.AddObserver(vtk.vtkCommand.MiddleButtonPressEvent, self.middle_button_press_event)
        # self.AddObserver(vtk.vtkCommand.MiddleButtonReleaseEvent, self.middle_button_release_event)


        #  键盘按键事件绑定
        self.AddObserver(vtk.vtkCommand.KeyReleaseEvent, self.key_release_event)
        self.AddObserver(vtk.vtkCommand.KeyPressEvent, self.key_press_event)
        self.AddObserver(vtk.vtkCommand.LeaveEvent, self.leave_event)
        self.AddObserver(vtk.vtkCommand.EnterEvent, self.enter_event)

    def set_pointpicker_proplist(self, actors):
        """设置点拾取器对象列表"""
        self.pointPicker.InitializePickList()
        for actor in actors:
            self.pointPicker.AddPickList(actor)
        self.pointPicker.PickFromListOn()
        self.pointPicker.Modified()

    def get_pointpicker_proplist(self):
        props = self.pointPicker.GetPickList()
        props.InitTraversal()
        num = props.GetNumberOfItems()
        proplist = []
        for i in range(num):
            proplist.append(props.GetNextProp())
        return proplist

    def remove_picked_actor(self, actors):
        proplist = self.get_pointpicker_proplist()
        for actor in actors:
            if actor in proplist:
                self.pointPicker.DeletePickList(actor)
        self.pointPicker.PickFromListOn()
        self.pointPicker.Modified()

    def clear_picked_list(self):
        """
        清空point picker 列表
        :return:
        """
        proplist = self.get_pointpicker_proplist()
        for actor in proplist:
            self.pointPicker.DeletePickList(actor)
        self.pointPicker.PickFromListOn()

    def left_button_press_event(self, obj, event):
        """
        左键按下, 记录坐标

        :param obj:
        :param event:
        :return:
        """
        # print('行:', sys._getframe().f_lineno, ' ', sys._getframe().f_code.co_name)
        click_pos = self.GetInteractor().GetEventPosition()
        self._left_pressing = True
        self.left_press_pos = (click_pos[0], click_pos[1])
        self.OnLeftButtonDown()


    def left_button_release_event(self, obj, event):
        self._left_pressing = False
        click_pos = self.GetInteractor().GetEventPosition()
        self.OnLeftButtonUp()  # 必须放在AreaPick 前边 ，刷新才实时
        if self.left_press_pos:
            # AreaPick 触发 area_end_pick
            self.areaPicker.AreaPick(self.left_press_pos[0],
                                     self.left_press_pos[1],
                                     click_pos[0],
                                     click_pos[1],
                                     self.ren)

            self.left_press_pos = None
        # self.OnLeftButtonUp()

    def mouse_move_event(self, obj, event):

        if not self._left_pressing:
            click_pos = self.GetInteractor().GetEventPosition()
            self.pointPicker.Pick(click_pos[0], click_pos[1], 0, self.ren)  # 当有pick目标时，才触发point_pick
            pick_obj = self.pointPicker.GetActor()  # 当前在pick的 actor

            if self.GetInteractor().GetShiftKey():
                ev = EV_MOUSE_HOVER_SEG
            else:
                ev = EV_MOUSE_HOVER
            if self.callback and ev:
                self.callback(ev=ev,
                              obj=pick_obj,
                              id=self.pointPicker.GetPointId(),
                              pos=self.pointPicker.GetPickPosition())
        self.OnMouseMove()

        # elif self._mid_pressing:
        #     self.Pan()

    def middle_button_press_event(self, obj, event):
        self._mid_pressing = True

        self.OnMiddleButtonDown()

    def middle_button_release_event(self, obj, event):
        self._mid_pressing = False
        self.OnMiddleButtonUp()

    def point_pick(self, obj, event):
        # print('point_pick ---------- ')
        pass

    def area_end_pick(self, obj, event):
        """
        EndPickEvent
        :param obj:
        :param event:
        :return:
        """
        # print('area_end_pick')
        if self.callback:
            self.callback(ev=EV_AREA_PICK,
                          picker=obj)




    def key_press_event(self, obj, event):
        """
        辅助按键 GetAltKey 是不可用的 ，GetControlKey，GetShiftKey 可以
        :param obj:
        :param event:
        :return:
        """
        key = self.GetInteractor().GetKeySym()
        # print("key = {}".format(key))
        # print(obj)
        # print(event)

        if key == 'r':
            pass
        elif key == 'Escape':
            if self.callback:
                self.callback(ev=EV_RESET_SELECT)

        # super().OnKeyPress()
        self.OnKeyPress()

    def key_release_event(self, obj, event):
        key = self.GetInteractor().GetKeySym()
        # super().OnKeyRelease()
        self.OnKeyRelease()

    def leave_event(self, obj, event):
        self.OnLeave()

    def enter_event(self, obj, event):
        self.OnEnter()

    def update_cursor_shape(self):
        """
        更新鼠标指针样式
        :return:
        """
        self.renWin.SetCurrentCursor(vtk.VTK_CURSOR_CROSSHAIR)

