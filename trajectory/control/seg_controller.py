#!/usr/bin/env python
# -*- coding: utf-8 -*-


import time
import numpy as np
import sys
from PyQt5.QtWidgets import QApplication

from trajectory.model.seg_model import SegModel
from trajectory.widgets.seg_edit_view import SegEditView


class SegController(object):
    def __init__(self, *args, **kwargs):
        super(SegController, self).__init__()

        self._app = QApplication(sys.argv)
        self._view = SegEditView()
        self._model = SegModel()

    def __init_connect(self):

        V = self._view
        M = self._model


        # M.set_tag_head_seg()
        # M.set_tag_tail_seg()
        #
        # # 段编辑
        # self.ui.btn_head.pressed.connect(lambda: self.slot_set_seg(1))
        # self.ui.btn_tail.pressed.connect(lambda: self.slot_set_seg(2))
        # self.ui.btn_closeseg.pressed.connect(lambda: self.slot_set_seg(3))
        # self.ui.btn_cancel.pressed.connect(lambda: self.slot_set_seg(4))
        #
        # self.vtk_wid.updateSegInfo.connect(self.disp_seg_info)  # 更新段信息

    def run(self):
        self._view.show()
        return self._app.exec_()


if __name__ == "__main__":
    c = SegController()
    c.run()

