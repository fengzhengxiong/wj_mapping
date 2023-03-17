#!/usr/bin/env python
# -*- coding: utf-8 -*-



import numpy as np
import sys
try:
    import vtkmodules.all as vtk
    from vtkmodules.util.numpy_support import vtk_to_numpy, numpy_to_vtk
except ImportError:
    import vtk
    from vtk.util.numpy_support import vtk_to_numpy, numpy_to_vtk




def get_axes_actor(length=(80, 80, 30), color=(0.1, 0.9, 0.1), linewidth=15.0):
    """
    创建坐标轴

    """
    axesActor = vtk.vtkAxesActor()
    axesActor.SetXAxisLabelText('x')
    axesActor.SetYAxisLabelText('y')
    axesActor.SetZAxisLabelText('z')
    axesActor.SetTotalLength(*length)
    axesActor.SetShaftTypeToLine()
    axesActor.SetNormalizedShaftLength(1.0, 1.0, 1.0)  # 设置末端箭头在轴上比例
    axesActor.SetNormalizedTipLength(0.08, 0.08, 0.08)
    # axesActor.SetShaftType(1)
    axesActor.SetCylinderRadius(6.0)
    axesActor.SetConeRadius(0.3)

    axesActor.GetXAxisCaptionActor2D().GetProperty().SetColor(*color)
    axesActor.GetYAxisCaptionActor2D().GetProperty().SetColor(*color)
    axesActor.GetZAxisCaptionActor2D().GetProperty().SetColor(*color)
    axesActor.GetXAxisCaptionActor2D().GetProperty().SetLineWidth(linewidth)
    axesActor.GetYAxisCaptionActor2D().GetProperty().SetLineWidth(linewidth)
    axesActor.GetZAxisCaptionActor2D().GetProperty().SetLineWidth(linewidth)
    bFlag = False
    if bFlag:
        colors = vtk.vtkNamedColors()
        xAxisLabel = axesActor.GetXAxisCaptionActor2D()
        xAxisLabel.GetPositionCoordinate().SetCoordinateSystemToNormalizedViewport()
        xAxisLabel.SetWidth(5.0)
        # xAxisLabel.GetPositionCoordinate().SetValue(0, 0)
        xAxisLabel.GetCaptionTextProperty().SetFontSize(6)
        xAxisLabel.GetCaptionTextProperty().SetColor(colors.GetColor3d("white"))

        yAxisLabel = axesActor.GetYAxisCaptionActor2D()
        yAxisLabel.GetPositionCoordinate().SetCoordinateSystemToNormalizedViewport()
        yAxisLabel.SetWidth(5.0)
        # yAxisLabel.GetPositionCoordinate().SetValue(0, 0)
        yAxisLabel.GetCaptionTextProperty().SetFontSize(6)
        zAxisLabel = axesActor.GetZAxisCaptionActor2D()
        zAxisLabel.GetPositionCoordinate().SetCoordinateSystemToNormalizedViewport()
        zAxisLabel.SetWidth(5.0)
        # zAxisLabel.GetPositionCoordinate().SetValue(0, 0)
        zAxisLabel.GetCaptionTextProperty().SetFontSize(6)
        del xAxisLabel, yAxisLabel, zAxisLabel, colors
        pass

    return axesActor



def get_box_widget(iren, size=3.0, color=(0.8, 0.5, 0.1), def_ret=None):
    """
    添加3D操作框控件
    # https://www.freesion.com/article/6280422237/#3_vtkBoxWidget__15
    :param iren: vtk.vtkRenderWindowInteractor()
    :param def_ret:
    :return:
    """
    try:
        # print(type(iren))
        bw = vtk.vtkBoxWidget()
        bw.SetInteractor(iren)
        bw.SetPlaceFactor(1.0)
        bw.PlaceWidget(-0.5, 0.5, -0.5, 0.5, -0.5, 0.5)
        bw.SetTranslationEnabled(1)
        bw.SetScalingEnabled(1)
        bw.SetRotationEnabled(1)
        bw.SetOutlineFaceWires(0)
        bw.SetOutlineCursorWires(1)
        bw.SetInsideOut(0)
        bw.HandlesOn()
        # bw.SetHandleSize(0.01)
        bw.GetHandleProperty().SetPointSize(size)
        bw.GetHandleProperty().SetColor(*color)
        # bw.On()

        return bw
    except Exception as e:
        print(e)
        return def_ret


def get_distance_widget(iren, def_ret=None):
    try:
        representation = vtk.vtkDistanceRepresentation3D()
        dw = vtk.vtkDistanceWidget()
        dw.SetInteractor(iren)
        dw.SetRepresentation(representation)
        # dw.CreateDefaultRepresentation()
        dw.SetPriority(0.9)
        dw.GetRepresentation().SetLabelFormat("%-#6.4f m")
        dw.ManagesCursorOn()
        dw.Off()

        return dw
    except Exception as e:
        return def_ret


