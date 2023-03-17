#!/usr/bin/env python
# -*- coding: utf-8 -*-


from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSignal

try:
    import vtkmodules.all as vtk
    from vtkmodules.util.numpy_support import vtk_to_numpy, numpy_to_vtk
    from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
except ImportError:
    import vtk
    from vtk.util.numpy_support import vtk_to_numpy, numpy_to_vtk
    from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

from trajectory.local_utils.vtk_util import *


class VtkShowView(QtWidgets.QFrame):
    BG_GRADIENT = 1  # 0 一种颜色，1 两种颜色
    BG_COLOR1 = (0.3, 0.05, 0.1)
    BG_COLOR2 = (0.2, 0.1, 0.5)

    updateSegInfo = pyqtSignal()
    showDistance = pyqtSignal(tuple)
    showHoverMsg = pyqtSignal(int)

    def __init__(self, parent=None):
        super(VtkShowView, self).__init__(parent=parent)
        self._parent = parent
        self._bg1 = self.BG_COLOR1
        self._bg2 = self.BG_COLOR2


        self.__init_ui()
        self.__init_camera()
        self.__init_axes()

        self.renderer.ResetCamera()
        self.win_render()


    def __init_ui(self):
        self.resize(600, 500)
        if self._parent:
            self.setParent(self._parent)

        '''PyQt控件'''
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.vtkWidget = QVTKRenderWindowInteractor(self)
        layout.addWidget(self.vtkWidget)

        '''VTK渲染'''
        self.window = self.vtkWidget.GetRenderWindow()  # renWin = vtk.vtkRenderWindow()
        self.interactor = self.vtkWidget.GetRenderWindow().GetInteractor()  # iren = vtk.vtkRenderWindowInteractor()
        self.renderer = vtk.vtkRenderer()
        self.renderer.SetViewport(0.0, 0.0, 1, 1)
        self.window.AddRenderer(self.renderer)

        '''背景色'''
        self.set_back_color(0, (.2, .2, .2))

        self.style = vtk.vtkInteractorStyleRubberBandPick()
        self.interactor.SetInteractorStyle(self.style)

    def __init_camera(self):
        self.vtk_camera = vtk.vtkCamera()  # 相机
        self.vtk_camera.SetPosition(0, 0, 20)
        self.vtk_camera.SetFocalPoint(0, 0, 0)
        self.vtk_camera.SetViewUp(0, 1, 0)
        self.vtk_camera.SetParallelProjection(1)
        self.renderer.ResetCamera()
        self.renderer.SetActiveCamera(self.vtk_camera)

    def __init_axes(self):
        self.axes = vtk.vtkAxesActor()
        self.axes.SetAxisLabels(0)
        self.axes.SetTotalLength(10, 10, 1)
        self.renderer.AddActor(self.axes)
        self.vtk_marker = get_axes_marker_widget(self.interactor)  # 坐标轴marker
        self.vtk_marker.SetEnabled(1)

    def win_render(self, flg=True):
        if flg:
            self.interactor.Initialize()
            self.window.Render()
            self.interactor.Start()
        else:
            self.window.Render()

    def reset(self):
        self.renderer.ResetCamera()
        self.win_render()

    def set_back_color(self, gradient=1, color1=(0, 0, 0), color2=(0, 0, 0)):
        self.BG_GRADIENT = gradient
        self._bg1 = color1
        if self.BG_GRADIENT == 1:
            self._bg2 = color2
        self._update_background()

    def _update_background(self):
        try:
            self.renderer.SetGradientBackground(self.BG_GRADIENT)
            self.renderer.SetBackground(*self._bg1)
            self.renderer.SetBackground2(*self._bg2)
            # self.renderer.Render()
            self.window.Render()
        except Exception as e:
            print(e)

    def currentCursor(self):
        cursor = QApplication.overrideCursor()
        if cursor is not None:
            cursor = cursor.shape()
        return cursor

    def overrideCursor(self, cursor):
        self._cursor = cursor
        if self.currentCursor() is None:
            QApplication.setOverrideCursor(cursor)
        else:
            QApplication.changeOverrideCursor(cursor)

    def restoreCursor(self):
        QApplication.restoreOverrideCursor()

    # def enterEvent(self, event):
    #     self.setMouseTracking(True)
    #     self.setFocus()
    #     self.overrideCursor(self._cursor)
    #     super(VTK_QWidget, self).enterEvent(event)
    #
    # def leaveEvent(self, event):
    #     self.restoreCursor()
    #     super(VTK_QWidget, self).leaveEvent(event)
    #     self.clearFocus()
    #     self.setMouseTracking(False)
    #
    # def focusOutEvent(self, ev):
    #     self.restoreCursor()

    def release(self):
        self.vtkWidget.Finalize()

    def closeEvent(self, event):
        self.release()
        super(VtkShowView, self).closeEvent(event)




if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    _view = VtkShowView()
    _view.show()
    sys.exit(app.exec_())

