#!/usr/bin/env python
# -*- coding: utf-8 -*-


import time
import numpy as np
import sys
from functools import partial
import os
import os.path as osp
import copy

TEST_PATH = r'C:\Users\wanji\Desktop\自动驾驶\yuanqu2\collisionpath'
TEST_PATH = r"/data/test_map/"

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

try:
    import vtkmodules.all as vtk
    from vtkmodules.util.numpy_support import vtk_to_numpy, numpy_to_vtk
except ImportError:
    import vtk
    from vtk.util.numpy_support import vtk_to_numpy, numpy_to_vtk

from trajectory.config import __appname__, __version__, software_msg
from trajectory.config.file_type import tra_property_dic, turn_light_dic, ID_PROPERTY, ID_SPEED, ID_TURNLIGHT,  file_suffix, save_dir,jsonfile_suffix
from trajectory.config.common_variable import *
from trajectory.widgets.main_view import MainView

from trajectory.model.vtk_show_model import VtkShowModel
from trajectory.model.seg_model import SegModel
from trajectory.model.measure_model import MeasureModel
from trajectory.model.data_model import DataModel
from trajectory.model.interactor_style_band import InteractorStyleBand
from trajectory.model.interactor_style_parallel import InteractorStyleParallel
from trajectory.manager.app_manager import app_manager, AppMode
from trajectory.manager.event_type import *
from trajectory.manager.common_mode import *
from trajectory.manager.area_pick_manager import area_pick_manager, AreaPickMode
from trajectory.manager.action_manager import action_manager, ActionData
from trajectory.manager.file_data_manager import ArrayDataManager
from trajectory.manager.project_manager import project_manager
from trajectory.control.para_edit_area_controller import ParaEditAreaController
from trajectory.control.menu_bar_controller import MenuBarController
from trajectory.control.tool_bar_controller import ToolBarController
from trajectory.control.file_list_controller import FileListController

from trajectory.local_utils.math_util import *
from trajectory.local_utils.pub import *
from trajectory.local_utils.file_utils import *

from trajectory.widgets.smooth_process_path import *


