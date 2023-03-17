#!/usr/bin/env python
# -*- coding: utf-8 -*-


import math
import time
import numpy as np

CONSTANTS_RADIUS_OF_EARTH = 6371004.0

#  墨卡托 投影计算的公式有点问题，暂时用球型计算方法， 换算。


# 地球长半轴
R_a = 6378137.00
# 地球短半轴
R_b = 6356752.3142

def GPStoXY(lat, lon, ref_lat, ref_lon):
    # input GPS and Reference GPS in degrees
    # output XY in meters (m) X:North Y:East
    lat_rad = math.radians(lat)
    lon_rad = math.radians(lon)
    ref_lat_rad = math.radians(ref_lat)
    ref_lon_rad = math.radians(ref_lon)

    sin_lat = math.sin(lat_rad)
    cos_lat = math.cos(lat_rad)
    ref_sin_lat = math.sin(ref_lat_rad)
    ref_cos_lat = math.cos(ref_lat_rad)

    cos_d_lon = math.cos(lon_rad - ref_lon_rad)

    arg = np.clip(ref_sin_lat * sin_lat + ref_cos_lat * cos_lat * cos_d_lon, -1.0, 1.0)
    c = math.acos(arg)

    k = 1.0
    if abs(c) > 0:
        k = (c / math.sin(c))

    x = float(k * (ref_cos_lat * sin_lat - ref_sin_lat * cos_lat * cos_d_lon) * CONSTANTS_RADIUS_OF_EARTH)
    y = float(k * cos_lat * math.sin(lon_rad - ref_lon_rad) * CONSTANTS_RADIUS_OF_EARTH)

    return x, y


def XYtoGPS(x, y, ref_lat, ref_lon):
    x_rad = float(x) / CONSTANTS_RADIUS_OF_EARTH
    y_rad = float(y) / CONSTANTS_RADIUS_OF_EARTH
    c = math.sqrt(x_rad * x_rad + y_rad * y_rad)

    ref_lat_rad = math.radians(ref_lat)
    ref_lon_rad = math.radians(ref_lon)

    ref_sin_lat = math.sin(ref_lat_rad)
    ref_cos_lat = math.cos(ref_lat_rad)

    if abs(c) > 0:
        sin_c = math.sin(c)
        cos_c = math.cos(c)

        lat_rad = math.asin(cos_c * ref_sin_lat + (x_rad * sin_c * ref_cos_lat) / c)
        lon_rad = (ref_lon_rad + math.atan2(y_rad * sin_c, c * ref_cos_lat * cos_c - x_rad * ref_sin_lat * sin_c))

        lat = math.degrees(lat_rad)
        lon = math.degrees(lon_rad)

    else:
        lat = math.degrees(ref_lat_rad)
        lon = math.degrees(ref_lon_rad)

    return lat, lon



def main():
    original_long = 120.0
    original_lat = 45.0
    move_x = -100.0
    move_y = 100.0

    move_x = -0.0
    move_y = 0.0

    rotaionangle = 0.0

    lat,lon = XYtoGPS(move_x, move_y,original_lat, original_long)
    print("计算的经纬度是 {},{} ".format(lon,lat))

    x, y = GPStoXY(lat,lon,original_lat,original_long)
    print("计算的xy = {},{}".format(x, y))

    # x, y = GPStoXY(40.0476420, 116.2903803, 40.04, 116.3)
    # print("计算的xy = {},{}".format(x, y))


def cal_trans(x, y, z):
    R_x = np.array([[1.0, 0.0, 0.0], [0.0, math.cos(x), -1 * math.sin(x)], [0.0, math.sin(x), math.cos(x)]])
    R_y = np.array([[math.cos(y), 0.0, math.sin(y)], [0.0, 1.0, 0.0], [-1 * math.sin(y), 0.0, math.cos(y)]])
    R_z = np.array([[math.cos(z), -1 * math.sin(z), 0.0], [math.sin(z), math.cos(z), 0.0], [0.0, 0.0, 1.0]])
    rotate = np.dot(R_z, R_y)
    rotate = np.dot(rotate, R_x)

    return rotate


