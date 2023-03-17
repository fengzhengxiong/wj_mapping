#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
本py 模拟运行MVC模式， 因model内部逻辑需要其他模块对象/数据, 因此run仅做显示，不能产生交互

"""



import time
import numpy as np
import sys
from PyQt5.QtWidgets import QApplication

from trajectory.model.measure_model import MeasureModel
from trajectory.widgets.measure_dis_view import MeasureDisView


class MeasureController(object):
    def __init__(self, *args, **kwargs):
        super(MeasureController, self).__init__()

        self._app = QApplication(sys.argv)
        self._view = MeasureDisView()
        self._model = MeasureModel()

    def __init_connect(self):

        V = self._view
        M = self._model
        V.btn_measure.clicked.connect(lambda: M.set_enabled(True))
        V.btn_noMeasure.clicked.connect(lambda: M.set_enabled(False))
        V.btn_point1.clicked.connect(lambda: self.set_pos(1))
        V.btn_point2.clicked.connect(lambda: self.set_pos(2))

        M.showDistance.connect(self.show_distance)

    def show_distance(self, data):
        wp1, wp2 = np.round(data[0], 6), np.round(data[1], 6)
        self._view.edt_point_coord1.setText('{}, {}, {}'.format(wp1[0], wp1[1], wp1[2]))
        self._view.edt_point_coord2.setText('{}, {}, {}'.format(wp2[0], wp2[1], wp2[2]))
        wp1 = np.asarray(wp1)
        wp2 = np.asarray(wp2)
        L = np.linalg.norm(wp2 - wp1)
        self._view.edt_distance.setText('{} m'.format(np.round(L, 4)))

    def set_pos(self, h):
        self._model.set_distance_wid(h, (0, 10, 0))

    def run(self):
        self._view.show()
        return self._app.exec_()



if __name__ == "__main__":
    # import sys
    # app = QApplication(sys.argv)
    # _view = MeasureDisView()
    # _view.show()
    # sys.exit(app.exec_())
    c = MeasureController()
    c.run()