class MainController(object):
    def __init__(self, *args, **kwargs):
        super(MainController, self).__init__()

        self.__init_var()

        # 初始化顺序不能随机变更---
        self._view = MainView()  # 界面
        self.__init_model()  # 模型数据
        self.__view_edit()  # 控件动态添加， 根据配置文件二次编辑---
        self.__init_connect()  # 链接槽

    def __view_edit(self):
        """
        子界面模块的一些控件编辑
        :return:
        """

        self._view.wid_segedit.sbx_pin1.setRange(-999, 99999999)
        self._view.wid_segedit.sbx_pin2.setRange(-999, 99999999)

        self._view.wid_multiselectchoose.btn_select.setChecked(True)
        area_pick_manager.set_pick_mode(AreaPickMode.DEFULT)  # 设置多选模式为默认选择

        self._view.wid_addpoint.btn_add_point_enable.setCheckable(True)  # 单点插值开关
        self._view.wid_addpoint.btn_auto_add_enable.setCheckable(True)  # 自动插值开关
        self._view.wid_addpoint.spbx_space.setRange(0.01, 999999)  # 自动添加点的间距设置
        self._view.wid_addpoint.spbx_space.setValue(1.0)
        self._view.wid_addpoint.spbx_space.setSingleStep(1.0)
        self._view.wid_addpoint.spbx_space.setSuffix(' cm')

        self._view.wid_btnarea.btn_area_pick.setCheckable(True)  # 切换多选模式

        # 属性编辑控件
        self._con_pare_edit = ParaEditAreaController(self._view.wid_paraedit)  # 对wid_paraedit 进行控件搭建
        # 菜单栏控件
        self._con_menubar = MenuBarController(self._view)

        self._con_menubar.actions.openfile.setEnabled(False)

        # 工具栏
        self._con_toolbar = ToolBarController(self._view, Qt.TopToolBarArea)
        self.cb_vtk_sen = QComboBox(self._con_toolbar.toolbar)  # 调节灵敏度。
        self.cb_vtk_sen.addItems(['1', '2', '3', '4', '5'])
        self.cb_vtk_sen.setCurrentText('2')
        self._con_toolbar.add_actions([self._con_menubar.actions.opendir,
                                       self._con_menubar.actions.savefile,
                                       QLabel('灵敏度:'),
                                       self.cb_vtk_sen])

        self._con_file_list = FileListController(self._view.wid_filelist)

        self._view.wid_smooth.spbx_space.setRange(0.01, 999999)  # 路径平滑的间距设置
        self._view.wid_smooth.spbx_space.setValue(5.0)
        self._view.wid_smooth.spbx_space.setSingleStep(5.0)
        self._view.wid_smooth.spbx_space.setSuffix(' cm')

    def show(self):
        self._view.show()

    def __init_model(self):
        """
        model 初始化， 模型变量定义 m_xxx
        :return:
        """
        self.ren = self._view.wid_vtkshow.renderer
        self.window = self._view.wid_vtkshow.window
        self.m_vtk_show = VtkShowModel(self.ren, self.window)

        self.m_seg = SegModel(self.ren, self.window)

        self.m_measure = MeasureModel(self.ren, self.window)
        self.m_measure.showDistance.connect(self.update_dis_msg)  # 测距控件 信息刷新触发

        self.m_data = DataModel()  # np 数据

        action_manager.register(self.m_data.restore_data)
        action_manager.register(self.m_vtk_show.restore_data)
        action_manager.register(self._view.wid_tabdata.restore_data)  # 表格回退测试

        self.style_band = InteractorStyleBand(self.ren, self.window, self.callback_func)
        self.style_parallel = InteractorStyleParallel(self.ren, self.window, self.callback_func)

        self._view.wid_vtkshow.interactor.SetInteractorStyle(self.style_parallel)

    def __init_connect(self):
        # 菜单栏
        self._con_menubar.actions.openfile.triggered.connect(self.open_file_dialog)
        self._con_menubar.actions.savefile.triggered.connect(self.save_file)
        self._con_menubar.actions.quit.triggered.connect(self._view.close)
        self._con_menubar.actions.opendir.triggered.connect(self.open_dir_dialog)
        self._con_menubar.actions.openjsonfile.triggered.connect(self.open_json_dir_dialog)
        self._con_menubar.actions.enablefile.triggered.connect(self.set_enable_file_from_hover)
        self._con_menubar.actions.undo.triggered.connect(lambda: self.restore_data(True))
        self._con_menubar.actions.redo.triggered.connect(lambda: self.restore_data(False))

        self._con_menubar.actions.shortcutExplain.triggered.connect(lambda: self.show_instructions_info(1))
        self._con_menubar.actions.about.triggered.connect(lambda: self.show_instructions_info(0))

        # 工具栏

        self.cb_vtk_sen.currentIndexChanged.connect(self.adjust_vtk_sensitivity)

        # 多选按钮
        self._view.wid_multiselectchoose.btn_toggle_signal.connect(self.toggle_pick_mode)

        # 按钮区
        btnArea = self._view.wid_btnarea
        btnArea.btn_clear_select.clicked.connect(self.clear_selected)  # clear
        btnArea.btn_area_pick.clicked.connect(self.toggle_region_add_mode)  # area_pick
        btnArea.btn_del.clicked.connect(self.delete_selected)  # 删除
        btnArea.btn_undo.clicked.connect(lambda: self.restore_data(True))  # undo
        btnArea.btn_redo.clicked.connect(lambda: self.restore_data(False))  # redo

        # 段编辑区域
        segEdit = self._view.wid_segedit
        segEdit.btn_cancel.clicked.connect(lambda: self.set_seg_mode(SegMode.SEG_NONE))
        segEdit.btn_head.clicked.connect(lambda: self.set_seg_mode(SegMode.SEG_HEAD))
        segEdit.btn_tail.clicked.connect(lambda: self.set_seg_mode(SegMode.SEG_TAIL))
        segEdit.btn_neighbor.clicked.connect(lambda: self.set_seg_mode(SegMode.SEG_CLOSE))

        # 测量功能
        meaDis = self._view.wid_measuredis
        meaDis.btn_measure.clicked.connect(lambda: self.set_diswid_enable(True))
        meaDis.btn_noMeasure.clicked.connect(lambda: self.set_diswid_enable(False))
        meaDis.btn_point1.clicked.connect(lambda: self.set_diswid_handle(1))
        meaDis.btn_point2.clicked.connect(lambda: self.set_diswid_handle(2))

        # 新增点控件
        addPoint = self._view.wid_addpoint
        # 对于开关按钮  clicked  press 触发信号时按钮的状态的不用的， set_add_point_mode 函数要注意
        addPoint.btn_add_point_enable.clicked.connect(self.set_add_point_mode)  # 插入单点
        addPoint.btn_auto_add_enable.clicked.connect(self.set_add_auto_mode)  # 自动插值
        addPoint.btn_reset.clicked.connect(self.reset_add_point)  # reset 重置
        addPoint.btn_undo.clicked.connect(lambda: self.add_point_undo(True))  # undo
        addPoint.btn_redo.clicked.connect(lambda: self.add_point_undo(False))  # redo
        addPoint.btn_preview.clicked.connect(self.preview_auto_add_point)  # 预览

        addPoint.btn_finish.clicked.connect(lambda: self.finish_add_point(False))  # 完成
        addPoint.btn_finish_auto.clicked.connect(lambda: self.finish_add_point(True))  # 完成

        addPoint.btn_cancel.clicked.connect(lambda: self.cancel_add_point_mode(False))  # 取消
        addPoint.btn_cancel_auto.clicked.connect(lambda: self.cancel_add_point_mode(True))  # 取消

        # 平滑处理功能控件
        smoothProcess = self._view.wid_smooth
        smoothProcess.btn_start_smooth.clicked.connect(self.start_smooth_path)  # 路径平滑
        smoothProcess.btn_end_smooth.clicked.connect(self.finish_smooth_path)  # 路径平滑完成
        smoothProcess.btn_start_smooth_v.clicked.connect(self.start_smooth_v)  # 速度平滑

        # 额外工作区功能控件
        additionwork=self._view.wid_additionwork
        additionwork.btn_color_change_ok.clicked.connect(self.color_change_ok)  # 单独改变地图颜色
        additionwork.btn_color_change_esc.clicked.connect(self.color_change_esc)  # 单独改变地图颜色

        # 参数编辑
        for ew in self._con_pare_edit.wid_list:
            #  ew is  EditWidget_
            ew.click_signal.connect(self.edit_para_property)

        # 文件列表
        self._con_file_list.fileUpToDown.connect(lambda: self.load_file_batch(False))  # 添加↓ 触发信号
        self._con_file_list.downDoubleClicked.connect(self.set_file_enable)  # 双击列表切换使能文件
        self._con_file_list.toggleCheck.connect(self.toggle_show_and_hide)  # 列表勾选
        self._con_file_list.removeFile.connect(self.remove_file)  # 删除↑
        self._con_file_list.showFile.connect(self.show_file)  #

    def __init_var(self):
        self.ori_files = []  # 文件夹内的文件列表
        self.files = []  # 打开的文件列表
        self.last_dir = None  # 当前打开的文件夹。

        # 使能。。。。。。

    def reset(self):
        project_manager.reset()
        self.ori_files = []
        self.files = []

        # 各个model自行reset
        self.m_data.reset()
        self.m_vtk_show.reset()
        self.m_seg.reset()
        self.m_measure.reset()

        # 界面view reset
        self._view.wid_vtkshow.reset()
        self._view.wid_segedit.reset()
        self._view.wid_filelist.reset()

        # self._view.wid_tabdata.clear_table()

    def set_dirty(self):
        """
        设置文件 改动了
        :return:
        """
        project_manager.set_dirty(project_manager.enable_file)
        self._con_file_list.set_file_state(project_manager.enable_file, True)

        self.update_undo_enable()

    def set_clean(self, file=None, all=True):
        """
        文件干净， 用于保存执行之后。
        :param file: 某个文件为clean 若为None ，则默认将当前文件为clean
        :param all:
        :return:
        """
        if not all:
            _file = file if file is not None else project_manager.enable_file
            project_manager.set_clean(_file)
            self._con_file_list.set_file_state(_file, False)
        else:
            for file in self.files:
                project_manager.set_clean(file)
                self._con_file_list.set_file_state(file, False)

    def callback_func(self, *args, **kwargs):
        """
        被回调函数   interactor
        :param args:
        :param kwargs:
        :return:
        """

        ev = kwargs.get("ev", '')
        # pos = kwargs.get("pos", (0, 0, 0))

        if ev == EV_MOUSE_HOVER:
            point_id = kwargs.get("id", -1)
            obj = kwargs.get("obj", None)
            self.hover_single_point(obj, point_id)

        elif ev == EV_MOUSE_HOVER_SEG:
            point_id = kwargs.get("id", -1)
            obj = kwargs.get("obj", None)
            self.hover_batch_points(obj, point_id)

        elif ev == EV_SELECT_SEG:
            point_id = kwargs.get("id", -1)
            obj = kwargs.get("obj", None)
            self.select_seg_point(obj, point_id)

        elif ev == EV_PICK_POINT:
            point_id = kwargs.get("id", -1)
            obj = kwargs.get("obj", None)

            self.select_single_point(obj, point_id)

        elif ev == EV_SET_TAG1:
            point_id = kwargs.get("id", -1)
            obj = kwargs.get("obj", None)
            self.tag_point(obj, point_id, 1)

        elif ev == EV_SET_TAG2:
            point_id = kwargs.get("id", -1)
            obj = kwargs.get("obj", None)
            self.tag_point(obj, point_id, 2)

        elif ev == EV_AREA_PICK:
            picker = kwargs.get("picker", None)
            if isinstance(picker, vtk.vtkAreaPicker):
                self.select_region_points(picker)

        elif ev == EV_ADDING_POINT:
            pos = kwargs.get("pos", None)
            if pos is not None:
                self.new_point_by_click(pos)

        elif ev == EV_RESET_SELECT:
            self.clear_selected()

        elif ev == EV_MOVE_SELECT:
            delta = kwargs.get("delta", None)  # 位移矢量 (x,y,0)
            # print("{} - delta ={} ".format(EV_MOVE_SELECT, delta))

            self.move_point(delta_pos=delta)

        elif ev == EV_ROTATE_SELECT:
            delta = kwargs.get("delta_ang", None)  # 旋转角度
            self.rotate_point(delta_ang=delta)

    def check_app_mode(self):
        print('行:', sys._getframe().f_lineno, ' ', sys._getframe().f_code.co_name)
        if app_manager.get_app_mode() == AppMode.DEFULT:
            return True
        else:
            self.infoMessage("检查应用模式", "切换到普通模式再操作,当前模式:{}".format(app_manager.get_app_mode()))
            return False

    def check_dirty(self):
        """
        检查文件是否保存
        :return:  继续后续的操作  返回True  ，阻止继续操作返回False
        """
        print('行:', sys._getframe().f_lineno, ' ', sys._getframe().f_code.co_name)
        if not project_manager.is_dirty():
            return True

        mb = QtWidgets.QMessageBox
        title = self._view.tr("保存数据")
        msg = self._view.tr('是否先将文件保存?')
        answer = mb.question(self._view, title, msg, mb.Save | mb.Discard | mb.Cancel, mb.Save)
        if answer == mb.Discard:
            return True
        elif answer == mb.Save:
            self.save_file()
            return True
        else:  # answer == mb.Cancel
            return False

    def check_dirty_in_files(self, files):
        """
        检查部分文件是否要保存
        :return:  继续后续的操作  返回True  ，阻止继续操作返回False
        """
        print('行:', sys._getframe().f_lineno, ' ', sys._getframe().f_code.co_name)

        _dirty = False
        for file in files:
            if project_manager.get_dirty(file):
                _dirty = True
                break
        if not _dirty:
            return True

        mb = QtWidgets.QMessageBox
        title = self._view.tr("检查数据是否改动")
        msg = self._view.tr('是否先将文件保存?')
        answer = mb.question(self._view, title, msg, mb.Save | mb.Discard | mb.Cancel, mb.Save)
        if answer == mb.Discard:
            return True
        elif answer == mb.Save:
            for file in files:
                self.save_single_file(file)
                print('行:', sys._getframe().f_lineno, ' ', sys._getframe().f_code.co_name)
            return True
        else:  # answer == mb.Cancel
            return False

    def update_undo_enable(self):
        # undo redo 堆栈使能
        self._view.wid_btnarea.btn_undo.setEnabled(action_manager.is_restorable(project_manager.enable_file, True))
        self._view.wid_btnarea.btn_redo.setEnabled(action_manager.is_restorable(project_manager.enable_file, False))
        self._con_menubar.actions.undo.setEnabled(action_manager.is_restorable(project_manager.enable_file, True))
        self._con_menubar.actions.redo.setEnabled(action_manager.is_restorable(project_manager.enable_file, False))

    def adjust_vtk_sensitivity(self):
        """ 调节灵敏度"""
        app_manager.vtk_move_sensitivity = int(self.cb_vtk_sen.currentText())

    def open_file_dialog(self):
        """菜单 打开文件"""
        print('行:', sys._getframe().f_lineno, ' ', sys._getframe().f_code.co_name)

        if not self.check_app_mode():
            return
        if not self.check_dirty():
            return

        if self.last_dir and osp.exists(self.last_dir):
            defaultOpenDirPath = self.last_dir
        else:
            defaultOpenDirPath = osp.abspath('.')

        default_path = defaultOpenDirPath
        if self.ori_files:
            default_path = osp.dirname(self.ori_files[-1])

        default_path = r'C:\Users\wanji\Desktop\自动驾驶\yuanqu2'

        targetDirPath = QtWidgets.QFileDialog.getOpenFileName(caption='选择文件',
                                                              directory=default_path,
                                                              filter='')

        print(targetDirPath)
        if targetDirPath[0]:
            fn = targetDirPath[0]

            if fn in self.ori_files:
                # 添加文件到下边。

                down_files = self._con_file_list.get_files(False, GetItemMode.ALL)


                return

            if osp.exists(fn):
                lst_append_once(self.ori_files, fn)

                # TODO 列表里添加， 这个文件。同时将该文件设为使能。

                self.load_file(fn)

    def open_json_dir_dialog(self):
        print('行:', sys._getframe().f_lineno, ' ', sys._getframe().f_code.co_name)

        if self.last_dir and osp.exists(self.last_dir):
            defaultOpenDirPath = self.last_dir
        else:
            defaultOpenDirPath = osp.abspath('.')

        if TEST_PATH is not None:
            defaultOpenDirPath = TEST_PATH

        targetDirPath = str(
            QtWidgets.QFileDialog.getExistingDirectory(
                self._view,
                self._view.tr("%s - Open Directory") % __appname__,
                defaultOpenDirPath,
                QtWidgets.QFileDialog.ShowDirsOnly
                | QtWidgets.QFileDialog.DontResolveSymlinks,
            )
        )

        print('targetJsonDirPath=', targetDirPath)
        if targetDirPath:
            self.disp_json_dir_files(targetDirPath)

    def disp_json_dir_files(self, dirpath, pattern=None):
        samedir = True if self.last_dir is not None and self.last_dir == dirpath else False
        if samedir:
            # 重复打开同一个文件夹，其他处理~
            pass

        self.last_dir = dirpath
        _files = scan_all_files(dirpath, ext=jsonfile_suffix)
        _save_path = osp.join(dirpath, save_dir)
        self.ori_files = [file for file in _files if osp.isfile(file) and str(_save_path) not in str(file)]
        self._con_file_list.load_json_file(self.ori_files, dirpath)

    def open_dir_dialog(self):
        print('行:', sys._getframe().f_lineno, ' ', sys._getframe().f_code.co_name)

        if not self.check_app_mode():
            return
        if not self.check_dirty():
            return

        if self.last_dir and osp.exists(self.last_dir):
            defaultOpenDirPath = self.last_dir
        else:
            defaultOpenDirPath = osp.abspath('.')

        if TEST_PATH is not None:
            defaultOpenDirPath = TEST_PATH

        targetDirPath = str(
            QtWidgets.QFileDialog.getExistingDirectory(
                self._view,
                self._view.tr("%s - Open Directory") % __appname__,
                defaultOpenDirPath,
                QtWidgets.QFileDialog.ShowDirsOnly
                | QtWidgets.QFileDialog.DontResolveSymlinks,
            )
        )
        print('targetDirPath=', targetDirPath)
        if targetDirPath:
            self.disp_dir_files(targetDirPath)

    def disp_dir_files(self, dirpath, pattern=None):
        """
        显示文件夹内文件，到控件列表中
        :return:
        """
        samedir = True if self.last_dir is not None and self.last_dir == dirpath else False
        if samedir:
            # 重复打开同一个文件夹，其他处理~
            pass

        # 复位所有变量
        self.reset()

        self.last_dir = dirpath
        self._view.setWindowTitle("{}-{}  {}".format(__appname__, __version__, self.last_dir))

        _files = scan_all_files(dirpath, ext=file_suffix)
        _save_path = osp.join(dirpath, save_dir)
        self.ori_files = [file for file in _files if osp.isfile(file) and str(_save_path) not in str(file)]

        self._con_file_list.load_file_list(self.ori_files, dirpath)

    def load_file(self, filename, refresh=False):
        """
        加载文件
        :param filename:
        :param refresh: 是否要强制重新加载txt内容。的、
        :return:
        """

        # 如果是新增文件，默认是clean的。
        if not project_manager.get_dirty(filename):
            project_manager.set_clean(filename)

        try:
            # 加载数据data --------
            self.m_data.load_file(filename, refresh)
            array = self.m_data.get_data(filename)
            if array is None:
                return False

            # 数据加载到缓存队列，为第一项  ----
            if not refresh and action_manager.file_check(filename):
                # 不更新缓存队列
                pass
            else:
                _copy_data = np.copy(array)
                ad = ActionData(ActionMode.ADD, [0], _copy_data)  # 这里用深拷贝，避免array之后改变影响队列数据。
                ad.set_other_data(file=project_manager.enable_file)
                action_manager.new_queue(filename, ad)

            # 显示 ----------
            if not refresh and self.m_vtk_show.check_file(filename):
                pass
            else:
                pts = ArrayDataManager.get_points_dim3_array(array)
                rgb = ArrayDataManager.get_color_array(array)

                # 注意判定numpy 不能直接用if pts  ，
                # 否则报错 The truth value of an array with more than one element is ambiguous. Use a.any() or a.all()
                if pts is not None and rgb is not None:
                    self.m_vtk_show.load_point(filename, pts, rgb)
                else:
                    print(" error-----  ")

            # 表格添加
            if not refresh and self._view.wid_tabdata.check_file(filename):
                pass
            else:
                data = self.m_data.get_data(filename)
                self._view.wid_tabdata.load_table(filename, data)

            # 设置使能文件，要放到各个模块加载完毕之后执行
            if project_manager.enable_file is None:
                self.set_file_enable(filename)


        except Exception as e:
            print(e)

    def load_json_file(self, filename):
        json_path = filename.split('\\')[-1]

        if 'outline' in json_path:
            color_index = 1
        if 'center' in json_path:
            color_index = 2
        if 'stoplines' in json_path:
            color_index = 3
        if 'crosswalks' in json_path:
            color_index = 4

        if  color_index == 1:
            array, json_line_temp_length ,left_linetype, right_linetype, left_right_count = self.m_data.load_json_file(filename,color_index)
            pts, rgb = ArrayDataManager.get_points_dim3_array_json(array, color_index)
            if pts is not None and rgb is not None:
                self.m_vtk_show.load_outline(filename, pts, rgb,json_line_temp_length,left_linetype,right_linetype,left_right_count)
            else:
                print(' error--------------- ')

        else:
            array, json_line, json_line_temp_length = self.m_data.load_json_file(filename,color_index)
            pts, rgb = ArrayDataManager.get_points_dim3_array_json(array, color_index)
            if pts is not None and rgb is not None:
                if json_line is False:
                    self.m_vtk_show.load_point(filename, pts, rgb)
                else:
                    self.m_vtk_show.load_line(filename, pts, rgb, json_line_temp_length)
            else:
                print(' error--------------- ')

    def load_file_batch(self, force=False):
        """
        批量加载文件
        :param force: 是否强制重新加载txt文件。
        :return:
        """
        if force is True:
            # TODO 检查是否有更改未保存的，提示让其保存或取消。
            pass

        self.files = self._con_file_list.get_files(up=False, choose=GetItemMode.ALL)  # 获取下边控件所有文件 list

        datas = []
        for file in self.files:
            temp=file.split('.')[1]
            if temp == 'json':
                self.load_json_file(file)

            if temp == 'txt':
                self.load_file(file, force)
                datas.append(self.m_data.get_data(file))

        # 设置段max值，对首次加载有用
        self.m_seg.set_max_id(self.m_vtk_show.enable_actor.pts.count - 1)

        show_list = self.m_vtk_show.update_show_actor()

        if hasattr(self, "style_band"):
            self.style_band.set_pointpicker_proplist(show_list)
        if hasattr(self, "style_parallel"):
            self.style_parallel.set_pointpicker_proplist(show_list)

    def remove_file(self):
        """
        删除文件
        :return:
        """
        if self._con_file_list.count(False) == 0:
            return

        rm_files = self._con_file_list.get_files(False, GetItemMode.SELECTED)

        if len(rm_files) == 0:
            self.infoMessage("移除文件", "请选择文件")
            return False

        if project_manager.enable_file in rm_files:
            if app_manager.get_app_mode() in [AppMode.ADD_POINT_AUTO, AppMode.ADD_POINT]:
                self.infoMessage("移除文件", "移除文件包含使能文件，不允许插值模式下执行当前操作")
                return False

        # 判断移除的文件中是否有改动未保存的
        if not self.check_dirty_in_files(rm_files):
            return False

        left_files = list(set(self.files) - set(rm_files))

        if len(left_files) > 0:
            # 还有剩余文件
            natural_sort(left_files, key=lambda x: x.lower())
            if project_manager.enable_file not in left_files:
                self.set_file_enable(left_files[0])
        else:
            # 文件删除干净
            project_manager.enable_file = None
            project_manager.reset_file_state()
            self.m_vtk_show.enable_actor = None

        for file in rm_files:
            temp=file.split('\\')[-1]
            if 'txt' in temp:
                self.m_data.remove_file(file)
                self.m_vtk_show.remove_file(file)
                self.m_seg.reset()
                action_manager.destroy_queue(file)
                self._con_file_list.remove_file(file)
                self._view.wid_tabdata.close_table(file)
            else:
                self.m_vtk_show.remove_file(file)
                self._con_file_list.remove_file(file)
        self.files = left_files

    def set_enable_file_from_hover(self):
        """
        快捷键方式 切换使能文件
        :return:
        """
        if project_manager.hover_file is not None and \
                project_manager.hover_file != project_manager.enable_file:
            self.set_file_enable(project_manager.hover_file)

    def set_file_enable(self, file):
        """
        设置文件使能
        :param file:
        :return:
        """
        try:
            # 切换使能文件，先检查app模式，
            if app_manager.get_app_mode() in [AppMode.ADD_POINT, AppMode.ADD_POINT_AUTO]:
                self.infoMessage("切换使能文件", "增加点模式下不能切换使能文件")
                return

            if file != project_manager.enable_file:
                project_manager.enable_file = file

                self.m_vtk_show.clear_selected()  # 选中状态，消除
                self.m_seg.reset()  # 段消除
                self.disp_seg_info()

                self._view.wid_smooth.lbl_smooth_path_.setText(project_manager.enable_file)  # 平滑处理处使能文件路径更新
                self._view.wid_smooth.lbl_smooth_path_v_.setText(project_manager.enable_file)

                self.m_vtk_show.set_enable_actor(file)
                self._con_file_list.set_enable_file(file)  # 列表显示使能

                self.update_undo_enable()  # 切换使能，更新之

        except Exception as e:
            print(e)

    def show_file(self, choose=1):
        """
        显示选择
        :param choose: 1 显示  0  隐藏  -1 反显
        :return:
        """
        # print('行:', sys._getframe().f_lineno, ' ', sys._getframe().f_code.co_name)
        # print(choose)
        # 切换使能文件，先检查app模式，
        if app_manager.get_app_mode() in [AppMode.ADD_POINT, AppMode.ADD_POINT_AUTO]:
            self.infoMessage("显示文件", "增加点模式下不可操作")
            return
        # 查看是否有选中 ，然后  ，屏蔽 toggle_show_and_hide信号 设定显示隐藏  打开信号
        if self._con_file_list.count(False) == 0:
            return

        files = self._con_file_list.get_files(False, GetItemMode.SELECTED)
        if len(files) == 0:
            self.infoMessage("显示文件", "请选择文件")
            return False

        self._con_file_list.toggleCheck.disconnect()
        if choose == 1:
            for file in files:
                self._con_file_list.set_show_file(file, True)
        elif choose == 0:
            for file in files:
                self._con_file_list.set_show_file(file, False)
        elif choose == -1:
            checks = self._con_file_list.get_files(False, GetItemMode.CHECKED)
            for file in files:
                flg = False if file in checks else True
                self._con_file_list.set_show_file(file, flg)

        self._con_file_list.toggleCheck.connect(self.toggle_show_and_hide)
        self.toggle_show_and_hide()

    def toggle_show_and_hide(self):

        # print('行:', sys._getframe().f_lineno, ' ', sys._getframe().f_code.co_name)
        try:

            check_files = self._con_file_list.get_files(False, GetItemMode.CHECKED)
            # print(check_files)
            # print(self.files)
            _visable = {}

            for file in self.files:
                _visable[file] = True if file in check_files else False
            self.m_vtk_show.dic_visible = copy.deepcopy(_visable)
            show_list = self.m_vtk_show.update_show_actor()
            self.style_parallel.set_pointpicker_proplist(show_list)
            self.style_band.set_pointpicker_proplist(show_list)

        except Exception as e:
            print(e)

    def save_file(self):
        print('save_file--------')
        for file in self.files:
            if project_manager.get_dirty(file):
                # 如果改动的，要保存
                self.m_data.save_file(file, self.last_dir)
                self.set_clean(file=file, all=False)

    def save_single_file(self, file):
        print('行:', sys._getframe().f_lineno, ' ', sys._getframe().f_code.co_name)
        print('file = ', file)

        if project_manager.get_dirty(file):
            self.m_data.save_file(file, self.last_dir)
            self.set_clean(file=file, all=False)

    def toggle_pick_mode(self):
        """
        切换多选模式
        :return:
        """

        # print('toggle_pick_mode')
        msc = self._view.wid_multiselectchoose
        _map = {
            msc.btn_select: AreaPickMode.DEFULT,
            msc.btn_add_select: AreaPickMode.ADD_PICK,
            msc.btn_sub_select: AreaPickMode.SUB_PICK,
            msc.btn_inverse_select: AreaPickMode.INVERSE_PICK,
        }

        for k, v in _map.items():
            if k.isChecked():
                area_pick_manager.set_pick_mode(v)
                break

        # print("moshi = ", area_pick_manager.get_pick_mode())

    def clear_selected(self):
        """清除选中"""
        self.m_vtk_show.clear_selected()
        project_manager.selected_list = []
        # TODO  清除选择 ，表格 ？

    def delete_selected(self):
        """  删除  """
        if project_manager.enable_file is None:
            return

        # 先获取要删除的列表
        # rm_ids = self.m_vtk_show.get_selected_list()  # 获取删除索引s
        rm_ids = copy.deepcopy(project_manager.selected_list)

        #  做backup  store
        data = self.m_data.get_data(project_manager.enable_file)
        if data is None:
            self.errorMessage("删除点", "获取数据失败 file={}".format(project_manager.enable_file))
            return

        # backup 缓存
        rm_data = np.copy(data[rm_ids, :])
        # print('select :', rm_ids)
        # print('rm_data = ', rm_data[:, :2])
        # rm_ids = rm_.tolist()

        ad = ActionData(ActionMode.SUB, rm_ids, rm_data)  # st 在当前索引开始增加。
        ad.set_other_data(file=project_manager.enable_file)
        action_manager.store(project_manager.enable_file, ad)

        ret = self.m_data.delete_data(project_manager.enable_file, rm_ids)
        if not ret:
            # 如果删除失败， 回退backup， 报错
            pass
        self.m_vtk_show.delete_selected_points()
        project_manager.selected_list = []

        #  TODO 表格更新删除。
        self._view.wid_tabdata.del_row_table(project_manager.enable_file, rm_ids)

        # 解除图钉。
        self.set_seg_mode(SegMode.SEG_NONE)

        # 文件改变
        self.set_dirty()

        cnt = self.m_vtk_show.get_current_point_count()
        if cnt is None:
            self.errorMessage("删除完成", "获取点数量失败")
            return

        self.m_seg.set_max_id(cnt - 1)

    def toggle_region_add_mode(self):
        pass
        # print('行:', sys._getframe().f_lineno, ' ', sys._getframe().f_code.co_name)
        # print('toggle_region_add_mode---  ')

        _btn = self._view.wid_btnarea.btn_area_pick

        if not _btn.isChecked():
            # print('11111')

            # 平滑处理
            selected_list = self.m_vtk_show.get_selected_list()
            if selected_list:
                self._view.wid_smooth.lbl_start_id_.setText(str(selected_list[0]))
                self._view.wid_smooth.lbl_end_id_.setText(str(selected_list[-1]))
                self._view.wid_smooth.lbl_start_id_v_.setText(str(selected_list[0]))
                self._view.wid_smooth.lbl_end_id_v_.setText(str(selected_list[-1]))
            # 平滑处理

            app_manager.set_app_mode(AppMode.DEFULT)
            self._view.wid_vtkshow.interactor.SetInteractorStyle(self.style_parallel)
            self.style_parallel.update_cursor_shape()

        else:
            ret = True
            if app_manager.get_app_mode() in [AppMode.ADD_POINT, AppMode.ADD_POINT_AUTO]:
                self.infoMessage("开启框选", "插值状态下不能切换框选模式")
                ret = False

            if ret is True:
                app_manager.set_app_mode(AppMode.AREA_PICK)
                self._view.wid_vtkshow.interactor.SetInteractorStyle(self.style_band)
                self.style_band.update_cursor_shape()
            else:
                _btn.setChecked(False)

    def restore_data(self, undo=True):
        """
        撤销操作
        :param undo: True undo ， False redo
        :return:
        """
        # print('行:', sys._getframe().f_lineno, ' ', sys._getframe().f_code.co_name)

        # 只有默认模式才可以回退操作
        if app_manager.get_app_mode() == AppMode.DEFULT:
            if action_manager.restore(project_manager.enable_file, undo):
                project_manager.selected_list = []
                self._view.wid_vtkshow.win_render()
                self.set_dirty()

    def hover_single_point(self, obj, point_id):

        project_manager.on_selected = False
        project_manager.hover_file = None
        if obj is None:
            self.m_vtk_show.hover_single_point(None, -1)
            self._view.lbl_statusbar.setText('')  # 状态栏刷新
            self.disp_hover_file()
            return

        res = self.m_vtk_show.find_actor(obj)
        if res:
            file, act = res

            # 检查是否悬浮在选中点上
            if file == project_manager.enable_file and \
                    point_id in project_manager.selected_list:
                project_manager.on_selected = True

            self.m_vtk_show.hover_single_point(act, point_id)
            result = self.m_data.get_single_point_info(file, point_id)
            if result:
                jingwei, _arr = result
                filemsg = osp.relpath(file, self.last_dir) if self.last_dir is not None else osp.basename(file)

                msg = 'File=%s,  ID=%d, T=%d[%s]  ,V=%d  ,L=%d[%s]' % (
                    filemsg,
                    point_id,
                    _arr[ID_PROPERTY],
                    tra_property_dic.get(_arr[ID_PROPERTY], {}).get("des", '-'),
                    _arr[ID_SPEED],
                    _arr[ID_TURNLIGHT],
                    turn_light_dic.get(_arr[ID_TURNLIGHT],{}).get("des", '-')
                   )

                self._view.lbl_statusbar.setText(msg)
                self._view.wid_tabdata.row_highlight(file, point_id)
                project_manager.hover_file = file
                self.disp_hover_file()
                return
        self.m_vtk_show.hover_single_point(None, -1)
        self._view.lbl_statusbar.setText('')  # 状态栏刷新
        self.disp_hover_file()

    def hover_batch_points(self, obj, point_id):
        """
        悬浮在某一段的点
        :param obj:
        :param point_id:
        :return:
        """
        project_manager.on_selected = False
        project_manager.hover_file = None

        if obj is None:
            self.m_vtk_show.hover_batch_points(None, -1, -1)
            self._view.lbl_statusbar.setText('')  # 状态栏刷新
            self.disp_hover_file()
            return

        res = self.m_vtk_show.find_actor(obj)
        if res:
            file, act = res

            # 检查是否悬浮在选中点上
            if file == project_manager.enable_file and \
                    point_id in project_manager.selected_list:
                project_manager.on_selected = True

            # 通过id 查找同属性点区间
            ret = self.m_data.find_section_by_id(file, point_id)
            if not ret:
                print("没找到")
                return
            start, end = ret
            self.m_vtk_show.hover_batch_points(act, start, end)

            jingwei, _arr = self.m_data.get_single_point_info(file, point_id)
            filemsg = osp.relpath(file, self.last_dir) if self.last_dir is not None else osp.basename(file)
            msg = 'File=%s,  ID=[%d, %d) T=%d[%s]  ' % (
                filemsg,
                start,
                end,
                _arr[ID_PROPERTY],
                tra_property_dic.get(_arr[ID_PROPERTY], {}).get("des", '-')
            )
            self._view.lbl_statusbar.setText(msg)
            self._view.wid_tabdata.row_highlight(file, point_id)
            project_manager.hover_file = file
            self.disp_hover_file()
            return
        self.m_vtk_show.hover_batch_points(None, -1, -1)
        self._view.lbl_statusbar.setText('')  # 状态栏刷新
        self.disp_hover_file()

    def disp_hover_file(self):
        """显示悬浮"""
        # print("disp_hover_file  --" )
        self._con_file_list.set_hover_file(project_manager.hover_file)

    def select_seg_point(self, obj, point_id):
        """
        选中一段点，触发
        :param obj:
        :param point_id:
        :return:
        """
        if obj is None:
            return

        res = self.m_vtk_show.find_actor(obj)
        if res:
            file, act = res
            # 通过id 查找同属性点区间
            ret = self.m_data.find_section_by_id(file, point_id)
            if not ret:
                print("没找到")
                return

            # 先判断文件是不是使能，若不是，则自动切换过来
            if app_manager.get_app_mode() in [AppMode.ADD_POINT, AppMode.ADD_POINT_AUTO]:
                # 正常情况不会进入该分支
                return
            if project_manager.enable_file != file:
                self.set_file_enable(file)

            start, end = ret
            self.m_vtk_show.select_point_in_segment(start, end - 1)
            project_manager.selected_list = self.m_vtk_show.get_selected_list()

    def select_single_point(self, obj, point_id):
        # print('select_single_point')
        """单点选中"""
        if obj is None:
            return
        res = self.m_vtk_show.find_actor(obj)
        if res is None:
            return

        file, act = res

        # 判定是当期可选中的 轨迹，才可继续编辑
        if file == project_manager.enable_file:
            self.m_vtk_show.select_single_point(act, point_id)
            project_manager.selected_list = self.m_vtk_show.get_selected_list()
            # TODO 表格是否选中状态 scrollitem

    def tag_point(self, obj, point_id, pin=1):
        """
        打图钉
        :param obj: 对象actor
        :param point_id:
        :param pin: 1 2 图钉号
        :return:
        """
        if obj is None:
            return
        res = self.m_vtk_show.find_actor(obj)
        if res is None:
            return

        if app_manager.get_app_mode() in [AppMode.ADD_POINT_AUTO, AppMode.ADD_POINT]:
            self.infoMessage("段编辑", "处于插值状态，不能修改标签位置")
            return

        file, act = res

        if file == project_manager.enable_file and act == self.m_vtk_show.enable_actor:
            xyz, rgb = self.m_vtk_show.get_xyz_and_rgb(file, point_id)
            ret = self.m_seg.create_tag(pin, point_id, xyz, rgb)
            p1, p2, m = self.m_seg.get_tag_info()
            if ret is True:
                if m == SegMode.SEG_NORMAL or m == SegMode.SEG_CLOSE:
                    self.m_vtk_show.select_point_in_segment(p1, p2)
                    project_manager.selected_list = self.m_vtk_show.get_selected_list()

            # 刷新界面显示
            self.disp_seg_info()

        # TODO 选中段，是否更新表格中选中状态

    def new_point_by_click(self, pos):
        """
        单击新增点
        :param pos:
        :return:
        """

        # 获取图钉1的点的信息

        p1, _, _ = self.m_seg.get_tag_info()
        if p1 is None:
            self.errorMessage("增加点", "图钉id异常:{}".format(p1))
            return False

        _, rgb = self.m_vtk_show.enable_actor.pts.get_point(p1)
        self.m_vtk_show.new_point_by_click(pos, rgb)
        self.disp_add_point_info()

    def disp_add_point_info(self):
        """
        显示新增点的个数
        :return:
        """
        # print('disp_add_point_info ---- ')
        cnt = self.m_vtk_show.get_new_point_count()
        if app_manager.get_app_mode() == AppMode.ADD_POINT:
            self._view.wid_addpoint.lbl_add_point_count.setText("增加点数: %d" % cnt)
        elif app_manager.get_app_mode() == AppMode.ADD_POINT_AUTO:
            self._view.wid_addpoint.lbl_auto_add_point_num.setText("增加点数: %d" % cnt)
        else:
            self._view.wid_addpoint.lbl_add_point_count.setText("增加点数")
            self._view.wid_addpoint.lbl_auto_add_point_num.setText("增加点数")

    def disp_seg_info(self):
        p1, p2, m = self.m_seg.get_tag_info()
        # 刷新界面显示
        val1 = p1 if p1 is not None else -99
        val2 = p2 if p2 is not None else -99
        self._view.wid_segedit.show_seg_info(val1, val2, " :{}".format(m))

    def select_region_points(self, area_picker):
        """
        区域选取点
        :param area_picker:
        :return:
        """
        print('行:', sys._getframe().f_lineno, ' ', sys._getframe().f_code.co_name)

        self.m_vtk_show.select_region_points(area_picker)
        # TODO 这里可以考虑 区域选取时，是否消除图钉 -------
        self.set_seg_mode(SegMode.SEG_NONE)
        # ---------------------------------------------
        self._view.wid_vtkshow.win_render()
        project_manager.selected_list = self.m_vtk_show.get_selected_list()
        # TODO 刷新选中表格
        # selected = self.m_vtk_show.get_selected_list()

    def set_seg_mode(self, _mode):
        """
        段类型切换
        :param _mode:
        :return:
        """

        if app_manager.get_app_mode() in [AppMode.ADD_POINT, AppMode.ADD_POINT_AUTO]:
            self.infoMessage("段切换", "正在处于插值过程，不可切换段位置")
            return

        if _mode == SegMode.SEG_NONE:
            self.m_seg.cancel_tag()
            self.disp_seg_info()

        if self.m_vtk_show.enable_actor is None:
            return

        if _mode == SegMode.SEG_HEAD:
            xyz, rgb = self.m_vtk_show.enable_actor.pts.get_point(0)
            self.m_seg.set_tag_head_seg(xyz, rgb)
        elif _mode == SegMode.SEG_TAIL:
            xyz, rgb = self.m_vtk_show.enable_actor.pts.get_point(self.m_vtk_show.enable_actor.pts.count - 1)
            self.m_seg.set_tag_tail_seg(xyz, rgb)

        elif _mode == SegMode.SEG_CLOSE:
            try:
                p1, _, _ = self.m_seg.get_tag_info()
                if p1 is not None and 0 <= p1 < self.m_vtk_show.get_current_point_count() - 1:
                    xyz, rgb = self.m_vtk_show.enable_actor.pts.get_point(p1 + 1)
                    self.m_seg.set_tag_neighbor_seg(xyz, rgb)
            except Exception as e:
                print(e)

        self.disp_seg_info()

    def set_diswid_enable(self, enable=True):
        """
        打开、关闭测距控件
        :param enable:
        :return:
        """
        self.m_measure.set_enabled(enable)
        if not enable:
            for w in [self._view.wid_measuredis.edt_distance,
                      self._view.wid_measuredis.edt_point_coord1,
                      self._view.wid_measuredis.edt_point_coord2]:
                w.clear()

    def update_dis_msg(self, data):
        """
        sid 控件刷新时候触发更新  显示距离
        :param data:
        :return:
        """

        wp1, wp2 = np.round(data[0], 6), np.round(data[1], 6)
        self._view.wid_measuredis.edt_point_coord1.setText('{}, {}, {}'.format(wp1[0], wp1[1], wp1[2]))
        self._view.wid_measuredis.edt_point_coord2.setText('{}, {}, {}'.format(wp2[0], wp2[1], wp2[2]))
        wp1 = np.asarray(wp1)
        wp2 = np.asarray(wp2)
        _dis = np.linalg.norm(wp2 - wp1)
        self._view.wid_measuredis.edt_distance.setText('{} m'.format(np.round(_dis, 4)))

    def set_diswid_handle(self, handle):
        """
        设置dis wid  端点位置
        :param handle:
        :return:
        """
        if self.m_measure.get_enabled() == 0:
            return

        # 获取标签位置
        try:
            p1, p2, _ = self.m_seg.get_tag_info()
            idx = p1 if handle == 1 else p2
            if idx is not None and 0 <= idx <= self.m_vtk_show.enable_actor.pts.count - 1:
                xyz, _ = self.m_vtk_show.enable_actor.pts.get_point(idx)
                self.m_measure.set_distance_wid(handle, xyz)
        except Exception as e:
            print(e)

    def set_add_point_mode(self):
        """
        按钮 插入点位 的功能
        :return:
        """
        print('set_add_point_mode  = ', self._view.wid_addpoint.btn_add_point_enable.isChecked())

        _btn = self._view.wid_addpoint.btn_add_point_enable

        if not _btn.isChecked():
            self.cancel_add_point_mode(False)

        else:
            ret = True
            if app_manager.get_app_mode() != AppMode.DEFULT:
                self.errorMessage("插值功能", "应用模式非默认模式")
                ret = False

            if ret is True:
                _, _, m = self.m_seg.get_tag_info()
                if m != SegMode.SEG_CLOSE:
                    self.errorMessage("插值功能", "非邻段不能插值")
                    ret = False

            if ret is True:
                app_manager.set_app_mode(AppMode.ADD_POINT)
                self.style_parallel.update_cursor_shape()
                self._view.wid_vtkshow.win_render()
            else:
                _btn.setChecked(False)

    def set_add_auto_mode(self):
        """
        自动插值开关
        :return:
        """
        print('set_add_auto_mode  = ', self._view.wid_addpoint.btn_auto_add_enable.isChecked())

        _btn = self._view.wid_addpoint.btn_auto_add_enable

        if not _btn.isChecked():
            self.cancel_add_point_mode(False)

        else:
            ret = True
            if app_manager.get_app_mode() != AppMode.DEFULT:
                self.errorMessage("自动插值功能", "应用模式非默认模式")
                ret = False

            if ret is True:
                _, _, m = self.m_seg.get_tag_info()
                if m != SegMode.SEG_CLOSE:
                    self.errorMessage("自动插值功能", "非邻段不能插值")
                    ret = False

            if ret is True:
                app_manager.set_app_mode(AppMode.ADD_POINT_AUTO)
            else:
                _btn.setChecked(False)

        print('set_add_auto_mode  === ', app_manager.get_app_mode())

    def reset_add_point(self):
        """
        重置按钮—  重置增加点
        :return:
        """
        self.m_vtk_show.reset_new_actor()
        self.disp_add_point_info()

    def add_point_undo(self, undo=True):
        """增加点撤回操作"""
        if self.m_vtk_show.new_backup_restore(undo):
            self.disp_add_point_info()
            self._view.wid_vtkshow.win_render()

    def preview_auto_add_point(self):
        """
        预览 新增点
        :return:
        """
        if app_manager.get_app_mode() != AppMode.ADD_POINT_AUTO:
            return

        p1, p2, m = self.m_seg.get_tag_info()  # 必然是邻段，否则失败了
        if m != SegMode.SEG_CLOSE:
            self.errorMessage("自动插值", "当前不是邻段！")
            return

        # 获取图钉12位置
        xyz1, rgb1 = self.m_vtk_show.enable_actor.pts.get_point(p1)
        xyz2, rgb2 = self.m_vtk_show.enable_actor.pts.get_point(p2)

        # 获取间距
        step_value = self._view.wid_addpoint.spbx_space.value() * 0.01

        # 根据间距，计算点位--------
        dis_p1p2 = np.linalg.norm(np.array(xyz2) - np.array(xyz1))
        print('两点距离dis_p1p2 = ', dis_p1p2)
        self._view.wid_addpoint.lbl_distance.setText("两点距离%4.3f m" % dis_p1p2)

        if step_value > (0.5 * dis_p1p2):
            self.infoMessage("自动插值", "设定间距过大，请修改")
            return

        points = cal_between_two_point(xyz1, xyz2, step_value)
        rgbs = np.tile(rgb1, (points.shape[0], 1))  # 拉伸
        # print('=================================')
        # print(points)
        # print(rgbs)

        self.m_vtk_show.set_points_to_new_actor(points, rgbs)
        # 更新点个数
        self.disp_add_point_info()

        self._view.wid_vtkshow.win_render()

