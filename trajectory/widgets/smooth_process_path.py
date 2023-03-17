#!/usr/bin/env python
# -*- coding: utf-8 -*-

import copy
import math
from math import factorial
import time
import numpy as np

time1 = 0
space = 0.05
space_detal = 0.008
digui_time = 0

def Trans_angle_to_heading(angle):
    angle = 360 - angle
    angle = angle + 90
    if angle >= 360:
        angle = angle - 360
    return angle

def Cal_Vector_length(vx, vy):
    return (vx ** 2 + vy ** 2) ** 0.5

def Vector_doc_product(v1x, v1y, v2x, v2y):
    return v1x * v2x + v1y * v2y

def Xianduan_to_Vector(p1x, p1y, p2x, p2y):
    return p2x - p1x, p2y - p1y

def Caldis(x1, x2, y1, y2):
    return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5

def Get_nearest_index(px, py, maping_spacing):
    dis_near = 100
    nearest_index = -1
    for index, mi in enumerate(maping_spacing):
        dis_temp = Caldis(px, mi[0], py, mi[1])
        if dis_temp < dis_near:
            dis_near = dis_temp
            nearest_index = index
    return nearest_index

def Getpointnum(points, space):
    dis_straight = 0
    x_last, y_last = points[0][0], points[0][1]
    for point in points:
        dis_straight += Caldis(point[0], x_last, point[1], y_last)
        x_last, y_last = point[0], point[1]
    numf = int(100 * dis_straight / space)
    return numf

def Calangle(x1, x2, y1, y2):
    if x1 == x2:
        if y2 >= y1:
            angle = 90
        else:
            angle = -90
    else:
        angle = math.atan((y2 - y1) / (x2 - x1))
        angle = math.degrees(angle)
        if x2 < x1:
            if y2 < y1:
                angle = angle - 180
            else:
                angle = angle + 180
    return angle

def Select_path_point(px, py, space):
    x0, y0 = px[0], py[0]
    x, y, h = [], [], []
    for i in range(len(px)):
        dis = Caldis(px[i], x0, py[i], y0)
        if dis >= space or dis == 0:
            x.append(px[i])
            y.append(py[i])
            x0, y0 = px[i], py[i]
            if i == 0:
                angle = Calangle(px[0], px[1], py[0], py[1])
            elif i == len(px) - 1:
                angle = Calangle(px[i-1], px[i], py[i-1], py[i])
            else:
                angle = Calangle(px[i-1], px[i+1], py[i-1], py[i+1])
            hi = Trans_angle_to_heading(angle)
            h.append(round(hi, 3))
    return x, y, h

def Getpath(points, numf, space):
    N = len(points)      #控制点个数
    n = N - 1            #阶数
    px, py = [], []
    for T in range(numf):
        t = T / numf
        x, y = 0, 0

        for i in range(N):
            B = factorial(n) * t ** i * (1 - t) ** (n - i) / (factorial(i) * factorial(n - i))
            x += points[i][0] * B
            y += points[i][1] * B
        px.append(x)
        py.append(y)
    px, py, ph = Select_path_point(px, py, space)
    return px, py, ph

def Xianjie(line1, line2, maping_spacing):
    point1 = [line1[0][0], line1[0][1]]
    point2 = [line1[-1][0], line1[-1][1]]
    point3 = [line2[0][0], line2[0][1]]
    point4 = [line2[-1][0], line2[-1][1]]
    points = [point1, point2, point3, point4]
    numf = Getpointnum(points, space)
    px, py, ph = Getpath(points, numf, space)
    line_spacing = []
    for i in range(len(px)):
        line_spacing.append(copy.deepcopy(maping_spacing[0]))
    for i in range(len(px)):
        nearest_index = Get_nearest_index(px[i], py[i], maping_spacing)
        line_spacing[i] = copy.deepcopy(maping_spacing[nearest_index])
        line_spacing[i][0] = px[i]
        line_spacing[i][1] = py[i]
        line_spacing[i][14] = ph[i]
    return line_spacing

