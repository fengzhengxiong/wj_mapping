#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    import vtkmodules.all as vtk
except ImportError:
    import vtk
import numpy as np
import time

"""
区间选择 ，起始点两钉pin
"""

class PointPin(object):
    SCALE = 5.0
    COLOR = (1, 0, 0)
    OPACITY = 0.2

    def __init__(self):
        self._pin_id = None  # 图钉的id，若为None ，表示非使能状态

        self._scale = self.SCALE
        self._color = self.COLOR
        self._opacity = self.OPACITY

        self.pos = (0, 0, 0)

        colors = vtk.vtkNamedColors()
        self.silhouette = vtk.vtkPolyDataSilhouette()
        self.silhouetteMapper = vtk.vtkPolyDataMapper()
        self.silhouetteActor = vtk.vtkActor()

        self.silhouetteMapper.SetInputConnection(self.silhouette.GetOutputPort())
        self.silhouetteActor.SetMapper(self.silhouetteMapper)
        # self.silhouetteActor.GetProperty().SetColor(colors.GetColor3d("Tomato"))
        self.silhouetteActor.GetProperty().SetColor(1, 1, 1)
        self.silhouetteActor.GetProperty().SetLineWidth(3)

        # 球
        self.build_actor()


    def reset(self):
        self.mapper.InitializeObjectBase()
        self.pin_actor.InitializeObjectBase()

    def build_actor(self):
        source = vtk.vtkSphereSource()
        source.SetPhiResolution(21)
        source.SetThetaResolution(21)
        source.Update(0)
        self.mapper = vtk.vtkPolyDataMapper()
        self.mapper.SetInputConnection(source.GetOutputPort(0))
        self.pin_actor = vtk.vtkActor()
        self.pin_actor.SetMapper(self.mapper)

        self.pin_actor.GetProperty().SetEdgeColor(1., 1., 1.)
        # self.pin_actor.GetProperty().SetEdgeVisibility(1)
        self.pin_actor.GetProperty().SetLineWidth(1.0)
        self.pin_actor.GetProperty().SetSpecular(.5)
        self.pin_actor.GetProperty().SetSpecularColor(0.8, 0.8, 1)
        self.pin_actor.GetProperty().SetSpecularPower(30.0)
        self.pin_actor.GetProperty().SetDiffuseColor(0.6, 0.7, 0.4)
        self.pin_actor.GetProperty().SetDiffuse(.8)

        self.set_property(self._color)

    def set_silhouette_color(self, color):
        self.silhouetteActor.GetProperty().SetColor(color)

    def set_id(self, val):
        self._pin_id = val

    @property
    def get_id(self):
        return self._pin_id

    def set_position(self, pos):
        self.pos = pos

    def get_position(self):
        return self.pos

    def set_scale(self, scale):
        self._scale = scale

    def get_scale(self):
        return self._scale

    def set_property(self, color=(1, 1, 1)):
        self._color = color

        self.pin_actor.SetPosition(self.pos)
        self.pin_actor.SetScale(self._scale)
        self.pin_actor.GetProperty().SetColor(self._color)
        self.pin_actor.GetProperty().SetOpacity(self._opacity)
        self.pin_actor.Modified()

    def add_by_render(self, render):
        render.AddActor(self.pin_actor)

        self.silhouette.SetCamera(render.GetActiveCamera())
        self.silhouette.SetInputData(self.pin_actor.GetMapper().GetInput())
        self.silhouetteMapper.SetInputConnection(self.silhouette.GetOutputPort(0))
        self.silhouetteActor.SetMapper(self.silhouetteMapper)
        self.silhouetteActor.SetPosition(self.pos)
        self.silhouetteActor.SetScale(self._scale)
        self.silhouetteActor.Modified()
        render.AddActor(self.silhouetteActor)


    def remove_by_render(self, render):
        render.RemoveActor(self.pin_actor)
        render.RemoveActor(self.silhouetteActor)


