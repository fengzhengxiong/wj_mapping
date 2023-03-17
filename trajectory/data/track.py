#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
"""
车轨迹类
"""


class Track(object):
    def __init__(self):

        self.lonlat_array = np.array([[0, 0]], dtype=float)
        self.pos_array = np.array([[0, 0, 0]], dtype=float)
        self.attr_array = np.array([0], dtype=int)




def main():
    t = Track()
    print(t.lonlat_array.shape)
    print(t.pos_array.shape)


main()