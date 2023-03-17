#!/usr/bin/env python
# -*- coding: utf-8 -*-


import numpy as np
import time

try:
    import vtkmodules.all as vtk
    from vtkmodules.util.numpy_support import vtk_to_numpy, numpy_to_vtk
except ImportError:
    import vtk
    from vtk.util.numpy_support import vtk_to_numpy, numpy_to_vtk

"""
vtk 显示点类的封装管理  
    点信息包括位置和颜色标量值，是绑定的
"""


class MyPoints(object):
    def __init__(self):
        self.pts = vtk.vtkPoints()  # 点
        self.cells = vtk.vtkCellArray()  # 顶点单元
        self.colors = vtk.vtkUnsignedCharArray()
        self.colors.SetNumberOfComponents(3)
        self.colors.SetName("colors")

        self.lines=vtk.vtkCellArray()   # json画实线
        self.lines_count=0

        self.double_lines=vtk.vtkCellArray()   # json画双实线
        self.double_lines_count = 0

        self.pointTree = vtk.vtkKdTree()  # kd 算法 查找工具类
        self.pointTree.SetTolerance(0.001)
        self.set_tree_data()

    def copy(self):
        c = MyPoints()
        c.pts.DeepCopy(self.pts)
        c.cells.DeepCopy(self.cells)
        c.colors.DeepCopy(self.colors)
        c.colors.SetNumberOfComponents(3)
        c.colors.SetName("colors")
        return c

    def set(self, instance):
        self.pts.DeepCopy(instance.pts)
        self.cells.DeepCopy(instance.cells)
        self.colors.DeepCopy(instance.colors)
        self.colors.SetNumberOfComponents(3)
        self.colors.SetName("colors")
        self.modify()

    def reset(self):
        self.pts.Initialize()
        self.pts.Reset()
        self.cells.Initialize()
        self.cells.Reset()
        self.colors.Initialize()
        self.colors.Reset()

        self.pointTree.Initialize()

    @property
    def count(self):
        return self.pts.GetNumberOfPoints()

    def set_tree_data(self):
        if self.count > 0:
            self.pointTree.BuildLocatorFromPoints(self.pts)

    def push_point(self, p, rgb):
        """ 增加点，颜色 """
        pid = self.pts.InsertNextPoint(p)
        # print('------------',pid)
        self.cells.InsertNextCell(1)
        self.cells.InsertCellPoint(pid)
        self.colors.InsertNextTuple3(rgb[0], rgb[1], rgb[2])

    def modify(self):
        """
        加该接口目的是，kdtree搜索时候，能得到最新的数据
        :return:
        """
        self.pts.Modified()
        self.cells.Modified()
        self.colors.Modified()

        self.set_tree_data()

    def set_cell_count(self, count):
        """
        设置单元数量
        :param count: 点的数量
        :return:
        """
        if count < self.cells.GetNumberOfCells():
            self.cells.Initialize()
            self.cells.Reset()
            for i in range(count):
                self.cells.InsertNextCell(1)
                self.cells.InsertCellPoint(i)
        else:
            start = self.cells.GetNumberOfCells()
            for i in range(start, count):
                self.cells.InsertNextCell(1)
                self.cells.InsertCellPoint(i)

    def set_points_from_array(self, pt_data, col_data):
        if pt_data.shape[0] != col_data.shape[0]:
            return False

        self.reset()
        for i in range(0, pt_data.shape[0]):
            p = pt_data[i]
            c = col_data[i]
            self.push_point(p, c)
        self.modify()
        return True

    def set_lines_from_array(self, pt_data, col_data, temp_length):
        if pt_data.shape[0] != col_data.shape[0]:
            return False

        self.reset()
        for i in range(0, pt_data.shape[0]):
            p = pt_data[i]
            c = col_data[i]
            self.push_point(p, c)

        count=0
        for i in range(len(temp_length)):
            temp=temp_length[i]
            for j in range(temp-1):
                rgb = col_data[i]
                line = vtk.vtkLine()
                line.GetPointIds().SetId(0, i+j+count)
                line.GetPointIds().SetId(1, i+j+count+ 1)
                self.lines.InsertNextCell(line)
                self.colors.InsertNextTuple3(rgb[0], rgb[1], rgb[2])
            count=count+temp-1
        self.lines_count=self.lines_count+1
        self.modify()
        return True

    def set_outlines_from_array(self, pt_data, col_data, temp_length, left_linetype, right_linetype, left_right_count):
        if pt_data.shape[0] != col_data.shape[0]:
            return False

        self.reset()
        for i in range(0, pt_data.shape[0]):
            p = pt_data[i]
            c = col_data[i]
            self.push_point(p, c)

        count = 0
        for i in range(len(temp_length)):
            temp = temp_length[i]
            left_point_count = left_right_count[2 * i]
            right_point_count = left_right_count[2 * i + 1]
            for j in range(temp - 1):
                if left_linetype[i] == 'SOLID' and j < left_point_count - 1:  # 左实线
                    line = vtk.vtkLine()
                    line.GetPointIds().SetId(0, i + j + count)
                    line.GetPointIds().SetId(1, i + j + count + 1)
                    self.lines.InsertNextCell(line)

                if right_linetype[i] == 'SOLID' and left_point_count <= j < temp - 1:  # 右实线
                    line = vtk.vtkLine()
                    line.GetPointIds().SetId(0, i + j + count)
                    line.GetPointIds().SetId(1, i + j + count + 1)
                    self.lines.InsertNextCell(line)

                if left_linetype[i] == 'BROKEN' and j < left_point_count - 1:  # 左虚线
                    if (i + j + count) % 2 == 0:
                        line = vtk.vtkLine()
                        line.GetPointIds().SetId(0, i + j + count)
                        line.GetPointIds().SetId(1, i + j + count + 1)
                        self.double_lines.InsertNextCell(line)

                if right_linetype[i] == 'BROKEN' and left_point_count <= j < temp - 1:  # 右虚线
                    if (i + j + count) % 2 == 0:
                        line = vtk.vtkLine()
                        line.GetPointIds().SetId(0, i + j + count)
                        line.GetPointIds().SetId(1, i + j + count + 1)
                        self.lines.InsertNextCell(line)

                if left_linetype[i] == 'DOUBLE SOLID' and j < left_point_count - 1:  # 左双实线
                    line = vtk.vtkLine()
                    line.GetPointIds().SetId(0, i + j + count)
                    line.GetPointIds().SetId(1, i + j + count + 1)
                    self.double_lines.InsertNextCell(line)

                if right_linetype[i] == 'DOUBLE SOLID' and left_point_count <= j < temp - 1:  # 右双实线
                    line = vtk.vtkLine()
                    line.GetPointIds().SetId(0, i + j + count)
                    line.GetPointIds().SetId(1, i + j + count + 1)
                    self.double_lines.InsertNextCell(line)

                if left_linetype[i] == 'DOUBLE BROKEN' and j < left_point_count - 1:  # 左双虚线
                    if (i + j + count) % 2 == 0:
                        line = vtk.vtkLine()
                        line.GetPointIds().SetId(0, i + j + count)
                        line.GetPointIds().SetId(1, i + j + count + 1)
                        self.double_lines.InsertNextCell(line)

                if right_linetype[i] == 'DOUBLE BROKEN' and left_point_count < j < temp - 1:  # 右双虚线
                    if (i + j + count) % 2 == 0:
                        line = vtk.vtkLine()
                        line.GetPointIds().SetId(0, i + j + count)
                        line.GetPointIds().SetId(1, i + j + count + 1)
                        self.lines.InsertNextCell(line)

                if left_linetype[i] == 'NULL' or right_linetype[i] == 'NULL':
                    pass
            count = count + temp - 1
        self.double_lines_count = self.double_lines_count + 1
        self.modify()
        return True


    def points_to_array(self):
        if self.count > 0:
            return vtk_to_numpy(self.pts.GetData())
        return np.array([])

    def colors_to_array(self):
        if self.colors.GetNumberOfTuples() > 0:
            return vtk_to_numpy(self.colors)
        return np.array([])

    def get_point(self, index):
        """
        获取单点
        :param index:
        :return:
        """
        if self.check_id(index):
            return (self.pts.GetPoint(index), self.colors.GetTuple3(index))
        else:
            return (None, None)

    def set_point(self, index, point, color=(255, 255, 255)):
        """
        设置单点， 位置颜色。
        :param index:
        :param point:(x y z )
        :param color:
        :return:
        """
        if 0 <= index <= self.count - 1:
            self.pts.InsertPoint(index, point)
            r, g, b = color[0], color[1], color[2]
            self.colors.InsertTuple3(index, r, g, b)

    def get_partial_point(self, ids):
        """
        获取部分点
        :param ids: id 列表
        :return: vtkPoints, 颜色数组
        """
        for index in ids:
            if not self.check_id(index):
                return None
        try:
            ret_col = vtk.vtkUnsignedCharArray()
            ret_col.SetNumberOfComponents(3)

            idlist = vtk.vtkIdList()
            for index in ids:
                idlist.InsertNextId(index)
                # idlist.InsertUniqueId(index)  # 只插入一次，不重复，较为耗时
                rgb = self.colors.GetTuple3(index)
                ret_col.InsertNextTuple3(rgb[0], rgb[1], rgb[2])
            ret_col.Modified()
            ret_p = vtk.vtkPoints()
            self.pts.GetPoints(idlist, ret_p)
            return (ret_p, ret_col)

        except Exception as e:
            print(e)
            return None

    def partial_point_to_array(self, ids):
        """
        部分点的数组
        :param ids:
        :return:
        """
        obj, _ = self.get_partial_point(ids)
        if obj is not None:
            return vtk_to_numpy(obj.GetData())
        else:
            return None

    def partial_color_to_array(self, ids):
        """
        获取部分点的颜色， 用不了类似vtkpoints方法！！！
        :param ids:
        :return:
        """
        for index in ids:
            if not self.check_id(index):
                return None
        try:
            # res2 = vtk.vtkUnsignedCharArray()
            # res2.SetNumberOfComponents(3)
            # # res2.SetName("colors")
            # self.colors.GetTuples(idlist, res2)

            result = np.zeros((len(ids), 3), dtype=int)
            for i in range(len(ids)):
                rgb = self.colors.GetTuple3(ids[i])
                result[i] = np.asarray(rgb)
            return result

        except Exception as e:
            print(e)
            return None

    def really_delete_point(self, indexs):
        """
        删除点
        :param indexs:
        :return:
        """
        # 1000000删除1000个点，耗时严重，原因是for 循环遍历list
        new_points = vtk.vtkPoints()
        new_color = vtk.vtkUnsignedCharArray()
        new_color.SetNumberOfComponents(3)

        origin = list(range(self.count))
        newlist = list(set(origin) - set(indexs))
        # newlist = [i for i in origin if i not in indexs]

        # ----------InsertPoints 方法稍快---------------
        # for i in newlist:
        #     p = self.pts.GetPoint(i)
        #     new_points.InsertNextPoint(p)
        # self.pts.ShallowCopy(new_points)

        if len(newlist) > 0:
            dstIds = vtk.vtkIdList()
            srcIds = vtk.vtkIdList()
            for i in range(len(newlist)):
                srcIds.InsertId(i, newlist[i])
                dstIds.InsertId(i, i)
            new_points.InsertPoints(dstIds, srcIds, self.pts)
            new_color.InsertTuples(dstIds, srcIds, self.colors)
            self.pts.ShallowCopy(new_points)
            self.colors.ShallowCopy(new_color)
            self.set_cell_count(self.pts.GetNumberOfPoints())
        else:
            self.pts.Initialize()
            self.colors.Initialize()
            self.cells.Initialize()
        self.modify()

    def really_insert_point(self, index, points, colors):
        """
        插入数据
        :param index: 索引，插入index和 index+1 位置
        :param points: np
        :param colors: np
        :return:
        """
        if isinstance(points, np.ndarray):
            insert_count = points.shape[0]
        else:
            insert_count = len(points)

        if insert_count < 1:
            return False

        # 尾部插入
        if self.count == 0:
            self._insert_tail(points, colors)
            return True

        if index == self.count - 1:
            self._insert_tail(points, colors)
            return True

        if index < 0:
            self._insert_head(points, colors)
            return True

        # 中间插入
        if 0 <= index < self.count - 1:
            self._insert_body(index, points, colors)
            return True

        return False

    def _insert_tail(self, points, colors):
        """插入尾部"""
        print("尾部插入")
        for i in range(0, points.shape[0]):
            self.push_point(points[i], colors[i])
        self.modify()

    def _insert_head(self, points, colors):
        """ 插入首部"""
        print("头部插入")
        tmp = vtk.vtkPoints()
        tmp.DeepCopy(self.pts)
        tmp_color = vtk.vtkUnsignedCharArray()
        tmp_color.SetNumberOfComponents(3)
        tmp_color.DeepCopy(self.colors)
        insert_count = points.shape[0]

        for i in range(0, insert_count):
            self.pts.InsertPoint(i, points[i])
            self.colors.InsertTuple3(i, colors[i][0], colors[i][1], colors[i][2])

        dstIds = vtk.vtkIdList()
        srcIds = vtk.vtkIdList()
        for i in range(tmp.GetNumberOfPoints()):
            srcIds.InsertNextId(i)
            dstIds.InsertNextId(i + insert_count)
        self.pts.InsertPoints(dstIds, srcIds, tmp)
        self.colors.InsertTuples(dstIds, srcIds, tmp_color)
        self.set_cell_count(self.pts.GetNumberOfPoints())

    def _insert_body(self, index, points, colors):
        """中间插入"""
        print("中间插入")
        insert_count = points.shape[0]

        ids = list(range(index + 1, self.count))
        # print("ids = ", ids)
        end_ps, end_col = self.get_partial_point(ids)
        # print('end_col= ', end_col)

        mid_ps = vtk.vtkPoints()
        mid_col = vtk.vtkUnsignedCharArray()
        mid_col.SetNumberOfComponents(3)
        for i in range(0, insert_count):
            mid_ps.InsertNextPoint(points[i])
            mid_col.InsertNextTuple3(colors[i][0], colors[i][1], colors[i][2])

        dstIds = vtk.vtkIdList()
        srcIds = vtk.vtkIdList()
        for i in range(insert_count):
            srcIds.InsertId(i, i)
            dstIds.InsertId(i, index + 1 + i)
        self.pts.InsertPoints(dstIds, srcIds, mid_ps)
        self.colors.InsertTuples(dstIds, srcIds, mid_col)

        dstIds.Initialize()
        srcIds.Initialize()
        for i in range(end_ps.GetNumberOfPoints()):
            srcIds.InsertId(i, i)
            dstIds.InsertId(i, index + insert_count + 1 + i)
        self.pts.InsertPoints(dstIds, srcIds, end_ps)
        self.colors.InsertTuples(dstIds, srcIds, end_col)
        self.set_cell_count(self.pts.GetNumberOfPoints())
        self.modify()
        return True

    def find_point(self, p):
        """
        寻找p点，返回id号
        :param p:
        :return:
        """

        #  BuildLocatorFromPoints  每次接近耗时1ms ，所以采用类成员方式， 每次modify 时建立tree。 这里不再更多耗时
        try:
            if self.count > 0:
                # pointTree = vtk.vtkKdTree()
                # pointTree.BuildLocatorFromPoints(self.pts)
                # pointTree.SetTolerance(0.001)
                ret = self.pointTree.FindPoint(np.asarray(p))
                return ret
            else:
                return -2
        except Exception as e:
            return -3

    def find_point2(self, p, eps=0.1):
        """
        查找点
        :param p:
        :param eps: 容差
        :return:
        """
        if self.count == 0:
            return -1

        idlist = vtk.vtkIdList()
        self.pointTree.FindPointsWithinRadius(5 * eps, np.asarray(p), idlist)
        if idlist.GetNumberOfIds() == 0:
            print("没找到 ：", np.asarray(p))

            return -1

        mindis = 5 * eps + 0.001
        result = -1

        # 寻找最近的点
        for i in range(idlist.GetNumberOfIds()):
            p1 = np.asarray(self.pts.GetPoint(idlist.GetId(i)))
            p2 = np.asarray(p)
            dis = np.linalg.norm((p2 - p1), ord=2)
            if mindis > dis:
                mindis = dis
                result = idlist.GetId(i)
        return result

    def find_closed_N_point(self, n, p):
        """
        查找距离p最近的n个点
        :param n:
        :param p:
        :return: id列表
        """
        try:
            if self.count > 0:
                idl = vtk.vtkIdList()
                self.pointTree.FindClosestNPoints(n, p, idl)
                # print('find_closed_N_point   ',1000*(t2-t1))
                result = [idl.GetId(i) for i in range(idl.GetNumberOfIds())]
                return result
            else:
                return []
        except Exception as e:
            return None

    def check_id(self, index):
        return 0 <= index < self.count