def lonlat_to_xyz(lon, lat, ref_lon, ref_lat, angle_north):
    x = (lon - ref_lon) * math.pi / 180 * R_a * math.cos(ref_lat * math.pi / 180)
    y = (lat - ref_lat) * math.pi / 180 * R_b
    xyz = np.array([[x, y, 0]])  # 旋转
    R_bmp = cal_trans(0, 0, angle_north * np.pi / 180)
    A = np.dot(R_bmp, xyz[:, :3].T)
    xyz[:, :3] = A.T
    x = xyz[0][0]
    y = xyz[0][1]
    print('axiong:::----------------------------- ')
    print('axiong:::xyz ', xyz)
    print('axiong:::R_bmp ', R_bmp)
    print('axiong:::A ', A)
    print('axiong::: ',x,y)
    return x, y


def lonlat_to_xyz_batch(lonlat_arr, ref_lon, ref_lat, angle_north):
    """

    :param lonlat_arr:  经纬度 二维np数组
    :param ref_lon:
    :param ref_lat:
    :param angle_north:
    :return:
    """
    xyz = np.zeros((lonlat_arr.shape[0], 3), dtype=float)
    rot_mat = cal_trans(0, 0, angle_north * math.pi /180)

    K1 = math.pi / 180 * R_a * math.cos(ref_lat * math.pi / 180)
    K2 = math.pi / 180 * R_b

    for i in range(lonlat_arr.shape[0]):
        lon = lonlat_arr[i][0]
        lat = lonlat_arr[i][1]
        xyz[i][0] = (lon - ref_lon) * K1
        xyz[i][1] = (lat - ref_lat) * K2

    A = np.dot(rot_mat, xyz[:, :3].T)

    xyz[:, :3] = A.T
    result = xyz[:, :2]
    return result


def xyz_to_lonlat(x, y, ref_lon, ref_lat, angle_north):
    R_bmp = cal_trans(0, 0, -angle_north * np.pi / 180)
    xyz = np.array([[x, y, 0]])  # 旋转
    A = np.dot(R_bmp, xyz[:, :3].T)
    xyz[:, :3] = A.T
    x_ = xyz[0][0]
    y_ = xyz[0][1]

    lon_ = x_ / ((math.pi / 180 * R_a) * (math.cos(ref_lat * math.pi / 180))) + ref_lon
    lat_ = y_ / (math.pi / 180 * R_b) + ref_lat

    return lon_, lat_


def xyz_to_lonlat_batch(xy_arr, ref_lon, ref_lat, angle_north):
    """

    :param xy_arr: x y  二维np数组
    :param ref_lon:
    :param ref_lat:
    :param angle_north:
    :return:
    """
    rot_mat = cal_trans(0, 0, -angle_north * np.pi / 180)
    ling = np.zeros((xy_arr.shape[0],), dtype=float).reshape(xy_arr.shape[0], -1)
    xyz = np.hstack((xy_arr, ling))
    A = np.dot(rot_mat, xyz[:, :3].T)
    xyz[:, :3] = A.T

    result = np.zeros((xy_arr.shape[0], 2), dtype=float)
    K1 = math.pi / 180 * R_a * math.cos(ref_lat * math.pi / 180)
    K2 = math.pi / 180 * R_b

    for i in range(xy_arr.shape[0]):
        x_ = xyz[i][0]
        y_ = xyz[i][1]
        result[i][0] = x_ / K1 + ref_lon
        result[i][1] = y_ / K2 + ref_lat
    return result

import time
def main2():
    filename = r'D:\py_project\collisionpath\intersection_1_1.txt'
    oriArray = np.loadtxt(filename, delimiter=',', dtype=float)
    refLonLat = [oriArray[0][0], oriArray[0][1]]

    print(refLonLat)
    t1 = time.time()
    # xy_array = lonlat_to_xyz_batch(oriArray[:, :2], refLonLat[0], refLonLat[1], 0)
    t2 = time.time()
    # print(xy_array[:10, :])

    print('------------------------------------------')
    t3 = time.time()
    xy_array = np.zeros((oriArray.shape[0], 2), dtype=float)
    for i in range(oriArray.shape[0]):
        x, y = lonlat_to_xyz(oriArray[i][0], oriArray[i][1], refLonLat[0], refLonLat[1], 0)
        xy_array[i] = np.array([x, y], dtype=float)
    t4 = time.time()
    # print(xy_array[:10, :])

    print("时间 {}，  {}".format(1000*(t2-t1), 1000*(t4-t3)))

if __name__ == '__main__':
    main2()


