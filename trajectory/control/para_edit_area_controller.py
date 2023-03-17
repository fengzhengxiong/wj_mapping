#!/usr/bin/env python
# -*- coding: utf-8 -*-


import time
import numpy as np
import sys
import copy
from PyQt5.QtWidgets import QApplication

from trajectory.widgets.para_edit_area_view import ParaEditAreaView
from trajectory.widgets.edit_widget_ import EditWidget_

from trajectory.config.file_type import map_txt_dic, map_key_list
from trajectory.local_utils.pub import *


class ParaEditAreaController(object):
    def __init__(self, view=None, model=None, *args, **kwargs):
        super(ParaEditAreaController, self).__init__()
        if view is not None:
            self._view = view
        else:
            self._view = ParaEditAreaView()
        try:
            self.init_view()
            pass
        except Exception as e:
            print(e)

    def init_view(self):
        """
        在原有视图基础上进行编辑
        :return:
        """
        _map_dic = copy.deepcopy(map_txt_dic)
        _map_list = copy.deepcopy(map_key_list)  # python 2.7 ,for order search

        dic_pop(_map_dic, "lon")
        dic_pop(_map_dic, "lat")
        _map_list.remove("lon")
        _map_list.remove("lat")

        # 创建属性列表
        self.wid_list = []

        for k in _map_list:
            v = _map_dic[k]
            label = v["ch"]
            if isinstance(v["val"], dict):
                mode = 'QComboBox'
                ew = EditWidget_(label, mode, parent=self._view.wid_)  # 加上parent 按钮显示正常
                strlist = []
                datalist = []
                colorlist = []
                for a, b in v["val"].items():  #   1:  {"des": "普通道路", "rgb": (10, 240, 10)},
                    strlist.append("%d - %s" % (a, b["des"]))
                    datalist.append(a)
                    if "rgb" in b:
                        colorlist.append(b["rgb"])
                ew.set_combo_attr(strlist, datalist, colorlist)

            else:
                mode = "QLineEdit"
                ew = EditWidget_(label, mode, parent=self._view.wid_)  # 加上parent 按钮显示正常
                ew.set_lineedit_number()

            ew.set_user_data(v["No"])  # 把当前项在txt所属列号，保存下来。
            self.wid_list.append(ew)

        for wid in self.wid_list:
            self._view.vbox.addWidget(wid)



    def __init_connect(self):

        pass

    def set_view(self, view):
        if isinstance(view, ParaEditAreaView):
            self._view = view

    def get_view(self):
        return self._view

    def set_model(self, model):
        pass


    def run(self):
        self._app = QApplication(sys.argv)
        self._view.show()
        return self._app.exec_()

    def show(self):
        self._view.show()


# if __name__ == "__main__":
#     v = ParaEditAreaView()
#     c = ParaEditAreaController(v)
#     # c.run()



if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    _view = ParaEditAreaView()
    c = ParaEditAreaController(_view)
    c.show()
    sys.exit(app.exec_())