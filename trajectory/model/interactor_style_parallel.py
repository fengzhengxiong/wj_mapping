#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
VTK 交互逻辑
"""

import time
# from PyQt5.QtCore import pyqtSignal, Qt, QObject

from trajectory.local_utils.vtk_util import *
from trajectory.manager.common_mode import AppMode
from trajectory.manager.app_manager import app_manager
from trajectory.manager.project_manager import project_manager
from trajectory.manager.event_type import *
from trajectory.config.common_variable import point_rot_speed, vtk_move_sensitivity


# vtkInteractorStyleRubberBandPick
# vtkInteractorStyleRubberBand2D
# vtkInteractorStyleRubberBand3D
# vtkParallelCoordinatesInteractorStyle
# vtkInteractorStyleTrackballCamera

class InteractorStyleParallel(vtk.vtkInteractorStyleTrackballCamera):
    """
    该类实现 ，屏蔽左键旋转相机视角功能， 改为平移，有两种实现方式：
    1.  self.StartPan()  —— OnMouseMove (或self.Pan) —— self.EndPan
    2 . mouse_move_event  :  self.Pan

    """

    def __init__(self, ren=None, renWin=None, callback=None):
        super(InteractorStyleParallel, self).__init__()
        self.callback = callback
        self.ren = ren
        self.renWin = renWin

        self.__init_picker()
        self.__init_observer()

        self._left_pressing = False
        self._mid_pressing = False
        self._right_pressing = False

        self.left_press_pos = None  # 左键按下时记录的坐标，送开后置为None

        self.moving_pos = None  # 实时坐标

        self.last_time = time.time()

    def __init_picker(self):
        # picker
        self.pointPicker = vtk.vtkPointPicker()  # 点拾取
        self.pointPicker.AddObserver(vtk.vtkCommand.PickEvent, self.point_pick)
        self.pointPicker.SetUseCells(1)
        # print(self.pointPicker.GetTolerance())
        self.pointPicker.SetTolerance(0.015)

    def __init_observer(self):
        self.AddObserver(vtk.vtkCommand.LeftButtonPressEvent, self.left_button_press_event)
        self.AddObserver(vtk.vtkCommand.LeftButtonReleaseEvent, self.left_button_release_event)
        self.AddObserver(vtk.vtkCommand.RightButtonPressEvent, self.right_button_press_event)
        self.AddObserver(vtk.vtkCommand.RightButtonReleaseEvent, self.right_button_release_event)
        self.AddObserver(vtk.vtkCommand.MouseMoveEvent, self.mouse_move_event)
        self.AddObserver(vtk.vtkCommand.MouseWheelBackwardEvent, self.mouse_wheel_backward_event)
        self.AddObserver(vtk.vtkCommand.MouseWheelForwardEvent, self.mouse_wheel_forward_event)

        self.AddObserver(vtk.vtkCommand.MiddleButtonPressEvent, self.middle_button_press_event)
        self.AddObserver(vtk.vtkCommand.MiddleButtonReleaseEvent, self.middle_button_release_event)

        # self.AddObserver(vtk.vtkCommand.LeftButtonDoubleClickEvent, self.left_button_double_click_event)
        # self.AddObserver(vtk.vtkCommand.RightButtonDoubleClickEvent, self.left_button_double_click_event)

        self.AddObserver(vtk.vtkCommand.PanEvent, self.pan_event)
        self.AddObserver(vtk.vtkCommand.StartPanEvent, self.pan_event)
        self.AddObserver(vtk.vtkCommand.EndPanEvent, self.pan_event)
        self.AddObserver(vtk.vtkCommand.ActiveCameraEvent, self.pan_event)
        self.AddObserver(vtk.vtkCommand.EndPinchEvent, self.pan_event)

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
        左键按下
        默认模式 ：ctrl 加图钉 ， shift选段， 单击pick点
        :param obj:
        :param event:
        :return:
        """
        # print('行:', sys._getframe().f_lineno, ' ', sys._getframe().f_code.co_name)
        click_pos = self.GetInteractor().GetEventPosition()
        self._left_pressing = True
        ev = None
        self.StartPan()

        if app_manager.get_app_mode() == AppMode.DEFULT:
            if self.GetInteractor().GetControlKey():
                # 默认模式 ctrl+left ，选定图钉1
                ev = EV_SET_TAG1  # tag标签
            elif self.GetInteractor().GetShiftKey():
                # 默认模式 shift+left ，选定段
                ev = EV_SELECT_SEG  # pick 选中一段
            else:
                pass

            self.pointPicker.Pick(click_pos[0], click_pos[1], 0, self.ren)
            pick_obj = self.pointPicker.GetActor()  # 当前在pick的 actor

            if self.callback and ev:
                self.callback(ev=ev,
                              obj=pick_obj,
                              id=self.pointPicker.GetPointId(),
                              pos=self.pointPicker.GetPickPosition())

        elif app_manager.get_app_mode() == AppMode.ADD_POINT:

            wp = display_to_world(self.ren, click_pos, flg=1)
            # print("点的坐标是 ", wp)
            ev = EV_ADDING_POINT

            if self.callback:
                self.callback(ev=ev,
                              pos=(wp[0], wp[1], 0.))

        self.OnLeftButtonDown()

    def left_button_release_event(self, obj, event):
        self._left_pressing = False
        self.EndPan()
        self.OnLeftButtonUp()

    def right_button_press_event(self, obj, event):
        """
        右键按下
        默认模式 ：ctrl 加图钉
        :param obj:
        :param event:
        :return:
        """
        click_pos = self.GetInteractor().GetEventPosition()
        if app_manager.get_app_mode() == AppMode.DEFULT:
            if self.GetInteractor().GetControlKey():
                # 默认模式 ctrl+ right，选定图钉2
                ev = EV_SET_TAG2  # tag标签
            else:
                ev = EV_PICK_POINT  # pick 选中一个点

            self.pointPicker.Pick(click_pos[0], click_pos[1], 0, self.ren)
            pick_obj = self.pointPicker.GetActor()  # 当前在pick的 actor

            if self.callback:
                self.callback(ev=ev,
                              obj=pick_obj,
                              id=self.pointPicker.GetPointId(),
                              pos=self.pointPicker.GetPickPosition())

        self.OnRightButtonDown()

    def right_button_release_event(self, obj, event):
        self.OnRightButtonUp()

    def middle_button_press_event(self, obj, event):
        self._mid_pressing = True

        self.OnMiddleButtonDown()

    def middle_button_release_event(self, obj, event):
        self._mid_pressing = False

        self.OnMiddleButtonUp()

    def mouse_move_event(self, obj, event):
        ev = None
        click_pos = self.GetInteractor().GetEventPosition()

        if project_manager.on_selected:
            self.renWin.SetCurrentCursor(vtk.VTK_CURSOR_SIZEALL)  # 鼠标光标 十字
        else:
            self.renWin.SetCurrentCursor(vtk.VTK_CURSOR_DEFAULT)

        if self._left_pressing:
            for i in range(app_manager.vtk_move_sensitivity):
                self.Pan()  # 多执行一次Pan函数， 移动的灵敏度会多加一倍
            # self.Pan()

            # self.OnMouseMove()  # 已经开启了StartPan 这里仅OnMouseMove 即可

        elif self._mid_pressing:
            #  中键按下， 移动点。
            ev = EV_MOVE_SELECT
            if self.moving_pos is None:
                self.moving_pos = click_pos

            if project_manager.on_selected:
                wp2 = display_to_world(self.ren, click_pos, flg=1)
                wp1 = display_to_world(self.ren, self.moving_pos, flg=1)
                # print("wp1 =   ", wp1)
                # print("wp2 =   ", wp2)
                delta_pos = (wp2[0] - wp1[0], wp2[1] - wp1[1], 0.0)

                if self.callback and ev:
                    self.callback(ev=ev,
                                  delta=delta_pos)
            else:
                self.OnMouseMove()

        else:
            click_pos = self.GetInteractor().GetEventPosition()
            self.pointPicker.Pick(click_pos[0], click_pos[1], 0, self.ren)
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

        self.moving_pos = click_pos

    def mouse_wheel_backward_event(self, obj, event):
        # print('行:', sys._getframe().f_lineno, ' ', sys._getframe().f_code.co_name)
        # now = time.time()
        # print("时间 = ", now - self.last_time)
        # self.last_time = now
        # if project_manager.on_selected:
        #     ev = EV_ROTATE_SELECT
        #     ang = point_rot_speed["normal"]
        #     if self.GetInteractor().GetControlKey():
        #         ang = point_rot_speed["fast"]
        #     elif self.GetInteractor().GetShiftKey():
        #         ang = point_rot_speed["slow"]
        #
        #     if self.callback and ev:
        #         self.callback(ev=ev,
        #                       delta_ang=ang, )
        # else:
        #     self.OnMouseWheelBackward()
        self.OnMouseWheelBackward()

    def mouse_wheel_forward_event(self, obj, event):
        # print('行:', sys._getframe().f_lineno, ' ', sys._getframe().f_code.co_name)
        # if project_manager.on_selected:
        #     ev = EV_ROTATE_SELECT
        #     ang = -point_rot_speed["normal"]
        #     if self.GetInteractor().GetControlKey():
        #         ang = -point_rot_speed["fast"]
        #     elif self.GetInteractor().GetShiftKey():
        #         ang = -point_rot_speed["slow"]
        #
        #     if self.callback and ev:
        #         self.callback(ev=ev,
        #                       delta_ang=ang, )
        # else:
        #     self.OnMouseWheelForward()
        self.OnMouseWheelForward()

    def pan_event(self, obj, event):

        print('行:', sys._getframe().f_lineno, ' ', sys._getframe().f_code.co_name)
        print(obj)
        print(event)

    def point_pick(self, obj, event):
        pass
        # if self.callback:
        #     self.callback(ev=event,
        #                   obj=obj)

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

        if key == 'a':
            if project_manager.on_selected:
                ev = EV_ROTATE_SELECT
                ang = point_rot_speed["normal"]
                if self.callback and ev:
                    self.callback(ev=ev,
                                  delta_ang=ang, )
        elif key == 'd':
            if project_manager.on_selected:
                ev = EV_ROTATE_SELECT
                ang = point_rot_speed["normal"]
                if self.callback and ev:
                    self.callback(ev=ev,
                                  delta_ang=-ang, )

        elif key == 'Escape':
            if self.callback:
                self.callback(ev=EV_RESET_SELECT)

        # super(InteractorStyle, self).InitializeObjectBase()
        # self.OnKeyPress()

    def key_release_event(self, obj, event):
        key = self.GetInteractor().GetKeySym()

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
        if app_manager.get_app_mode() == AppMode.ADD_POINT:
            self.renWin.SetCurrentCursor(vtk.VTK_CURSOR_ARROW)

        elif app_manager.get_app_mode() in [AppMode.DEFULT, AppMode.ADD_POINT_AUTO]:
            self.renWin.SetCurrentCursor(vtk.VTK_CURSOR_DEFAULT)
