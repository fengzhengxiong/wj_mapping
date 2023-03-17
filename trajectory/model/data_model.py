#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
核心txt数据，管理。
"""
import sys
import time
import numpy as np
import os
import os.path as osp
from trajectory.local_utils.gps_xy import lonlat_to_xyz_batch, xyz_to_lonlat_batch, xyz_to_lonlat
from trajectory.config.file_type import ID_PROPERTY, save_dir, file_fmt
from trajectory.manager.action_manager import ActionData, ActionMode, action_manager
from trajectory.local_utils.pub import *
import json


class DataModel(object):
    def __init__(self, color_map=dict()):
        super(DataModel, self).__init__()

        self._dic_data = {}  # key 文件名， value np.array 二维， 这里前两列是已经转化的xy
        self.ref_lon_lat = None  # 原点经纬度

        self.json_result=[]  # 加载出来的data转换成xy坐标
        self.json_line=False  # 判断是否要画线（outline除外）
        self.json_line_temp_length=[]  #如果要画线，肯定要分段，这个就是每一段的点的长度

        self.left_linetype = []  # 加载outline时候的左边界线里边的每段的线的类型
        self.right_linetype = []  # 加载outline时候的右边界线里边的每段的线的类型
        self.left_right_count = []  # 加载outline时候的左右边界线里边的每段的线的类型的点的个数

    def reset(self):
        self._dic_data.clear()
        self.ref_lon_lat = None

    def load_file(self, filename, force=False):
        """

        :param filename:
        :param force: 是否强制重新加载txt 数据
        :return:
        """
        try:
            if not force and filename in self._dic_data:
                # 如果已经有数据了， 不重复加载
                return True

            # filename = r'C:\Users\wanji\Desktop\yuanqu1'
            cur_data = np.loadtxt(filename, delimiter=',', dtype=float)
            # cur_data = cur_data[:10, :]
            print("file 数据size=  ", cur_data.shape)

            if self.ref_lon_lat is None:
                self.ref_lon_lat = np.array((cur_data[0][0], cur_data[0][1]))

            xy_data = self.trans_data(cur_data, True)  # 转xy
            self._dic_data[filename] = xy_data

            return True
        except Exception as e:
            print('加载文件失败 {}'.format(e))
            return False

    def save_file(self, file, start):
        """
        保存
        :param file: 当前文件名称，非被保存文件名称
        :param start:
        :return:
        """
        if not self.is_file_in_dic(file):
            print("save_file  not exist={}".format(file))
            return False

        tardir = osp.join(osp.dirname(file), save_dir)
        rel_file = osp.basename(file)
        if start is not None and osp.isdir(start):
            if "../" not in osp.relpath(file, start):
                rel_file = osp.relpath(file, start)
                tardir = osp.join(start, save_dir)

        tarfile = osp.join(tardir, rel_file)

        if not osp.exists(osp.dirname(tarfile)):
            os.makedirs(osp.dirname(tarfile))

        # print('tarfile=', tarfile)

        try:
            this_data = self._dic_data[file]
            lane_arr = self.trans_data(this_data, False)
            np.savetxt(tarfile, lane_arr, fmt=file_fmt, delimiter=',')

        except Exception as e:
            print(e)

    def get_data(self, file):
        return self._dic_data.get(file, None)

    def get_single_point_info(self, file, point_id, def_ret=None):
        """
        获取单点信息
        :param file:
        :param point_id:
        :return: 返回经纬度 + 完整信息
        """
        if not self.is_file_in_dic(file):
            # print("get_single_point_info  not exist={}".format(file))
            return def_ret

        try:
            this_data = self._dic_data[file]
            x, y = this_data[point_id][0], this_data[point_id][1]
            lon, lat = xyz_to_lonlat(x, y, self.ref_lon_lat[0], self.ref_lon_lat[1], 0)
            return ([lon, lat], this_data[point_id])

        except Exception as e:
            print(e)
            return def_ret

    def find_section_by_id(self, file, point_id, def_ret=False):
        """

        :param file:
        :param point_id:
        :param def_ret:
        :return: 返回区间是 左闭右开
        """
        if not self.is_file_in_dic(file):
            print("find_section_by_id  not exist={}".format(file))
            return def_ret

        try:
            this_data = self._dic_data[file]

            if not (0 <= point_id <= this_data.shape[0]):
                return def_ret

            maxid = this_data.shape[0] - 1
            idx1 = point_id
            idx2 = point_id
            attr = this_data[point_id][ID_PROPERTY]

            while True:
                if this_data[idx1][ID_PROPERTY] != attr:
                    idx1 += 1
                    break
                if idx1 == 0:
                    break

                idx1 -= 1

            while True:
                if this_data[idx2][ID_PROPERTY] != attr:
                    idx2 -= 1
                    break
                if idx2 == maxid:
                    break
                idx2 += 1


            return (idx1, idx2 + 1)

        except Exception as e:
            print(e)
            return def_ret


    def trans_data(self, data_arr, toXYZ=True):
        if toXYZ:
            xy_array = lonlat_to_xyz_batch(data_arr[:, :2], self.ref_lon_lat[0], self.ref_lon_lat[1], 0)
            result = np.hstack((xy_array, data_arr[:, 2:]))
            return result
        else:
            xy_array = xyz_to_lonlat_batch(data_arr[:, :2], self.ref_lon_lat[0], self.ref_lon_lat[1], 0)
            result = np.hstack((xy_array, data_arr[:, 2:]))
            return result

    def delete_data(self, file, ids):
        """
        删除点
        :param file: 文件
        :param ids: ids索引
        :return:
        """

        if not self.is_file_in_dic(file):
            print("delete_data  not exist={}".format(file))
            return False
        try:
            this_data = self._dic_data[file]
            # print('delete_data  1111   ', this_data.shape)
            this_data = np.delete(this_data, ids, axis=0)

            # print('delete_data  22222    ', this_data.shape)
            self._dic_data[file] = this_data

        except Exception as e:
            print(e)

    def insert_data(self, file, start_id, data):
        """
        插入数据
        :param file:
        :param start_id: 起点
        :param data: 数据内容
        :return:
        """
        if not self.is_file_in_dic(file):
            print("insert_data  not exist={}".format(file))
            return False
        try:
            this_data = self._dic_data[file]

            if this_data.shape[1] != data.shape[1]:
                return False

            this_data = np.insert(this_data, start_id, data, axis=0)
            self._dic_data[file] = this_data

        except Exception as e:
            print(e)

    def edit_element(self, file, ids, col, val):
        """
        批量编辑数据某个元素
        :param file:
        :param ids: 行号 列表
        :param col: 第几列
        :param val: 值
        :return:
        """
        if not self.is_file_in_dic(file):
            print("edit_element  not exist={}".format(file))
            return False
        try:
            this_data = self._dic_data[file]

            for idx in ids:
                this_data[idx][col] = val

            self._dic_data[file] = this_data

        except Exception as e:
            print(e)

    def change_data(self,file,row,col,data):
        """
        用于修改数据后的数据处理
        :param file: 要修改的文件
        :param row: 要修改的文件行 []
        :param col: 要修改的文件列 []
        :param data: 数据
        :return:
        """
        if not self.is_file_in_dic(file):
            print("edit_data  not exist={}".format(file))
            return False
        if len(row) !=len(data) or len(row)!=len(col) :
            print("edit_data  不一致 =".format(file))
            return False
        try:
            this_data = self._dic_data[file]
            for i in range(len(row)):
                this_data[row[i]][col[i]] = data[i]
            self._dic_data[file] = this_data
        except Exception as e:
            print(e)

    def edit_data(self, file, ids, data):
        """
        编辑数据，按照行, 可用于redo还原
        :param file:
        :param ids: 行号列表
        :param data: 二维数组，维度必须和ids一致
        :return:
        """
        if not self.is_file_in_dic(file):
            print("edit_data  not exist={}".format(file))
            return False
        if len(ids) != data.shape[0]:
            print("edit_data  不一致 =".format(file))
            return False

        try:
            this_data = self._dic_data[file]

            for i in range(len(ids)):
                this_data[ids[i]] = data[i]

            self._dic_data[file] = this_data

        except Exception as e:
            print(e)

    def remove_file(self, file):
        if self.is_file_in_dic(file):
            del self._dic_data[file]

    def is_file_in_dic(self, file):
        return file in self._dic_data.keys()

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
            this_data = self._dic_data.get(this_file, None)
            if this_data is None:
                return False

            if action_obj.action == ActionMode.ADD:
                self._restore_add(this_file, action_obj.data, action_obj.ids, undo)
                pass
            elif action_obj.action == ActionMode.SUB:
                self._restore_sub(this_file, action_obj.data, action_obj.ids, undo)
                pass
            elif action_obj.action == ActionMode.EDIT:
                self._restore_edit(this_file, action_obj.data, action_obj.ids, undo)
                pass

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
        print('_restore_add --------')
        this_data = self._dic_data.get(file, None)
        if undo:
            idx = ids[0]
            rm_ids = list(range(idx, idx + data.shape[0]))
            this_data = np.delete(this_data, rm_ids, axis=0)
            self._dic_data[file] = this_data
        else:
            # redo
            idx = ids[0]
            this_data = np.insert(this_data, idx, data, axis=0)
            self._dic_data[file] = this_data

    def _restore_sub(self, file, data, ids, undo):
        """

        :param file:
        :param data:
        :param ids: 被删除的有序 index
        :param undo:
        :return:
        """
        # print('_restore_sub --------')
        this_data = self._dic_data.get(file, None)
        # test_data = np.copy(this_data)

        if undo:
            # 将ids数列按连续 拆分为n段， data 拆分为n个子数组， 分别插入原数据
            # ids = [5,6,7,9,10] ———— [[5,6,7],[9,10]]
            ids_seg = split_list_in_segs(ids)
            # print('行:', sys._getframe().f_lineno, ' ', sys._getframe().f_code.co_name)
            # print("ids_seg =", ids_seg)
            # print("len ids = {}, data.shape={}".format(len(ids), data.shape[0]))
            t1 = time.time()
            _data = np.copy(data)
            for seg in ids_seg:
                idx = seg[0]
                row_cnt = len(seg)
                _seg_data = _data[:row_cnt, :]
                this_data = np.insert(this_data, idx, _seg_data, axis=0)
                _data = _data[row_cnt:, :]
            t2 = time.time()
            # print("_restore_sub耗时 = {}".format(1000*(t2-t1)))

            self._dic_data[file] = this_data

            # ---------------循环插入对比耗时-----结果相差很大-----------
            # _data = np.copy(data)
            # t1 = time.time()
            # for i in range(len(ids)):
            #     test_data = np.insert(test_data, ids[i], _data[i], axis=0)
            # t2 = time.time()
            # print("_restore_sub  222 耗时 = {}".format(1000 * (t2 - t1)))
            # ret = np.array_equal(this_data, test_data)
            # print("相等 ？ = ", ret)

        else:
            # redo
            this_data = np.delete(this_data, ids, axis=0)
            self._dic_data[file] = this_data

    def _restore_edit(self, file, data, ids, undo):
        """
        撤回编辑
        :param file:
        :param data: 修改的数据，为list = [old new]
        :param ids:
        :param undo:
        :return:
        """
        print('_restore_sub --------')
        this_data = self._dic_data.get(file, None)

        _data = np.copy(data[0]) if undo else np.copy(data[1])  # 新数据 旧数据

        for i in range(len(ids)):
            this_data[ids[i]] = _data[i]
        self._dic_data[file] = this_data


    def load_json_file(self,filename,color_index):
        """
        加载高精度地图json文件
        filename：打开的文件路径
        """

        self.json_result.clear()
        self.json_line_temp_length.clear()
        self.left_linetype.clear()
        self.right_linetype.clear()
        self.left_right_count.clear()

        with open(filename, 'r', encoding='utf-8') as f:
            try:
                while True:
                    line_data = f.readline()
                    if line_data:
                        data=json.loads(line_data)
                    else:
                        break
            except Exception as e:
                print(e)
                f.close()

        features = data['features']

        if color_index==1:
            for i in range(len(features)):
                features_data = features[i]
                features_data_properties = features_data['properties']
                leftBoundaryLine = features_data_properties['leftBoundaryLine']
                rightBoundaryLine = features_data_properties['rightBoundaryLine']
                leftBoundaryLine_keys = leftBoundaryLine.keys()
                rightBoundaryLine_keys = rightBoundaryLine.keys()
                leftBoundaryLine_data = leftBoundaryLine['geometry']
                rightBoundaryLine_data = rightBoundaryLine['geometry']

                if 'lineType' in leftBoundaryLine_keys:
                    leftBoundaryLine_type = leftBoundaryLine['lineType']
                    self.left_linetype.append(leftBoundaryLine_type)
                else:
                    self.left_linetype.append('NULL')

                if 'lineType' in rightBoundaryLine_keys:
                    rightBoundaryLine_type = rightBoundaryLine['lineType']
                    self.right_linetype.append(rightBoundaryLine_type)
                else:
                    self.right_linetype.append('NULL')

                self.left_right_count.append(len(leftBoundaryLine_data))
                self.left_right_count.append(len(rightBoundaryLine_data))

                lng_lat = []
                for i in range(len(leftBoundaryLine_data)):
                    leftBoundaryLine_data_i = leftBoundaryLine_data[i]
                    left_lat = leftBoundaryLine_data_i['lat']
                    left_lng = leftBoundaryLine_data_i['lng']
                    left = []
                    left.append(left_lng)
                    left.append(left_lat)
                    lng_lat.append(left)

                for i in range(len(rightBoundaryLine_data)):
                    rightBoundaryLine_data_i = rightBoundaryLine_data[i]
                    right_lat = rightBoundaryLine_data_i['lat']
                    right_lng = rightBoundaryLine_data_i['lng']
                    right = []
                    right.append(right_lng)
                    right.append(right_lat)
                    lng_lat.append(right)

                temp = self.trans_data(np.array(lng_lat), True)
                self.json_result.append(temp)
                self.json_line_temp_length.append(len(temp))
            return self.json_result,self.json_line_temp_length, self.left_linetype, self.right_linetype, self.left_right_count

        else:
            for i in range(len(features)):
                features_data = features[i]
                features_data_geometry = features_data['geometry']
                features_data_geometry_coordinates = features_data_geometry['coordinates']
                if len(features_data_geometry_coordinates) == 1:
                    features_data_geometry_coordinates = np.array(features_data_geometry_coordinates[0])
                    self.json_line = False
                else:
                    features_data_geometry_coordinates = np.array(features_data_geometry_coordinates)
                    self.json_line = True
                features_data_geometry_coordinates = features_data_geometry_coordinates[:, 0:2]
                temp = self.trans_data(features_data_geometry_coordinates, True)
                self.json_result.append(temp)
                self.json_line_temp_length.append(len(temp))
            return self.json_result, self.json_line, self.json_line_temp_length





