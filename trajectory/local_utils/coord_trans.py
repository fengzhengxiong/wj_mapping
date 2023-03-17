#!/usr/bin/env python
# -*- coding: utf-8 -*-


# 1. 地球坐标系——WGS84：常见于 GPS 设备，Google 地图等国际标准的坐标体系。
# 2. 火星坐标系——GCJ02：中国国内使用的被强制加密后的坐标体系，高德坐标就属于该种坐标体系。
# 3. 百度坐标系——BD-09：百度地图所使用的坐标体系，是在火星坐标系的基础上又进行了一次加密处理。
# 4. 天地图坐标系——CGCS2000：2000国家大地坐标系(CGCS 2000) 与 WGS84差别极小可以认为是同一种坐标系。



import math

# 圆周率π
pi = 3.1415926535897932384626
# 圆周率转换量
x_pi = pi * 3000.0 / 180.0
# 卫星椭球坐标投影到平面地图坐标系的投影英子
a = 6378245.0
# 椭球偏心率
ee = 0.00669342162296594323


def gcj02_to_bd09(lng, lat):
    """
    火星坐标系(GCJ-02)转百度坐标系(BD-09)
    :param lng:火星坐标经度
    :param lat:火星坐标纬度
    :return:
    """
    z = math.sqrt(lng * lng + lat * lat) + 0.00002 * math.sin(lat * x_pi)
    theta = math.atan2(lat, lng) + 0.000003 * math.cos(lng * x_pi)
    bd_lng = z * math.cos(theta) + 0.0065
    bd_lat = z * math.sin(theta) + 0.006
    return [bd_lng, bd_lat]


def gcj02_to_wgs84(lng, lat):
    """
    GCJ02(火星坐标系)转WGS84
    :param lng:火星坐标系的经度
    :param lat:火星坐标系纬度
    :return:
    """
    # 判断是否在国内
    if _out_of_china(lng, lat):
        return lng, lat
    d_lat = _transform_lat(lng - 105.0, lat - 35.0)
    d_lng = _transform_lng(lng - 105.0, lat - 35.0)
    rad_lat = lat / 180.0 * pi
    magic = math.sin(rad_lat)
    magic = 1 - ee * magic * magic
    sqrt_magic = math.sqrt(magic)
    d_lat = (d_lat * 180.0) / ((a * (1 - ee)) / (magic * sqrt_magic) * pi)
    d_lng = (d_lng * 180.0) / (a / sqrt_magic * math.cos(rad_lat) * pi)
    mg_lat = lat + d_lat
    mg_lng = lng + d_lng
    return [lng * 2 - mg_lng, lat * 2 - mg_lat]


def bd09_to_gcj02(bd_lon, bd_lat):
    """
    百度坐标系(BD-09)转火星坐标系(GCJ-02)
    :param bd_lat:百度坐标纬度
    :param bd_lon:百度坐标经度
    :return:转换后的坐标列表形式
    """
    x = bd_lon - 0.0065
    y = bd_lat - 0.006
    z = math.sqrt(x * x + y * y) - 0.00002 * math.sin(y * x_pi)
    theta = math.atan2(y, x) - 0.000003 * math.cos(x * x_pi)
    gg_lng = z * math.cos(theta)
    gg_lat = z * math.sin(theta)
    return [gg_lng, gg_lat]


def bd09_to_wgs84(bd_lon, bd_lat):
    """
    百度坐标系(BD-09)转WGS84
    :param bd_lat:百度坐标纬度
    :param bd_lon:百度坐标经度
    :return:转换后的坐标列表形式
    """
    lon, lat = bd09_to_gcj02(bd_lon, bd_lat)
    return gcj02_to_wgs84(lon, lat)


def wgs84_to_gcj02(lng, lat):
    """
    WGS84转火星坐标系(GCJ-02)
    :param lng:WGS84坐标系的经度
    :param lat:WGS84坐标系的纬度
    :return:
    """
    # 判断是否在国内
    if _out_of_china(lng, lat):
        return lng, lat
    d_lat = _transform_lat(lng - 105.0, lat - 35.0)
    d_lng = _transform_lng(lng - 105.0, lat - 35.0)
    rad_lat = lat / 180.0 * pi
    magic = math.sin(rad_lat)
    magic = 1 - ee * magic * magic
    sqrt_magic = math.sqrt(magic)
    d_lat = (d_lat * 180.0) / ((a * (1 - ee)) / (magic * sqrt_magic) * pi)
    d_lng = (d_lng * 180.0) / (a / sqrt_magic * math.cos(rad_lat) * pi)
    mg_lat = lat + d_lat
    mg_lng = lng + d_lng
    return [mg_lng, mg_lat]


def wgs84_to_bd09(lng, lat):
    """
    WGS84转百度坐标系(BD-09)
    :param lng:WGS84坐标系的经度
    :param lat:WGS84坐标系的纬度
    :return:
    """
    lng, lat = wgs84_to_gcj02(lng, lat)
    return gcj02_to_bd09(lng, lat)


def baidu_to_google(lng, lat):
    """
    百度转谷歌坐标
    :param lng:百度坐标系的经度
    :param lat:百度坐标系的纬度
    :return:
    """
    return bd09_to_wgs84(lng, lat)


def google_to_baidu(lng, lat):
    """
    谷歌转百度坐标
    :param lng:谷歌坐标系的经度
    :param lat:谷歌坐标系的纬度
    :return:
    """
    return wgs84_to_bd09(lng, lat)


def google_to_amap(lng, lat):
    """
    谷歌转高德坐标
    :param lng:WGS84坐标系的经度
    :param lat:WGS84坐标系的纬度
    :return:
    """
    return wgs84_to_gcj02(lng, lat)


def _transform_lat(lng, lat):
    ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + \
          0.1 * lng * lat + 0.2 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 *
            math.sin(2.0 * lng * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lat * pi) + 40.0 *
            math.sin(lat / 3.0 * pi)) * 2.0 / 3.0
    ret += (160.0 * math.sin(lat / 12.0 * pi) + 320 *
            math.sin(lat * pi / 30.0)) * 2.0 / 3.0
    return ret


def _transform_lng(lng, lat):
    ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + \
          0.1 * lng * lat + 0.1 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 *
            math.sin(2.0 * lng * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lng * pi) + 40.0 *
            math.sin(lng / 3.0 * pi)) * 2.0 / 3.0
    ret += (150.0 * math.sin(lng / 12.0 * pi) + 300.0 *
            math.sin(lng / 30.0 * pi)) * 2.0 / 3.0
    return ret


def _out_of_china(lng, lat):
    """
    判断是否在国内，不在国内不做偏移
    :param lng:
    :param lat:
    :return:
    """
    return not (73.66 < lng < 135.05 and 3.86 < lat < 53.55)


if __name__ == '__main__':
    pass