def point3s_to_question(point1, point2, point3):
    question_states = []
    v1x, v1y = Xianduan_to_Vector(point1[0], point1[1], point3[0], point3[1])
    v2x, v2y = Xianduan_to_Vector(point1[0], point1[1], point2[0], point2[1])
    v3x, v3y = Xianduan_to_Vector(point2[0], point2[1], point3[0], point3[1])
    v1_doc_v2 = Vector_doc_product(v1x, v1y, v2x, v2y)
    v2_doc_v3 = Vector_doc_product(v2x, v2y, v3x, v3y)
    if Cal_Vector_length(v1x, v1y) == 0:
        return 0, 0, 0, 0, [1.3]
    elif Cal_Vector_length(v2x, v2y) == 0 or Cal_Vector_length(v3x, v3y) == 0:
        return 0, 0, 0, 0, [1.2]
    v1_radians_v2 = math.acos(round(v1_doc_v2 / (Cal_Vector_length(v1x, v1y) * Cal_Vector_length(v2x, v2y)), 8))
    v2_radians_v3 = math.acos(round(v2_doc_v3 / (Cal_Vector_length(v2x, v2y) * Cal_Vector_length(v3x, v3y)), 8))
    v2_degrees_v3 = math.degrees(v2_radians_v3)
    if v2_degrees_v3 > 90:
        question_states.append(2)
    elif v2_degrees_v3 > 0.3:        # 角度的抖动
        question_states.append(3)
    dis_point2_to_v1 = Cal_Vector_length(v2x, v2y) * math.sin(v1_radians_v2)
    dis_point2_to_point3 = Caldis(point2[0], point3[0], point2[1], point3[1])
    if dis_point2_to_point3 > space + space_detal or dis_point2_to_point3 < space - space_detal:
        question_states.append(5)
    v1_radians_xaxis = math.acos(Vector_doc_product(v1x, v1y, 1, 0) / Cal_Vector_length(v1x, v1y))
    v1_degrees_xaxis = math.degrees(v1_radians_xaxis)
    v1_degrees_xaxis = v1_degrees_xaxis if v1y >= 0 else v1_degrees_xaxis * (-1)
    v1_heading = Trans_angle_to_heading(v1_degrees_xaxis)
    detal_heading_point2h_to_point13h = point2[2] - v1_heading
    if detal_heading_point2h_to_point13h >= 180:
        detal_heading_point2h_to_point13h -= 360
    elif detal_heading_point2h_to_point13h <= -180:
        detal_heading_point2h_to_point13h += 360
    return v2_degrees_v3, dis_point2_to_v1, dis_point2_to_point3, detal_heading_point2h_to_point13h, question_states

def Replace(i, maping1):
    if i < 11:
        line1 = [[mi[0], mi[1]] for mi in maping1[0: i]]
        line2 = [[mi[0], mi[1]] for mi in maping1[i + 6: i + 11]]
        starti, endi = 0, i + 10
    elif i > len(maping1) - 12:
        line1 = [[mi[0], mi[1]] for mi in maping1[i - 10: i - 5]]
        line2 = [[mi[0], mi[1]] for mi in maping1[i + 1:]]
        starti, endi = i - 10, len(maping1) - 1
    else:
        line1 = [[mi[0], mi[1]] for mi in maping1[i - 10: i - 5]]
        line2 = [[mi[0], mi[1]] for mi in maping1[i + 6: i + 11]]
        starti, endi = i - 10, i + 10
    maping_spacing = maping1[starti: endi + 1]
    line_spacing = Xianjie(line1, line2, maping_spacing)
    del maping1[starti: endi + 1]
    for linei_point in reversed(line_spacing):
        maping1.insert(starti, linei_point)
    return maping1

def Handle(maping1, result=None, start_index=1):
    global digui_time
    digui_time += 1
    if result is None:
        result = []
    if digui_time > 100:
        return maping1, result, 0
    for i in range(start_index, len(maping1) - 2):
        point1 = [maping1[i - 1][0], maping1[i - 1][1], maping1[i - 1][14]]
        point2 = [maping1[i][0], maping1[i][1], maping1[i][14]]
        point3 = [maping1[i + 1][0], maping1[i + 1][1], maping1[i + 1][14]]
        result_temp = point3s_to_question(point1, point2, point3)
        if result_temp[-1]:
            if 1.3 == min(result_temp[-1]):
                maping1.pop(i + 1)
                if i < 5:
                    return Handle(maping1)
                else:
                    result.append(result_temp)
                    return Handle(maping1, result, i - 3)
            elif 1.2 == min(result_temp[-1]):
                maping1.pop(i)
                if i < 5:
                    return Handle(maping1)
                else:
                    return Handle(maping1, result, i - 3)
            elif 2 == min(result_temp[-1]):
                maping1.pop(i + 1)
                if i < 5:
                    return Handle(maping1)
                else:
                    return Handle(maping1, result, i - 3)
            elif 3 == min(result_temp[-1]):
                maping1 = Replace(i, maping1)
                if i < 5:
                    return Handle(maping1)
                else:
                    return Handle(maping1, result, i - 3)
            elif min(result_temp[-1]) == 5:
                maping1 = Replace(i, maping1)
                if i < 5:
                    return Handle(maping1)
                else:
                    return Handle(maping1, result, i - 3)
        else:
            result.append(result_temp)
    return maping1, result, 1

def all_smooth(maping0,space0):
    global digui_time, time1,space
    space=space0
    time1 = time.time()
    digui_flag = 0
    maping0=maping0.tolist()
    while digui_flag == 0:
        maping_result, _, digui_flag = Handle(maping0)
        digui_time=0
    maping_result=np.array(maping_result)
    return maping_result[:,:2],maping_result[:,14]
