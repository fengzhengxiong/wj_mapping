#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math
import numpy as np


def cal_between_two_point(p1, p2, step):
    """
    :param p1:
    :param p2:
    :param step: 间距
    :return:
    """
    dis = np.linalg.norm(np.array(p2) - np.array(p1))
    if dis < step:
        return np.array([])

    dim = np.array(p1).shape[0]
    seg_cnt = int(round(dis / step, 0))
    real_step = dis / seg_cnt
    unit_vec = (np.array(p2) - np.array(p1)) / dis  # 单位向量
    result = np.zeros((seg_cnt-1, dim))

    for i in range(seg_cnt - 1):
        result[i] = np.array(p1) + unit_vec * (i+1) * real_step

    return result


def cal_between_two_point_(p1, p2, step, def_ret=None):
    """

    :param p1:
    :param p2:
    :param step: 间距
    :return:
    """
    dis = np.linalg.norm(np.array(p1) - np.array(p2))

    if dis < step:
        return def_ret
    try:
        seg_cnt = int(round(dis/step, 0))
        x_list = get_list_between_two_number(p1[0], p2[0], seg_cnt)
        y_list = get_list_between_two_number(p1[1], p2[1], seg_cnt)

        if np.array(p1).shape[0] == 3:
            z_list = get_list_between_two_number(p1[2], p2[2], seg_cnt)
        else:
            z_list = np.zeros_like(x_list)


        # print('cal_between_two_point  ', x_list.shape, '  ', y_list.shape)

        point = np.vstack((x_list, y_list, z_list)).T

        return point

    except Exception as e:
        print(e)
        return def_ret


def get_list_between_two_number(x1, x2, seg):
    """

    :param x1:
    :param x2:
    :param seg: 段数
    :return:
    """
    step = (x2 - x1) / seg  # 间距
    x_list = np.arange(x1, x2, step)

    return x_list[1:]


def dim2_to_dim3(data):
    """
    二维np数组 [x, y] 变为 [x, y, 0.0]
    :param data:
    :return:
    """
    try:
        z = np.zeros((data.shape[0],), dtype=data.dtype).reshape(data.shape[0], -1)
        pts = np.hstack((data[:, :2], z))  # 组成 n * 3 点位数组

        return np.asarray(pts)

    except Exception as e:
        print(e)
        return np.copy(data)



def rot_points_dim2(center, points, angle):

    rot_sin = np.sin(np.deg2rad(angle))
    rot_cos = np.cos(np.deg2rad(angle))
    # rot_mat = np.array(
    #     [
    #         [rot_cos, -rot_sin, 0],
    #         [rot_sin, rot_cos, 0],
    #         [0., 0., 1.]
    #     ], dtype=float
    # )
    rot_mat = np.array(
        [
            [rot_cos, -rot_sin],
            [rot_sin, rot_cos]
        ], dtype=float
    )
    delta_p = np.array(points) - np.array(center)  # 相对坐标

    roted_p = np.dot(rot_mat, delta_p[:, :2].T)
    roted_p = roted_p.T
    roted_p = roted_p + center

    return roted_p


def rot_points_dim3(center, points, angle):
    rot_sin = np.sin(np.deg2rad(angle))
    rot_cos = np.cos(np.deg2rad(angle))
    rot_mat = np.array(
        [
            [rot_cos, -rot_sin, 0],
            [rot_sin, rot_cos, 0],
            [0., 0., 1.]
        ], dtype=float
    )

    delta_p = np.array(points) - np.array(center)  # 相对坐标

    roted_p = np.dot(rot_mat, delta_p[:, :3].T)
    # roted_p = rot_mat @ delta_p[:, :3].T
    roted_p = roted_p.T
    roted_p = roted_p + center

    return roted_p






def main():

    start = 9.456
    end = 45.973

    step = 4.34

    dis = end - start

    cnt = int(round(dis / step, 0))
    print("cnt = ", cnt)
    real_step = dis / cnt
    print("real_step = ", real_step)

    a = np.arange(start, end, real_step)
    print(a, '\n',type(a))

def main2():

    p1 = np.array([0,0,0], dtype=float)

    p2 = np.array([2., 5. , 9.])

    step = 2.5

    res = cal_between_two_point(p1,p2,step)

    print(res)


if __name__ == '__main__':
    main2()



