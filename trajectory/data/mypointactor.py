#!/usr/bin/env python
# -*- coding: utf-8 -*-


import numpy as np
import time
from trajectory.data.mypoints import MyPoints
try:
    import vtkmodules.all as vtk
except ImportError:
    import vtk



class MyPointActor(object):

    SIZE = 3

    def __init__(self):
        self.pts = MyPoints()
        self.polydata = vtk.vtkPolyData()
        self.mapper = vtk.vtkPolyDataMapper()
        self.actor = vtk.vtkActor()

        self.double_polydata = vtk.vtkPolyData()
        self.double_mapper = vtk.vtkPolyDataMapper()
        self.double_actor = vtk.vtkActor()

        self.data = None  # 其他属性数据

    def data_copy(self):
        if self.data is not None:
            return np.copy(self.data)
        return None

    def reset(self):
        self.pts.reset()
        self.polydata.Initialize()
        self.mapper.InitializeObjectBase()
        self.actor.InitializeObjectBase()

    def build_polydata(self):
        self.polydata.Initialize()
        self.polydata.Reset()
        # self.polydata = vtk.vtkPolyData()
        self.polydata.SetPoints(self.pts.pts)

        if self.pts.lines_count == 0:
            self.polydata.SetVerts(self.pts.cells)

        if self.pts.lines_count!=0 :
            self.polydata.SetLines(self.pts.lines)

        if self.pts.double_lines != 0:
            self.polydata.SetLines(self.pts.lines)
            self.double_polydata.SetPoints(self.pts.pts)
            self.double_polydata.SetLines(self.pts.double_lines)

        self.polydata.GetPointData().SetScalars(self.pts.colors)
        self.polydata.Modified()

    def build_actor(self):
        # 下面的初始化加与否暂时没有影响，暂时先加上，预防未知问题
        # self.mapper.InitializeObjectBase()
        # self.actor.InitializeObjectBase()
        self.mapper.SetInputData(self.polydata)
        self.mapper.SetScalarVisibility(1)
        self.actor.SetMapper(self.mapper)
        self._update_point_size()

        if self.pts.double_lines != 0:
            self.double_mapper.SetInputData(self.double_polydata)
            self.double_mapper.SetScalarVisibility(1)
            self.double_actor.SetMapper(self.double_mapper)
            self._update_line_width()

    def set_point_size(self, point_size=5):
        self.SIZE = point_size

    def get_point_size(self):
        return self.SIZE

    def _update_point_size(self):
        self.actor.GetProperty().SetPointSize(self.SIZE)

    def _update_line_width(self):
        self.actor.GetProperty().SetLineWidth(self.SIZE)
        self.double_actor.GetProperty().SetLineWidth(self.SIZE * 2)

    def add_by_render(self, render):
        render.AddActor(self.actor)
        if self.pts.double_lines != 0:
            render.AddActor(self.double_actor)


    def remove_by_render(self, render):
        render.RemoveActor(self.actor)

    def make_actor(self):
        """
        pts点位确定，直接生成actor
        :return:
        """
        self.pts.modify()
        self.build_polydata()
        self.build_actor()


