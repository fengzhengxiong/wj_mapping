#!/usr/bin/env python
# -*- coding: utf-8 -*-
import copy
import copyreg

from trajectory.data.mypointactor import MyPointActor
from trajectory.config.common_variable import point_actor_size
from trajectory.data.mysegment import MySegment
from trajectory.manager.area_pick_manager import area_pick_manager, AreaPickMode
from trajectory.manager.file_data_manager import ArrayDataManager
from trajectory.manager.action_manager import ActionData
from trajectory.manager.common_mode import *
from trajectory.local_utils.myqueue import MyQueue
from trajectory.local_utils.math_util import *
from trajectory.local_utils.pub import *
import time
import sys
import numpy as np

try:
    import vtkmodules.all as vtk
    from vtkmodules.util.numpy_support import vtk_to_numpy, numpy_to_vtk
    from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
except ImportError:
    import vtk
    from vtk.util.numpy_support import vtk_to_numpy, numpy_to_vtk
    from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor


class VtkShowModel(object):
    def __init__(self, ren=None, window=None):
        super(VtkShowModel, self).__init__()

        # actor的修改需要渲染器配合使用
        self.ren = ren
        self.window = window

        # 核心数据------------
        self._dic_actor = {}  # key: filename, value: MyPointActor
        self.dic_visible = {}  # 显示与否 key : file ,value: True False

        self._select_actor = MyPointActor()
        self._select_actor.set_point_size(point_actor_size.get("selected", 10))
        self._hover_actor = MyPointActor()  # 悬浮点
        self._hover_actor.set_point_size(point_actor_size.get("hover", 10))

        self._new_actor = MyPointActor()  # 新增点临时存储对象
        self._new_actor.set_point_size(point_actor_size.get("new", 10))
        self._seg_actor = MySegment()  # 段存储

        # 标志位
        self.enable_actor = None  # 允许被选中的对象, 指针  ==MyPointActor
        self.new_backup = MyQueue(20)  # 用于新增点步骤的记录



    @property
    def ren_enable(self):
        return (self.ren is not None and self.window is not None)

    def reset(self):
        if not self.ren_enable:
            return

        self.enable_actor = None
        acts = list(self._dic_actor.values())
        acts = acts + [self._select_actor, self._new_actor, self._hover_actor]
        for a in acts:
            a.remove_by_render(self.ren)
            a.reset()
        self._dic_actor.clear()
        self.dic_visible.clear()

    def remove_file(self, file):
        act = self._dic_actor.get(file, None)
        if act is not None:
            act.remove_by_render(self.ren)
            act.reset()
            self._dic_actor.pop(file)

        if file in self.dic_visible:
            del self.dic_visible[file]

    def update_show_actor(self):
        """
        刷新隐藏和显示
        :return:
        """
        if not bool(self._dic_actor):
            return

        result = []
        for file, act in self._dic_actor.items():
            val = self.dic_visible.get(file, True)
            if val:
                act.add_by_render(self.ren)
                result.append(act.actor)
            else:
                act.remove_by_render(self.ren)

        self.window.Render()
        return result

    def load_point(self, filename, point, rgb):
        """
        初始化，加载文件，
        :param filename:
        :param point:
        :param rgb:
        :return:
        """
        if not self.ren_enable:
            print('load_point ren_enable=False')
            return False

        cur_actor = self._dic_actor.get(filename, None)
        if cur_actor is None:
            cur_actor = MyPointActor()
            self._dic_actor[filename] = cur_actor
        else:
            cur_actor.remove_by_render(self.ren)

        ret = cur_actor.pts.set_points_from_array(point, rgb)
        if not ret:
            print("点数与颜色数不符")
            return False

        cur_actor.make_actor()
        cur_actor.add_by_render(self.ren)
        self.ren.ResetCamera()  # 刷新视角，所有点可见
        self.window.Render()


    def load_line(self, filename, point, rgb, temp_length):
        """
        初始化，加载文件，
        :param filename:
        :param point:
        :param rgb:
        :param temp_length:
        :return:
        """
        if not self.ren_enable:
            print('load_point ren_enable=False')
            return False

        cur_actor = self._dic_actor.get(filename, None)
        if cur_actor is None:
            cur_actor = MyPointActor()
            self._dic_actor[filename] = cur_actor
        else:
            cur_actor.remove_by_render(self.ren)
        ret = cur_actor.pts.set_lines_from_array(point, rgb ,temp_length)
        if not ret:
            print("点数与颜色数不符")
            return False
        cur_actor.make_actor()
        cur_actor.add_by_render(self.ren)
        self.ren.ResetCamera()  # 刷新视角，所有点可见
        self.window.Render()

    def load_outline(self, filename, point, rgb, temp_length,left_linetype, right_linetype, left_right_count):
        if not self.ren_enable:
            print('load_point ren_enable=False')
            return False

        cur_actor = self._dic_actor.get(filename, None)
        if cur_actor is None:
            cur_actor = MyPointActor()
            self._dic_actor[filename] = cur_actor
        else:
            cur_actor.remove_by_render(self.ren)
        ret = cur_actor.pts.set_outlines_from_array(point, rgb , temp_length, left_linetype, right_linetype, left_right_count)
        if not ret:
            print("点数与颜色数不符")
            return False
        cur_actor.make_actor()
        cur_actor.add_by_render(self.ren)
        self.ren.ResetCamera()  # 刷新视角，所有点可见
        self.window.Render()


    def set_enable_actor(self, file):
        self.enable_actor = self._dic_actor.get(file, self.enable_actor)

    def get_actor_list(self):
        """
        获取所有演员，用于pointpicker  拾取
        :return:
        """
        return [myactor.actor for myactor in list(self._dic_actor.values())]

    def hover_single_point(self, point_act, point_id):
        """
        悬浮
        :param point_act:  my point actor
        :param point_id: id
        :return:
        """
        if not self.ren_enable:
            print("ren_enable error")
            return

        self._hover_actor.remove_by_render(self.ren)
        if point_act is not None and point_id >= 0:
            xyz, rgb = point_act.pts.get_point(point_id)
            self._hover_actor.pts.reset()
            self._hover_actor.pts.push_point(xyz, rgb)
            self._hover_actor.make_actor()
            self._hover_actor.add_by_render(self.ren)

        self.window.Render()

    def hover_batch_points(self, point_act, start, end):
        """
        悬浮一段 点  ， 左闭右开
        :param point_act:
        :param start: 起点id
        :param end: 终点id
        :return:
        """
        if not self.ren_enable:
            print("ren_enable error")
            return
        try:
            self._hover_actor.remove_by_render(self.ren)
            self._hover_actor.pts.reset()
            if point_act is not None:
                # --------------------耗时1 在1ms内，耗时2 在1~4ms左右--------------------
                t1 = time.time()
                if 0 <= start < end <= point_act.pts.count:
                    for point_id in range(start, end):
                        xyz, rgb = point_act.pts.get_point(point_id)
                        self._hover_actor.pts.push_point(xyz, rgb)
                    # print("hover_batch_points 耗时1 = {}".format(1000*(time.time() - t1)))
                    # ----------------------------------------
                    # self._hover_actor.pts.reset()
                    # ids = list(range(start, end))
                    # t1 = time.time()
                    # arr_p = point_act.pts.partial_point_to_array(ids)
                    # arr_col = point_act.pts.partial_color_to_array(ids)
                    # self._hover_actor.pts.set_points_from_array(arr_p, arr_col)
                    # print("hover_batch_points 耗时2 = {}".format(1000 * (time.time() - t1)))

                    self._hover_actor.make_actor()
                    self._hover_actor.add_by_render(self.ren)

            self.window.Render()
        except Exception as e:
            print(e)



    def select_single_point(self, pa, point_id):
        """
        单击选中点，如果已经是选中状态的，再选择，改变状态
        :param pa:  my point actor
        :param point_id: 点id号
        :return:
        """
        if not self.ren_enable:
            print("ren_enable error")
            return

        if point_id < 0:
            return
        if self.enable_actor != pa:
            # 如果不是当前可选的使能actor，结束
            return

        xyz, rgb = pa.pts.get_point(point_id)
        # print("xyz = ", point_id, xyz, rgb)
        self._select_actor.remove_by_render(self.ren)
        idx = self._select_actor.pts.find_point(xyz)  # 是否存在于选中点中
        # print(self.select_actor.pts.points_to_array())
        # print("选中id号 = ", idx)
        if idx >= 0:
            self._select_actor.pts.really_delete_point([idx])
        else:
            self._select_actor.pts.push_point(xyz, rgb)
            self._select_actor.pts.modify()

        # print("新的  select_actor=", self.select_actor.pts.points_to_array())
        self._select_actor.build_polydata()
        self._select_actor.build_actor()
        self._select_actor.add_by_render(self.ren)

        self.window.Render()

    def select_region_points(self, area_picker):
        """
        区域选取点
        :param area_picker:
        :return:
        """
        if self.enable_actor is None:
            # 选中的需要使能
            return
        if self.enable_actor not in [act for file, act in self._dic_actor.items() if self.dic_visible.get(file, True)]:
            return

        try:
            frustum = area_picker.GetFrustum()  # vtk.vtkPlanes()
            geo = vtk.vtkExtractPolyDataGeometry()
            geo.SetInputData(self.enable_actor.polydata)
            geo.SetImplicitFunction(frustum)
            geo.Update(0)

            select_polydata = geo.GetOutput()
            num = select_polydata.GetNumberOfPoints()
            print('pick num=', num)

            # TODO 寻求方法：select_polydata 里点cell id号， 能省去find查找id，更高效

            select_array = vtk_to_numpy(select_polydata.GetPoints().GetData())  # 选中点的np数据

            # print("select_array = ", select_array)
            if num > 0:
                self._select_actor.remove_by_render(self.ren)
                t1 = time.time()
                if area_pick_manager.get_pick_mode() == AreaPickMode.DEFULT:
                    self._actor_select_points(select_array)
                    # self._actor_select_points2(select_array)
                elif area_pick_manager.get_pick_mode() == AreaPickMode.ADD_PICK:
                    self._actor_add_points(select_array)
                elif area_pick_manager.get_pick_mode() == AreaPickMode.SUB_PICK:
                    self._actor_remove_points(select_array)
                elif area_pick_manager.get_pick_mode() == AreaPickMode.INVERSE_PICK:
                    self._actor_inverse_points(select_array)
                t2 = time.time()

                print("区域选中耗时={}".format(1000*(t2-t1)))
                self._select_actor.add_by_render(self.ren)
                self.window.Render()

        except Exception as e:
            print(e)

    def _actor_select_points(self, data):
        """
        选中区域点
        :param data:
        :return:
        """
        tmplist = []  # 记录之前选中，而本次没有选中的点的 id
        print('self.select_actor.pts.count=', self._select_actor.pts.count)
        if self._select_actor.pts.count > 0:
            tmplist = list(range(self._select_actor.pts.count))
            pass

        add_ids = []
        for i in range(data.shape[0]):
            xyz = data[i]
            s_idx = self._select_actor.pts.find_point(xyz)

            if s_idx >= 0:
                # 这个点已经是选中状态
                tmplist.remove(s_idx)
                continue

            idx = self.enable_actor.pts.find_point(xyz)
            add_ids = add_ids + [idx] if idx >= 0 else add_ids

        # 单独用add_ids 循环添加点，不再上述循环内完成是为了 find_point 的逻辑， 依赖 modify函数对tree的刷新
        for idx in add_ids:
            p, rgb = self.enable_actor.pts.get_point(idx)  # 通过索引拿到rgb
            self._select_actor.pts.push_point(p, rgb)
        self._select_actor.pts.modify()

        if tmplist:
            self._select_actor.pts.really_delete_point(tmplist)
        self._select_actor.make_actor()

    def _actor_select_points2(self, data):
        """
        选中区域点2   与_actor_select_points  功能相同，清除再添加，2 理论上应该没有1 效率高
        :param data:
        :return:
        """

        self._select_actor.reset()
        for i in range(data.shape[0]):
            xyz = data[i]
            idx = self.enable_actor.pts.find_point(xyz)
            _, rgb = self.enable_actor.pts.get_point(idx)  # 通过索引拿到rgb
            self._select_actor.pts.push_point(xyz, rgb)

        self._select_actor.make_actor()

    def _actor_add_points(self, data):
        """
        添加data点
        :param data:
        :return:
        """

        add_ids = []  # 需要被添加点 id列表
        for i in range(data.shape[0]):
            xyz = data[i]
            s_idx = self._select_actor.pts.find_point(xyz)
            if s_idx >= 0:
                # 这个点已经是选中状态
                continue
            idx = self.enable_actor.pts.find_point(xyz)
            add_ids = add_ids + [idx] if idx >= 0 else add_ids

        for idx in add_ids:
            p, rgb = self.enable_actor.pts.get_point(idx)  # 通过索引拿到rgb
            self._select_actor.pts.push_point(p, rgb)

        self._select_actor.make_actor()

    def _actor_remove_points(self, data):
        """ select_actor 删除 data点 """
        rm_ids = []
        for i in range(data.shape[0]):
            xyz = data[i]
            s_idx = self._select_actor.pts.find_point(xyz)
            if s_idx >= 0:
                # 这个点已经是选中状态
                rm_ids.append(s_idx)
        if rm_ids:
            self._select_actor.pts.really_delete_point(rm_ids)
            self._select_actor.build_polydata()
            self._select_actor.build_actor()

    def _actor_inverse_points(self, data):
        """
        选中的点，取反。
        :param data:
        :return:
        """

        rm_ids = []
        add_ids = []
        for i in range(data.shape[0]):
            s_idx = self._select_actor.pts.find_point(data[i])
            if s_idx >= 0:
                rm_ids.append(s_idx)
                continue

            idx = self.enable_actor.pts.find_point(data[i])
            add_ids = add_ids + [idx] if idx >= 0 else add_ids

        for idx in add_ids:
            p, rgb = self.enable_actor.pts.get_point(idx)  # 通过索引拿到rgb
            self._select_actor.pts.push_point(p, rgb)

        self._select_actor.pts.modify()

        if rm_ids:
            # print('0000000000000000-------------  ', len(rm_ids))
            # print(self._select_actor.pts.count)
            self._select_actor.pts.really_delete_point(rm_ids)
        # print( '11111        -----   ',self.select_actor.pts.count)
        self._select_actor.make_actor()

    def delete_selected_points(self):
        """删除选中的点"""
        if not self.ren_enable:
            return

        rm_ids = self.get_selected_list()

        self._select_actor.remove_by_render(self.ren)
        self._select_actor.reset()
        if self.enable_actor:
            self.enable_actor.remove_by_render(self.ren)
            if rm_ids:

                self.enable_actor.pts.really_delete_point(rm_ids)
                self.enable_actor.build_polydata()
                self.enable_actor.build_actor()

            self.enable_actor.add_by_render(self.ren)
            self.window.Render()

    def edit_selected_position(self, point_array):
        """
        编辑选中点的位置
        _select_actor  存储的点位的顺序和 selected_list 的id是不同的！！， 需要重新修改 p 和 rgb
        :param point_array:  np数组 批量点 xyz
        :return:
        """

        selected_list = self.get_selected_list()
        if len(selected_list) != point_array.shape[0]:
            # print('行:', sys._getframe().f_lineno, ' ', sys._getframe().f_code.co_name)
            # pps = self.enable_actor.pts.partial_point_to_array(project_manager.selected_list)
            # print("pps = ", pps)
            # sele = self._select_actor.pts.points_to_array()
            # print("sele = ", sele)
            return

        self._select_actor.remove_by_render(self.ren)
        self.enable_actor.remove_by_render(self.ren)
        for i in range(self._select_actor.pts.count):
            x, y, z = point_array[i][0], point_array[i][1], point_array[i][2]
            p, color = self.enable_actor.pts.get_point(selected_list[i])  # 先获取当前点位 信息
            self.enable_actor.pts.pts.InsertPoint(selected_list[i], (x, y, z))
            self._select_actor.pts.set_point(i, point=(x, y, z), color=color)

        self._select_actor.make_actor()  # 必须加这句，否则内部点位得不到更新。
        self.enable_actor.make_actor()
        self._select_actor.add_by_render(self.ren)
        self.enable_actor.add_by_render(self.ren)

    def edit_selected_property(self, **kwargs):
        """
        编辑选中点的属性
        目前编辑类别里，仅有属性编辑后要修改颜色， 其他暂无
        :param kwargs:
        :return:
        """

        rgb = kwargs.get("color", (255, 255, 255))
        selected_list = self.get_selected_list()

        if len(selected_list) == 0:
            return
        is_edited = False
        # 寻找点， 更新点的颜色
        for i in range(self._select_actor.pts.count):
            p, color = self._select_actor.pts.get_point(i)
            idx = self.enable_actor.pts.find_point(p)
            if idx >= 0:
                is_edited = True
                self._select_actor.pts.set_point(i, p, rgb)
                self.enable_actor.pts.set_point(idx, p, rgb)
        self.enable_actor.pts.modify()
        self._select_actor.pts.modify()
        self.window.Render()


    def get_selected_list(self):
        """
        获取选中点的索引号列表
        :return:
        """
        res = []
        count = self._select_actor.pts.count
        if count < 1:
            return res

        for i in range(count):
            p, col = self._select_actor.pts.get_point(i)
            idx = self.enable_actor.pts.find_point(p)
            if idx >= 0:
                res.append(idx)

        result = np.sort(np.array(res), axis=-1)  # 排序
        result = result.tolist()
        return result

    def get_index_by_pose(self, xyz, def_ret=None):
        """根据位置获取点id"""
        idx = def_ret
        if self.enable_actor:
            idx = self.enable_actor.pts.find_point(xyz)

        return idx

    def new_point_by_click(self, pos, rgb):
        """
        新增点
        :param pos: 位置
        :param rgb: 颜色
        :return:
        """
        print('new_point_by_click:', pos)

        self._new_actor.remove_by_render(self.ren)
        self._new_actor.pts.push_point(pos, rgb)
        self._new_actor.make_actor()
        self._new_actor.add_by_render(self.ren)
        self.window.Render()  # 刷新一下
        self.new_backup_store()


    def end_add_points(self, st=-2, merge=True):
        """
        结束插入点操作
        :param merge: 是否合并 新增数据到主数据
        :return:
        """
        import sys
        print('end_add_points---merge= ',merge)
        print('行:', sys._getframe().f_lineno, ' ', sys._getframe().f_code.co_name, ' ', \
              sys._getframe().f_back.f_code.co_name, ' ', sys._getframe().f_back.f_back.f_code.co_name)

        ret = True
        self._new_actor.remove_by_render(self.ren)
        if merge and self._new_actor.pts.count > 0:
            points, colors = self.get_new_point_data()
            # 更新显示
            self.enable_actor.remove_by_render(self.ren)

            ret = self.enable_actor.pts.really_insert_point(st, points, colors)

            if not ret:
                print("end_add_points  , 插入点失败")
            self.enable_actor.add_by_render(self.ren)
        self._new_actor.reset()
        self.new_backup_clear()

        return ret

    def reset_new_actor(self):
        """
        重置，清空新增点演员显示
        :return:
        """
        if not self.ren_enable:
            return
        self._new_actor.remove_by_render(self.ren)
        self._new_actor.reset()
        self.window.Render()

    def select_point_in_segment(self, p1, p2):
        """
        按照一个区间选中
        :param p1:
        :param p2:
        :return:
        """
        if not self.ren_enable:
            print('select_point_in_segment error')
            return

        ids = [p1, p2]
        p1 = min(ids)
        p2 = max(ids)
        self._select_actor.remove_by_render(self.ren)

        # 先查看选中的点，不处于该区间内，则删除之。
        add_ids = list(range(p1, p2 + 1))
        rm_ids = []  # select 点的索引

        for i in range(self._select_actor.pts.count):
            xyz, rgb = self._select_actor.pts.get_point(i)
            idx = self.enable_actor.pts.find_point(xyz)

            if p1 <= idx <= p2:
                add_ids.remove(idx)
            else:
                # 不处于区间内，删除
                rm_ids.append(i)

        # 删除多余选中点
        if rm_ids:
            self._select_actor.pts.really_delete_point(rm_ids)
        # 填充[p1,p2]未选中点
        for i in add_ids:
            xyz, rgb = self.enable_actor.pts.get_point(i)
            if xyz:
                self._select_actor.pts.push_point(xyz, rgb)
            else:
                print('select_points_by_tag --i= {}'.format(i))

        self._select_actor.make_actor()
        self._select_actor.add_by_render(self.ren)

    def clear_selected(self):
        if not self.ren_enable:
            return
        self._select_actor.remove_by_render(self.ren)
        self._select_actor.reset()
        self.window.Render()

    def find_actor(self, actor):
        """
        查找actor
        :param actor:
        :return:  返回文件名称， mypointactor
        """
        for key, val in self._dic_actor.items():
            if val.actor == actor:
                return (key, val)

        return None

    def check_file(self, file):
        return file in self._dic_actor

    def get_xyz_and_rgb(self, file, point_id):
        this_data = self._dic_actor.get(file, None)
        if this_data is None:
            return None, None
        xyz, rgb = this_data.pts.get_point(point_id)
        return xyz, rgb

    def get_current_point_count(self):
        """获取当前对象点数"""
        return self.enable_actor.pts.count if self.enable_actor else None

    def get_new_point_data(self):
        """
        获取新增点数据
        :return:
        """

        points = np.copy(self._new_actor.pts.points_to_array())
        colors = np.copy(self._new_actor.pts.colors_to_array())

        return points, colors

    def get_new_point_count(self):
        """
        获取新增点个数
        :return:
        """
        return self._new_actor.pts.count

    def set_points_to_new_actor(self, points, rgbs):
        """
        添加到new_actor
        :param points:
        :param rgbs:
        :return:
        """
        self._new_actor.remove_by_render(self.ren)
        self._new_actor.reset()
        if self._new_actor.pts.set_points_from_array(points, rgbs):
            # print('-set_points_to_new_actor --======')
            self._new_actor.make_actor()
            self._new_actor.add_by_render(self.ren)

    def new_backup_store(self):
        """新增点操作 缓存"""
        self.new_backup.put(self._new_actor.pts.copy())

    def new_backup_restore(self, undo=True):
        """新增点动作，回退 """
        if not self.new_backup_restorable_(undo):
            return False
        pts = self.new_backup.getLast() if undo else self.new_backup.getNext()
        self._new_actor.remove_by_render(self.ren)
        self._new_actor.pts.set(pts)
        self._new_actor.make_actor()
        self._new_actor.add_by_render(self.ren)
        self.window.Render()
        return True

    def new_backup_restorable_(self, undo=True):
        """  新增点动作，是否可以回退"""
        return self.new_backup.isGetLast() if undo else self.new_backup.isGetNext()

    def new_backup_clear(self):
        self.new_backup.reset()

    def restore_data(self, action_obj, undo):
        """
        返回上一步 回调函数
        :param action_obj:
        :param undo:
        :return:
        """
        if not isinstance(action_obj, ActionData):
            return False
        print('行:', sys._getframe().f_lineno, ' ', sys._getframe().f_code.co_name)

        # print(action_obj.action)
        # print(action_obj.data[:, :3])
        # print(action_obj.ids)
        # print(action_obj.get_other_data())

        try:
            this_file = action_obj.get_other_data().get('file', None)
            if not this_file:
                print('data model restore_data error ')
                return False

            # 原则上正在操作的撤回文件，与当前enable 是一致的！！
            if self.enable_actor != self._dic_actor.get(this_file, -1):
                print("enable actor 不是撤回文件的actor")
                return False

            self.clear_selected()  # 清除选中
            self.enable_actor.remove_by_render(self.ren)

            if action_obj.action == ActionMode.ADD:
                self._restore_add(this_file, action_obj.data, action_obj.ids, undo)
                pass
            elif action_obj.action == ActionMode.SUB:
                self._restore_sub(this_file, action_obj.data, action_obj.ids, undo)
                pass
            elif action_obj.action == ActionMode.EDIT:
                self._restore_edit(this_file, action_obj.data, action_obj.ids, undo)
                pass

            self.enable_actor.add_by_render(self.ren)
            self.window.Render()

        except Exception as e:
            print('行:', sys._getframe().f_lineno, ' ', sys._getframe().f_code.co_name)
            print(e)


    def _restore_add(self, file, data, ids, undo):
        """
        撤回添加
        :param file: 文件key
        :param data: 增量数据np
        :param ids:  [idx] 插入位置
        :param undo: 反向、正向
        :return:
        """
        if not isinstance(self.enable_actor, MyPointActor):
            return

        print('行:', sys._getframe().f_lineno, ' ', sys._getframe().f_code.co_name)
        if undo:
            idx = ids[0]
            rm_ids = list(range(idx, idx + data.shape[0]))
            self.enable_actor.pts.really_delete_point(rm_ids)
        else:
            # redo
            idx = ids[0]
            rgb = ArrayDataManager.get_color_array(data)
            points = ArrayDataManager.get_points_dim3_array(data)
            self.enable_actor.pts.really_insert_point(idx - 1, points, rgb)  # 接口是插入id , id+1 位置
        self.enable_actor.make_actor()


    def _restore_sub(self, file, data, ids, undo):
        """
        撤回添加
        :param file: 文件key
        :param data: 增量数据np
        :param ids:  删除列表
        :param undo: 反向、正向
        :return:
        """
        if not isinstance(self.enable_actor, MyPointActor):
            return
        print('行:', sys._getframe().f_lineno, ' ', sys._getframe().f_code.co_name)

        if undo:
            # 将ids数列按连续 拆分为n段， data 拆分为n个子数组， 分别插入原数据
            # ids = [5,6,7,9,10] ———— [[5,6,7],[9,10]]
            ids_seg = split_list_in_segs(ids)
            print('行:', sys._getframe().f_lineno, ' ', sys._getframe().f_code.co_name)
            # print("ids_seg =", ids_seg)
            # print("len ids = {}, data.shape={}".format(len(ids), data.shape[0]))
            t1 = time.time()
            _data = np.copy(data)
            for seg in ids_seg:
                idx = seg[0]
                row_cnt = len(seg)
                _seg_data = _data[:row_cnt, :]

                points = ArrayDataManager.get_points_dim3_array(_seg_data)
                rgb = ArrayDataManager.get_color_array(_seg_data)
                self.enable_actor.pts.really_insert_point(idx - 1, points, rgb)
                _data = _data[row_cnt:, :]
            t2 = time.time()
            print("_restore_sub vtk 耗时 = {}".format(1000*(t2-t1)))
        else:
            # redo
            self.enable_actor.pts.really_delete_point(ids)
        self.enable_actor.make_actor()

    def _restore_edit(self, file, data, ids, undo):
        """
        撤回编辑, 对于actor显示， 目前只有用到 点 和 颜色
        :param file:
        :param data: 修改的数据，为list = [old new]
        :param ids:
        :param undo:
        :return:
        """
        if not isinstance(self.enable_actor, MyPointActor):
            return
        print('行:', sys._getframe().f_lineno, ' ', sys._getframe().f_code.co_name)
        if np.array_equal(data[0][:, :3], data[1][:, :3]):
            # 如果点位和颜色没有变更，这里不需要继续更新了。
            return
        print('行:', sys._getframe().f_lineno, ' ', sys._getframe().f_code.co_name)

        _data = np.copy(data[0]) if undo else np.copy(data[1])  # 新数据 旧数据
        points = ArrayDataManager.get_points_dim3_array(_data)
        rgb = ArrayDataManager.get_color_array(_data)

        for i in range(len(ids)):
            self.enable_actor.pts.set_point(ids[i], points[i], rgb[i])
        self.enable_actor.make_actor()