def world_to_display(ren, world_point, def_ret=None, flg=1):
    """
    vtk 世界坐标转换到像素坐标 , 2个算法
    :param ren: renderer
    :param world_point: 空间坐标xyz
    :return: (x,y) 或 (x, y, z)
    """
    try:
        flg = flg
        if flg == 1:
            ren.SetWorldPoint(world_point[0], world_point[1], world_point[2], 1)
            ren.WorldToDisplay()
            result = ren.GetDisplayPoint()[:2]
            return result
        else:
            vtk_coord = vtk.vtkCoordinate()
            vtk_coord.SetCoordinateSystemToWorld()
            vtk_coord.SetValue(world_point[0], world_point[1], world_point[2])
            result = vtk_coord.GetComputedDoubleViewportValue(ren)[:2]
            return result
    except Exception as e:
        print(e)
        return def_ret



def display_to_world(ren, coord, flg=1, z=0, def_ret=None):
    """
    vtk 像素坐标转换到世界坐标 , 2个算法
    :param ren: renderer
    :param coord: 像素x y
    :return: (x,y,z)
    """
    try:
        flg = flg
        if flg == 1:
            ren.SetDisplayPoint(coord[0], coord[1], z)
            ren.DisplayToWorld()
            result = ren.GetWorldPoint()
            # print(result)
            return result[:3]
        else:
            vtk_coord = vtk.vtkCoordinate()
            vtk_coord.SetCoordinateSystemToDisplay()
            vtk_coord.SetValue(coord[0], coord[1], z)
            result = vtk_coord.GetComputedWorldValue(ren)
            # print('==== ',result)
            # vtk.vtkArcPlotter
            return result[:3]
    except Exception as e:
        print(e)
        return def_ret


def get_vtk_window_screen(window, def_ret=None):
    """
    获取vtk窗口图像
    :param window:
    :param def_ret:
    :return:
    """
    try:
        converter = vtk.vtkWindowToImageFilter()
        converter.SetInput(window)
        converter.SetInputBufferTypeToRGB()
        converter.ReadFrontBufferOff()
        converter.Update(0)
        im = vtk_to_numpy(converter.GetOutput().GetPointData().GetScalars())
        # print('getVtkWindowScreen=', window.GetSize())
        return np.flipud(im.reshape(window.GetSize()[1], window.GetSize()[0], im.shape[-1]))
    except Exception as e:
        print(e)
        return def_ret


def get_follower(text, pos, color=(1, 1, 1), def_ret=None):
    """
    获取字体 actor
    :param text:
    :param pos:
    :param color:
    :param def_ret:
    :return:
    """
    try:
        vec_text = vtk.vtkVectorText()
        vec_text.SetText(text)
        textMapper = vtk.vtkPolyDataMapper()
        textMapper.SetInputConnection(vec_text.GetOutputPort(0))
        textActor = vtk.vtkFollower()
        # textActor = vtk.vtkActor()
        textActor.SetMapper(textMapper)
        textActor.SetScale(0.6, 0.6, 0.6)
        textActor.AddPosition(*pos)
        textActor.GetProperty().SetColor(*color)
        return textActor
    except Exception as e:
        print(e)
        return def_ret


def actor_in_renderer_ornot(act, ren, def_ret=False):
    """
    actor 是否显示在renderer里
    :param act:
    :param ren:
    :param def_ret:
    :return:
    """
    try:
        actorCollection = ren.GetActors()
        num = actorCollection.GetNumberOfItems()
        actorCollection.InitTraversal()
        # print('num=', num)
        for i in range(num):
            a = actorCollection.GetNextActor()
            if act == a:
                return True

        actorCollection = ren.GetActors2D()
        num = actorCollection.GetNumberOfItems()
        actorCollection.InitTraversal()
        for i in range(num):
            a = actorCollection.GetNextProp()
            if act == a:
                return True

        del actorCollection
        del num
        return False
    except Exception as e:
        print(e)
        return def_ret


def get_axes_marker_widget(iren, def_ret=None):
    try:
        axes = vtk.vtkAxesActor()
        axesWidget = vtk.vtkOrientationMarkerWidget()
        axesWidget.SetOutlineColor(1, 1, 1)  # (0.93, 0.57, 0.13) # 外边框颜色
        axesWidget.SetOrientationMarker(axes)
        axesWidget.SetInteractor(iren)
        axesWidget.SetEnabled(1)  # EnabledOn()
        axesWidget.InteractiveOn()  # 坐标系是否可移动
        return axesWidget
    except Exception as e:
        print(e)
        return def_ret