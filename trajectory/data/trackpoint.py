#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
行车轨迹单点属性
"""


class TrackPoint(object):
    def __init__(self):
        self.lon = 0.0
        self.lat = 0.0
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0
        self.attr = 0
        self.speed = 0
        self.pt_id = 0


