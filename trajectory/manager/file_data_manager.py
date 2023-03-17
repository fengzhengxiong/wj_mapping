#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
原始数据管理、解析工具
"""
import numpy as np

from trajectory.config.file_type import *
import copy


class ArrayDataManager():
    def __init__(self):
        self._a = 0

    @staticmethod
    def get_color_array(data):
        """
        read txt版
        数据数组，获取rgb np数组
        :param data:
        :return:
        """
        _data = np.copy(data)
        rgb = np.zeros((_data.shape[0], 3), dtype=int)
        color_dic = copy.deepcopy(tra_property_dic)
        for i in range(_data.shape[0]):
            attr_val = int(_data[i][ID_PROPERTY])
            color = color_dic.get(attr_val, {}).get("rgb", (255, 255, 0))
            rgb[i] = np.array(color)
        return np.asarray(rgb)

    @staticmethod
    def get_points_dim3_array(data):
        """
        read txt版
        获取数据，z补充为0
        :param data: 数据前两列是 x y
        :return:
        """
        _data = np.copy(data[:, :2])
        z = np.zeros((_data.shape[0],), dtype=_data.dtype).reshape(_data.shape[0], -1)
        points = np.hstack((_data, z))  # 组成 n * 3 点位数组
        return np.asarray(points)

    def get_points_dim3_array_json(data,color_index):
        """
        read json版
        获取数据，z补充为0
        :param data: 数据前两列是 x y
        :param color_index:
        :return:
        """
        new_data=[]
        new_rgb=[]
        for i in range(len(data)):
            temp=data[i]
            for j in range(len(temp)):
                dp=[]
                dp.append(temp[j][0])
                dp.append(temp[j][1])
                dp.append(0)
                new_data.append(dp)
                rgb=json_color_dic.get(color_index, {}).get("rgb", (255, 255, 0))
                new_rgb.append(rgb)
        return np.array(new_data),np.array(new_rgb)



