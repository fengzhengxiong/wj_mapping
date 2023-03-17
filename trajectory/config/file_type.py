#!/usr/bin/env python
# -*- coding: utf-8 -*-


from collections import OrderedDict
"""
地图文件信息 ，说明

"""




tra_property_dic = {
    1:  {"des": "普通道路", "rgb": (10, 240, 10)},
    2:  {"des": "路口", "rgb": (255, 255, 10)},
    3:  {"des": "环岛", "rgb": (65, 105, 200)},
    4:  {"des": "匝道", "rgb": (10, 250, 230)},
    5:  {"des": "水平泊车", "rgb": (127, 250, 200)},
    6:  {"des": "垂直泊车", "rgb": (160, 32, 230)},
    7:  {"des": "隧道", "rgb": (244, 164, 98)},
    8:  {"des": "路口中转", "rgb": (255, 0, 10)},
    9:  {"des": "路口后段", "rgb": (255, 97, 3)},
    10: {"des": "预留", "rgb": (112, 128, 100)},
}

json_color_dic = {
    1:  {"des": "outline", "rgb": (255, 255, 255)},
    2:  {"des": "centerline", "rgb": (255, 0, 255)},
    3:  {"des": "stopline", "rgb": (0, 0, 255)},
    4:  {"des": "corssworkline", "rgb": (0, 255, 0)},
}

tra_lane_dic = {
    1:  {"des": "单行道"},
    2:  {"des": "双车道右侧"},
    3:  {"des": "三车道"},
    4:  {"des": "双车道左侧"},
    5:  {"des": "借道"},
}

merge_dic = {
    1:  {"des": "默认"},
    2:  {"des": "切换SLAM"},
    3:  {"des": "左并道"},
    4:  {"des": "右并道"},
    5:  {"des": "结束并道"},
}

road_state_dic = {
    1:  {"des": "正常道路"},
    2:  {"des": "颠簸道路"},
    3:  {"des": "闸机口"},
}

turn_light_dic = {
    0:  {"des": "无需打灯"},
    1:  {"des": "左转灯"},
    2:  {"des": "右转灯"},
    3:  {"des": "双闪"},
}


# txt 文件属性
import numpy as np

map_txt_dic = {
    # key 名称    val: 中文名称      列数      描述   值(供参考选择)
    "lon":          {"ch": "经度", "No": 0, "describe": "", "val": None},
    "lat":          {"ch": "纬度", "No": 1, "describe": "", "val": None},
    "property":     {"ch": "地图属性", "No": 2, "describe": "", "val": tra_property_dic},
    "speed":        {"ch": "设定速度", "No": 3, "describe": "", "val": None},
    "laneState":    {"ch": "车道状态", "No": 4, "describe": "", "val": tra_lane_dic},
    "merge":        {"ch": "并道属性", "No": 5, "describe": "", "val": merge_dic},
    "road":         {"ch": "道路状态", "No": 6, "describe": "", "val": road_state_dic},
    "turnLight":    {"ch": "转向灯状态", "No": 7, "describe": "", "val": turn_light_dic},
    "rightOffset":    {"ch": "右侧临时停车偏移距离", "No": 8, "describe": "", "val": None},
    "thisWidth":    {"ch": "自车道宽度", "No": 9, "describe": "", "val": None},
    "leftWidth":    {"ch": "左车道宽度", "No": 10, "describe": "", "val": None},
    "rightWidth":    {"ch": "右车道宽度", "No": 11, "describe": "", "val": None},
    "leftSafeDis":    {"ch": "轨迹左侧安全距离", "No": 12, "describe": "", "val": None},
    "rightSafeDis":    {"ch": "轨迹右侧安全距离", "No": 13, "describe": "", "val": None},
    "yaw":          {"ch": "航向角", "No": 14, "describe": "", "val": float()},
    "gpsTime":      {"ch": "GPS时间", "No": 15, "describe": "", "val": int()},
    "satelliteCnt":    {"ch": "卫星个数", "No": 16, "describe": "", "val": np.array([1., 32.3])},

    "laneswitch":    {"ch": "换道标志位", "No": 17, "describe": "", "val": None},
    "sidepass":    {"ch": "借道标志位", "No": 18, "describe": "", "val": None},
    "lanenum":    {"ch": "车道总数", "No": 19, "describe": "", "val": None},
    "lanesite":    {"ch": "所在第几车道数", "No": 20, "describe": "", "val": None},
}

map_key_list = [
    "lon",
    "lat",
    "property",
    "speed",
    "laneState",
    "merge",
    "road",
    "turnLight",
    "rightOffset",
    "thisWidth",
    "leftWidth",
    "rightWidth",
    "leftSafeDis",
    "rightSafeDis",
    "yaw",
    "gpsTime",
    "satelliteCnt",

    "laneswitch",
    "sidepass",
    "lanenum",
    "lanesite",
]


save_dir = "traj_dir"  # 子文件夹

file_suffix = ['.txt']  #
jsonfile_suffix = ['.json']  #
# 格式
file_fmt = ['%4.8f', '%4.8f', '%d', '%d', '%d', '%d', '%d', '%d', '%.2f', '%.2f', '%.2f', '%.2f', '%.2f',
            '%.2f',
            '%.3f', '%d', '%d',
            '%d','%d','%d','%d']

# 对应txt 列
ID_PROPERTY = 2  # 地图属性
ID_SPEED = 3  # 设定速度
ID_LANESTATE = 4  # 车道状态
ID_MERGE = 5  # 并道属性
ID_TURNLIGHT = 7  # 转向灯状态


# def main():
#     pass
#     print(map_txt_dic["satelliteCnt"]["val"])
#     print(isinstance(map_txt_dic["satelliteCnt"]["val"], np.ndarray))
#
#     a = map_txt_dic["satelliteCnt"]["val"]
#     print(type(a))
#
#     # if isinstance(a, tuple):
#     #     for d in a:
#     #         print(type(d))
#
#
# if __name__ == '__main__':
#     main()