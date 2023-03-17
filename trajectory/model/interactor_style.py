#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
VTK 交互逻辑
"""

# from PyQt5.QtCore import pyqtSignal, Qt, QObject

from trajectory.local_utils.vtk_util import *
from trajectory.manager.common_mode import AppMode
from trajectory.manager.app_manager import app_manager
from trajectory.manager.event_type import *


# vtkInteractorStyleRubberBandPick
# vtkInteractorStyleRubberBand2D
# vtkInteractorStyleRubberBand3D

class InteractorStyle(vtk.vtkInteractorStyleRubberBandPick):

    def __init__(self, ren=None, renWin=None, callback=None):
        super(InteractorStyle, self).__init__()
        self.callback = callback
        self.ren = ren
        self.renWin = renWin

        # picker
        self.pointPicker = vtk.vtkPointPicker()  # 点拾取
        self.pointPicker.AddObserver(vtk.vtkCommand.PickEvent, self.point_pick)
        self.pointPicker.SetUseCells(1)
        # print(self.pointPicker.GetTolerance())
        self.pointPicker.SetTolerance(0.015)

        self.areaPicker = vtk.vtkAreaPicker()  # 多点拾取
        # self.renWin.GetInteractor().SetPicker(self.areaPicker)
        self.areaPicker.AddObserver(vtk.vtkCommand.EndPickEvent, self.area_end_pick)

        self.AddObserver(vtk.vtkCommand.LeftButtonPressEvent, self.left_button_press_event)
        self.AddObserver(vtk.vtkCommand.LeftButtonReleaseEvent, self.left_button_release_event)
        self.AddObserver(vtk.vtkCommand.RightButtonPressEvent, self.right_button_press_event)
        self.AddObserver(vtk.vtkCommand.RightButtonReleaseEvent, self.right_button_release_event)
        self.AddObserver(vtk.vtkCommand.MouseMoveEvent, self.mouse_move_event)
        self.AddObserver(vtk.vtkCommand.LeftButtonDoubleClickEvent, self.left_button_double_click_event)
        self.AddObserver(vtk.vtkCommand.RightButtonDoubleClickEvent, self.left_button_double_click_event)

        #  键盘按键事件绑定
        self.AddObserver(vtk.vtkCommand.KeyReleaseEvent, self.key_release_event)
        self.AddObserver(vtk.vtkCommand.KeyPressEvent, self.key_press_event)
        self.AddObserver(vtk.vtkCommand.LeaveEvent, self.leave_event)
        self.AddObserver(vtk.vtkCommand.EnterEvent, self.enter_event)

        self._left_pressing = False
        # self.StartSelect()

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
        click_pos = self.GetInteractor().GetEventPosition()
        self._left_pressing = True
        ev = None
        if app_manager.get_app_mode() == AppMode.DEFULT:
            if self.GetInteractor().GetControlKey():
                # 默认模式 ctrl+left ，选定图钉1
                ev = EV_SET_TAG1  # tag标签
            elif self.GetInteractor().GetShiftKey():
                # 默认模式 shift+left ，选定段
                ev = EV_SELECT_SEG  # pick 选中一段
            else:
                # ev = EV_PICK_POINT  # pick 选中一个点
                pass

            self.pointPicker.Pick(click_pos[0], click_pos[1], 0, self.ren)
            pick_obj = self.pointPicker.GetActor()  # 当前在pick的 actor

            if self.callback and ev:
                self.callback(ev=ev,
                              obj=pick_obj,
                              id=self.pointPicker.GetPointId(),
                              pos=self.pointPicker.GetPickPosition())
            self.OnMiddleButtonDown()
            # self.OnLeftButtonDown()
        elif app_manager.get_app_mode() == AppMode.ADD_POINT:
            # print("click_pos = {}".format(click_pos))
            wp = display_to_world(self.ren, click_pos, flg=1)
            # print("点的坐标是 ", wp)
            ev = EV_ADDING_POINT

            if self.callback:
                self.callback(ev=ev,
                              pos=(wp[0], wp[1], 0.))

        elif app_manager.get_app_mode() == AppMode.AREA_PICK:
            self.OnLeftButtonDown()

        return

    def left_button_release_event(self, obj, event):
        self._left_pressing = False

        # 通过改写鼠标事件，固定相机视角，不能3D翻转
        if app_manager.get_app_mode() == AppMode.DEFULT:
            self.OnMiddleButtonUp()
            # self.OnLeftButtonUp()

        elif app_manager.get_app_mode() == AppMode.AREA_PICK:
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

    def mouse_move_event(self, obj, event):
        ev = None

        if not self._left_pressing:
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

    def left_button_double_click_event(self, obj, event):
        """
        双击左键，触发函数，  实际测试，没有作用。。。
        :param obj:
        :param event:
        :return:
        """
        print('行:', sys._getframe().f_lineno, ' ', sys._getframe().f_code.co_name)
        print("event = ", event)

        click_pos = self.GetInteractor().GetEventPosition()
        self.pointPicker.Pick(click_pos[0], click_pos[1], 0, self.ren)
        if self.callback:
            self.callback(ev='LeftButtonDoubleClickEvent',
                          id=self.pointPicker.GetPointId(),
                          pos=self.pointPicker.GetPickPosition())


    def point_pick(self, obj, event):
        if self.callback:
            self.callback(ev=event,
                          obj=obj)

    def area_end_pick(self, obj, event):
        """
        EndPickEvent
        :param obj:
        :param event:
        :return:
        """
        print('area_end_pick')
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
            if app_manager.get_app_mode() in [AppMode.ADD_POINT, AppMode.ADD_POINT_AUTO]:
                return
            elif app_manager.get_app_mode() == AppMode.DEFULT:
                app_manager.set_app_mode(AppMode.AREA_PICK)
                self.renWin.SetCurrentCursor(vtk.VTK_CURSOR_CROSSHAIR)
                # self.StartSelect()
            else:
                app_manager.set_app_mode(AppMode.DEFULT)
                self.renWin.SetCurrentCursor(vtk.VTK_CURSOR_DEFAULT)
                # self.InitializeObjectBase()
                # self.StartSelect()
                # super(InteractorStyle, self).InitializeObjectBase()
        elif key == 'Escape':
            if self.callback:
                self.callback(ev=EV_RESET_SELECT)

        # super(InteractorStyle, self).InitializeObjectBase()
        # self.OnKeyPress()


    def key_press_event2(self, obj, event):
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
            if app_manager.get_app_mode() in [AppMode.ADD_POINT, AppMode.ADD_POINT_AUTO]:
                return
            elif app_manager.get_app_mode() == AppMode.DEFULT:
                app_manager.set_app_mode(AppMode.AREA_PICK)
                self.renWin.SetCurrentCursor(vtk.VTK_CURSOR_CROSSHAIR)
                # self.StartSelect()
            else:
                app_manager.set_app_mode(AppMode.DEFULT)
                self.renWin.SetCurrentCursor(vtk.VTK_CURSOR_DEFAULT)
                # self.InitializeObjectBase()
                # self.StartSelect()
                # super(InteractorStyle, self).InitializeObjectBase()
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