# 平滑处理  算法操作开始--------------------------------------------------------------------------------------------------
    def start_smooth_path(self):
        """
        # 路径平滑 预览
        # :return:
        # """

        start_idx = int(self._view.wid_smooth.lbl_start_id_.text())
        end_idx = int(self._view.wid_smooth.lbl_end_id_.text())

        count = end_idx - start_idx + 1
        selected_list = []
        for i in range(count):
            temp = start_idx + i
            selected_list.append(temp)

        data = self.m_data.get_data(project_manager.enable_file)
        if data is None:
            self.errorMessage("编辑数据", "获取数据失败file={}".format(project_manager.enable_file))
            return
        old_data = np.copy(data[selected_list, :])
        _, rgb = self.m_vtk_show.enable_actor.pts.get_point(selected_list[0])
        step_value = self._view.wid_smooth.spbx_space.value() * 0.01
        new_data_xy, new_data_yaw = all_smooth(old_data, step_value)
        self._view.wid_smooth.lbl_add_point_num.setText(str(len(new_data_xy)))
        points = np.zeros((len(new_data_xy), 3))

        for i in range(len(new_data_xy)):
            points[i][0] = new_data_xy[i][0]
            points[i][1] = new_data_xy[i][1]
        rgbs = np.tile(rgb, (points.shape[0], 1))
        self.m_vtk_show.set_points_to_new_actor(points, rgbs)
        self._view.wid_vtkshow.win_render()

    def finish_smooth_path(self):
        """
        # 要先delete之后在将平滑的点add到actor中
        # 路径平滑 结束
        # :return:
        # """

        start_idx = int(self._view.wid_smooth.lbl_start_id_.text())
        end_idx = int(self._view.wid_smooth.lbl_end_id_.text())
        if start_idx == 0:
            start_idx=start_idx+1
        if end_idx == start_idx:
            return

        count = end_idx - start_idx + 1
        rm_ids = []
        for i in range(count):
            temp = start_idx + i
            rm_ids.append(temp)

        data = self.m_data.get_data(project_manager.enable_file)
        if data is None:
            self.errorMessage("删除点", "获取数据失败 file={}".format(project_manager.enable_file))
            return

        rm_data = np.copy(data[rm_ids, :])
        ad = ActionData(ActionMode.SUB, rm_ids, rm_data)  # st 在当前索引开始增加。
        ad.set_other_data(file=project_manager.enable_file)
        action_manager.store(project_manager.enable_file, ad)

        ret = self.m_data.delete_data(project_manager.enable_file, rm_ids)
        if not ret:
            pass
        self.m_vtk_show.delete_selected_points()

        #  TODO 表格更新删除。
        self._view.wid_tabdata.del_row_table(project_manager.enable_file, rm_ids)

        app_manager.set_app_mode(AppMode.DEFULT)
        self.style_parallel.update_cursor_shape()
        self.disp_add_point_info()

        # 合并新增点
        points, colors = self.m_vtk_show.get_new_point_data()  # 获取的points 必须是深拷贝的，否则后边使用将会有问题

        ret = self.m_vtk_show.end_add_points(st=start_idx - 1, merge=True)
        self._view.wid_vtkshow.win_render()

        if not ret:
            self.errorMessage("新增点", "插值点失败")

        # 更新数组数据
        delta_data = self.merge_added_data(start_idx + 1, points)
        cnt = self.m_vtk_show.get_current_point_count()
        if not cnt:
            self.errorMessage("完成插值", "获取点数量失败")
            return

        self.m_seg.set_max_id(cnt - 1)
        self.disp_seg_info()

        # TODO 更新表格信息
        if delta_data is not None:
            self._view.wid_tabdata.add_row_table(project_manager.enable_file, start_idx + 1, delta_data)

        # 文件改变
        self.set_dirty()
        self._view.wid_smooth.lbl_start_id_.setText('None')
        self._view.wid_smooth.lbl_end_id_.setText('None')

    def d_v(self,data):
        lis=[]
        lis.append(0)
        for i in range(1,len(data)):
            lis.append(data[i]-data[i-1])
        return lis

    def get_first(self,lis):
        res=0
        for i ,item in enumerate(lis):
            if item>0:
                res=i
            break
        return res

    def pointdistance(self,x_r,y_r,x,y):
        dx=x_r-x
        dy=y_r-y
        return math.sqrt(dx*dx+dy*dy)

    def start_smooth_v(self):
        """
        # 速度平滑 处理
        :return:
        """
        selected_list = self.m_vtk_show.get_selected_list()
        if selected_list:
            data = self.m_data.get_data(project_manager.enable_file)
            if data is None:
                self.errorMessage("编辑数据", "获取数据失败file={}".format(project_manager.enable_file))
                return
            old_data = np.copy(data[selected_list, :])
            x=old_data[:,0]
            y=old_data[:,1]
            data_v=old_data[:,3]
            data_speed = list(np.array(data_v) / 3.6)
            lis = self.d_v(data_speed)
            index = self.get_first(lis)
            acc = 2
            dcc = 1.5
            while index < len(data_speed):
                distan = self.pointdistance(x[index], y[index], x[index - 1], y[index - 1])
                dv_square = data_speed[index] * data_speed[index] - data_speed[index - 1] * data_speed[index - 1]
                if dv_square / 2 / distan > 1.5:
                    data_speed[index] = math.sqrt(data_speed[index - 1] * data_speed[index - 1] + 2 * acc * distan)
                index = index + 1
            index_re = 0
            data_speed_re = data_speed[::-1]
            x_re = x[::-1]
            y_re = y[::-1]
            lis_re = self.d_v(data_speed_re)
            index_re = self.get_first(lis_re)
            while index_re < len(data_speed_re):  # 车速变大的开始位置
                # 计算跟上一个速度点的距离
                distan_re = self.pointdistance(x_re[index_re], y_re[index_re], x_re[index_re - 1], y_re[index_re - 1])
                dv_square_re = data_speed_re[index_re] * data_speed_re[index_re] - data_speed_re[index_re - 1] * \
                               data_speed_re[index_re - 1]
                if dv_square_re / 2 / distan_re > dcc:
                    data_speed_re[index_re] = math.sqrt(
                        data_speed_re[index_re - 1] * data_speed_re[index_re - 1] + 2 * dcc * distan_re)
                index_re = index_re + 1
                data_speed = []
                data_speed = data_speed_re[::-1]
            data_speed = list(np.array(data_speed) * 3.6)
            col_list=[3]*len(data_speed)
            self.m_data.change_data(project_manager.enable_file, selected_list, col_list, data_speed)

            new_data = np.copy(data[selected_list, :])
            ad = ActionData(ActionMode.EDIT, selected_list, [old_data, new_data])  # st 在当前索引开始增加。
            ad.set_other_data(file=project_manager.enable_file)
            action_manager.store(project_manager.enable_file, ad)
            self._view.wid_tabdata.edit_row_table(project_manager.enable_file, selected_list, new_data)
            self.set_dirty()

