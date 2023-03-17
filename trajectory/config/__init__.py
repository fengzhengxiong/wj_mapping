#!/usr/bin/env python
# -*- coding: utf-8 -*-


import platform


# config 文件夹放置的文件为配置文件，可以修改的，可通过导入外部yaml json等方式编辑修改


__appname__ = 'Trajectory'
__version__ = 'V2.1.1'
__date__ = "2022-9-5"
__author__ = "AnHaiyang, FengZhengxiong"
__right__ = "北京万集科技股份有限公司"


software_msg = "名称: %s   轨迹编辑软件\n" % __appname__ + \
    "版本: %s\n" % __version__ + \
    "时间: %s\n" % __date__ + \
    "作者: %s\n" % __author__ + \
    "所属: %s" % __right__



from .file_type import *