# 平滑处理  算法操作结束--------------------------------------------------------------------------------------------------

    def finish_add_point(self, auto=True):
        """
        完成 新增点
        :param auto:
        :return:
        """
        if auto is True:
            self._view.wid_addpoint.btn_auto_add_enable.setChecked(False)
        else:
            self._view.wid_addpoint.btn_add_point_enable.setChecked(False)

        app_manager.set_app_mode(AppMode.DEFULT)
        self.style_parallel.update_cursor_shape()
        self.disp_add_point_info()

        # 合并新增点
        points, colors = self.m_vtk_show.get_new_point_data()  # 获取的points 必须是深拷贝的，否则后边使用将会有问题
        start_idx, _, _ = self.m_seg.get_tag_info()

        ret = self.m_vtk_show.end_add_points(st=start_idx, merge=True)
        self._view.wid_vtkshow.win_render()

        if not ret:
            self.errorMessage("新增点", "插值点失败")

        # 更新数组数据
        # print('start_idx = ', start_idx)
        # print('points = ', points)
        delta_data = self.merge_added_data(start_idx + 1, points)  # 插值应该在标签pin1 的下一地方插入

        #  更新图钉 id信息
        _, pose2 = self.m_seg.get_tag_position()
        idx = self.m_vtk_show.get_index_by_pose(pose2)
        if not idx:
            self.errorMessage("完成插值", "计算idx失败")
            return
        self.m_seg.set_pin_id(2, idx)
        cnt = self.m_vtk_show.get_current_point_count()
        if not cnt:
            self.errorMessage("完成插值", "获取点数量失败")
            return

        self.m_seg.set_max_id(cnt - 1)
        self.disp_seg_info()

        # TODO 更新表格信息
        if delta_data is not None:
            self._view.wid_tabdata.add_row_table(project_manager.enable_file, start_idx + 1, delta_data)
            

        # 文件改变
        self.set_dirty()

    def merge_added_data(self, st, point_data):
        """
        合并数据到主数组
        :param st:  起点 index
        :param point_data:
        :return:
        """
        print('merge_added_data', st)

        if point_data.shape[0] == 0:
            return None
        try:
            if st == -1:
                pass
                # TODO 暂时没有支持首段 插入点， 如果支持了，则也可数组拼接
            else:
                _, paste_data = self.m_data.get_single_point_info(project_manager.enable_file, st)

                # 20221103 航向角计算 用的等差数列赋值
                _, paste_prev_data = self.m_data.get_single_point_info(project_manager.enable_file, st - 1)
                paste_data_yaw = paste_data[14]
                paste_prev_data_yaw = paste_prev_data[14]
                yaw = [0] * point_data.shape[0]
                dn = (paste_data_yaw - paste_prev_data_yaw) / (point_data.shape[0] + 1)
                for i in range(point_data.shape[0]):
                    yaw[i] = paste_prev_data_yaw + (i + 1) * dn

                if paste_data is None:
                    self.errorMessage("合并np数据", "获取st数据失败: {}".format(st))
                    return None

                paste_data = np.tile(paste_data, (point_data.shape[0], 1))  # 拉伸

                for i in range(point_data.shape[0]):
                    paste_data[i][0] = point_data[i][0]
                    paste_data[i][1] = point_data[i][1]
                    paste_data[i][14] = yaw[i]

                ad = ActionData(ActionMode.ADD, [st], paste_data)  # st 在当前索引开始增加。
                ad.set_other_data(file=project_manager.enable_file)
                action_manager.store(project_manager.enable_file, ad)

                self.m_data.insert_data(project_manager.enable_file, st, paste_data)
                return paste_data

        except Exception as e:
            self.errorMessage("合并np数据", "异常e={}".format(e))
            return None

    def cancel_add_point_mode(self, auto=True):
        """
        取消插值模式
        :param auto:
        :return:
        """
        app_manager.set_app_mode(AppMode.DEFULT)
        self.style_parallel.update_cursor_shape()
        self.disp_add_point_info()

        if auto is True:
            self._view.wid_addpoint.btn_auto_add_enable.setChecked(False)
            self._view.wid_addpoint.lbl_distance.setText('')
        else:
            self._view.wid_addpoint.btn_add_point_enable.setChecked(False)

        self.m_vtk_show.end_add_points(merge=False)
        self._view.wid_vtkshow.win_render()

        # TODO 更新按钮使能模式 , 灰色

    def move_point(self, delta_pos=None):
        """
        移动
        :param delta_pos:  x y 0
        :return:
        """
        # print('行:', sys._getframe().f_lineno, ' ', sys._getframe().f_code.co_name)
        # print(delta_pos)

        if delta_pos is None:
            print('行:', sys._getframe().f_lineno, ' ', sys._getframe().f_code.co_name)
            return

        try:
            if np.array_equal(np.array(delta_pos)[:2], np.array([0., 0.])):
                # print('行:', sys._getframe().f_lineno, ' ', sys._getframe().f_code.co_name)
                return
            # print("sele 个数 ： ", self.m_vtk_show._select_actor.pts.count)

            self.m_vtk_show.hover_single_point(None, -1)  # 先将悬浮点隐藏
            self.set_seg_mode(SegMode.SEG_NONE)  # 取消段

            # selected_list = self.m_vtk_show.get_selected_list()
            selected_list = project_manager.selected_list
            if len(selected_list) == 0:
                print('行:', sys._getframe().f_lineno, ' ', sys._getframe().f_code.co_name)
                return

            data = self.m_data.get_data(project_manager.enable_file)
            old_pos = data[selected_list, :2]
            new_pos = old_pos + np.array(delta_pos, dtype=float)[:2]  # 计算点
            new_pos = dim2_to_dim3(new_pos)
            self.edit_para_position(new_pos)

        except Exception as e:
            print(e)

    def rotate_point(self, delta_ang=None):
        # print('行:', sys._getframe().f_lineno, ' ', sys._getframe().f_code.co_name)
        # print(delta_ang)
        if delta_ang is None or delta_ang == 0:
            # print('行:', sys._getframe().f_lineno, ' ', sys._getframe().f_code.co_name)
            return
        try:

            # selected_list = self.m_vtk_show.get_selected_list()
            selected_list = project_manager.selected_list
            if len(selected_list) == 0:
                return

            self.m_vtk_show.hover_single_point(None, -1)  # 先将悬浮点隐藏
            self.set_seg_mode(SegMode.SEG_NONE)  # 取消段

            data = self.m_data.get_data(project_manager.enable_file)
            old_pos = data[selected_list, :2]
            cen = np.average(old_pos, axis=0)
            new_pos = rot_points_dim2(cen, old_pos, delta_ang)  # 计算旋转后的点
            new_pos = dim2_to_dim3(new_pos)
            # 更新数据
            self.edit_para_position(new_pos)

        except Exception as e:
            print(e)

    def edit_para_position(self, point_array):
        """
        编辑点位的  经纬度  =  xy
        :param point_array:  选中点的新的位置
        :return:
        """
        # selected_list = self.m_vtk_show.get_selected_list()
        selected_list = project_manager.selected_list
        if len(selected_list) != point_array.shape[0]:
            self.errorMessage("编辑数据点位", "个数不匹配:{}!={}".format(len(selected_list), point_array.shape[0]))
            return
        #  修改numpy 数据
        data = self.m_data.get_data(project_manager.enable_file)
        if data is None:
            self.errorMessage("编辑数据点位", "获取数据失败file={}".format(project_manager.enable_file))
            return

        old_data = np.copy(data[selected_list, :])

        for i in range(len(selected_list)):
            idx = selected_list[i]
            data[idx][0] = point_array[i][0]
            data[idx][1] = point_array[i][1]

        new_data = np.copy(data[selected_list, :])

        # 备份
        ad = ActionData(ActionMode.EDIT, selected_list, [old_data, new_data])  # st 在当前索引开始增加。
        ad.set_other_data(file=project_manager.enable_file)
        action_manager.try_store(project_manager.enable_file, ad)  # 过于频繁的修改同一批数据，用try_store

        # VTK显示
        self.m_vtk_show.edit_selected_position(point_array)
        self._view.wid_vtkshow.win_render()

        # TODO 表格改变数据.... 点位需要转化为经纬度？
        self._view.wid_tabdata.edit_row_table(project_manager.enable_file, selected_list, new_data)

        # 文件改变
        self.set_dirty()

    def edit_para_property(self, data):
        """
        编辑参数属性
        :param data:(控件id， 值)
        :return:
        """
        wid, val = data

        # print('edit_para_property')
        # print(wid.get_user_data(), '  ***   ', wid.get_label())
        # print("data = ", data, '   ', type(data))
        # print("wid = ",wid,'  ',type(wid),'  ',wid.get_user_data())
        # print("val = ",val, '  ', type(val))

        selected_list = self.m_vtk_show.get_selected_list()
        if selected_list:
            col = wid.get_user_data()
            if col == ID_PROPERTY :
                # 如果改动的是颜色属性项 ，修改颜色显示
                rgb = tra_property_dic.get(val, {}).get('rgb', (240, 240, 240))
                self.m_vtk_show.edit_selected_property(color=rgb)

            # 修改numpy数据-----------
            data = self.m_data.get_data(project_manager.enable_file)
            if data is None:
                self.errorMessage("编辑数据", "获取数据失败file={}".format(project_manager.enable_file))
                return

            old_data = np.copy(data[selected_list, :])

            if is_number(val):
                val = float(val)
                val = check_float_to_int(val)

            self.m_data.edit_element(project_manager.enable_file, selected_list, col, val)

            new_data = np.copy(data[selected_list, :])
            # print("old =  ", old_data)
            # print("new =  ", new_data)
            ad = ActionData(ActionMode.EDIT, selected_list, [old_data, new_data])  # st 在当前索引开始增加。
            ad.set_other_data(file=project_manager.enable_file)
            action_manager.store(project_manager.enable_file, ad)

            # TODO 修改表格数据
            self._view.wid_tabdata.edit_row_table(project_manager.enable_file, selected_list, new_data)

            # 文件改变
            self.set_dirty()

    def color_change_ok(self):
        """
        单独改变地图选中区域的颜色
        """
        selected_list = self.m_vtk_show.get_selected_list()
        if selected_list:
            idx=self._view.wid_additionwork.combobox.currentIndex()
            color_=self._view.wid_additionwork.colorlist[idx]
            self.m_vtk_show.edit_selected_property(color=color_)
        else:
            print('区域未选中')
            pass

    def color_change_esc(self):
        """
        取消单独改变的区域的颜色
        """
        selected_list = self.m_vtk_show.get_selected_list()
        array = self.m_data.get_data(project_manager.enable_file)
        rgb = ArrayDataManager.get_color_array(array)
        if selected_list:
            for i in range(self.m_vtk_show._select_actor.pts.count):
                p, _ = self.m_vtk_show._select_actor.pts.get_point(i)
                idx = self.m_vtk_show.enable_actor.pts.find_point(p)
                color=rgb[idx,:]
                if idx >= 0:
                    self.m_vtk_show._select_actor.pts.set_point(i, p, color)
                    self.m_vtk_show.enable_actor.pts.set_point(idx, p, color)
            self.m_vtk_show.enable_actor.pts.modify()
            self.m_vtk_show._select_actor.pts.modify()
            self.m_vtk_show.window.Render()
        else:
            print('区域未选中')
            pass


    def show_instructions_info(self, flag):

        if flag == 1:
            msg = shortcut_explain
            QMessageBox.information(self._view, u'简要使用说明', msg)

        else:
            msg = software_msg
            QMessageBox.information(self._view, u'软件信息', msg)
            # self.infoMessage(u'软件信息', msg)


    def errorMessage(self, title, message):
        return QtWidgets.QMessageBox.critical(
            self._view, title, "<p><b>%s</b></p>%s" % (title, message)
        )

    def infoMessage(self, title, message):
        return QtWidgets.QMessageBox.information(
            self._view, title, "<p><b>%s</b></p>%s" % (title, message)
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("{}-{}".format(__appname__, __version__))
    app.setWindowIcon(QIcon("wanji_logo64.ico"))

    c = MainController()
    c.show()

    sys.exit(app.exec_())
