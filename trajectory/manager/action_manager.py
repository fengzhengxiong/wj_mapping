#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 记录增删改动作流程
import copy
import sys
from threading import Lock
from trajectory.local_utils.myqueue import MyQueue
from .common_mode import ActionMode
import time

# ActionData 使用规则：
# 数据增加  action=ActionMode.ADD，ids 保存单个索引，记录在哪里加入的， data为增加的数据
# 数据删除  action=ActionMode.SUB， ids 记录删除的数据索引， data为被删除数据， 必须保证ids 和 data 长度一致
# 数据修改  action=ActionMode.EDIT，ids 记录修改数据的索引， data = [ olddata, newdata] ， 分别记录修改之前数据和修改之后的数据， 索引与ids长度保持一致


class ActionData(object):
    def __init__(self, action=ActionMode.ADD, ids=list(), data=None):
        self.action = action    # 动作（增加删除编辑）
        self.ids = ids                  # 索引
        self.data = data                # 增加的数据，删除的数据，编辑的数据
        self.timestamp = time.time()    # 记录当前时间戳
        self._other_data = {}            # 其他数据需要记录、预留的

    def set_other_data(self, **kwargs):
        self._other_data = copy.deepcopy(kwargs)
        # print('other_data =  ',self.other_data)

    def get_other_data(self):
        return self._other_data


class ActionManager(object):
    """
    每个文件单独设计一个队列管理操作动作，字典记录
    """
    queue_size = 40  # 队列长度
    time_threshold = 0.5  # 时间阈值

    def __init__(self):
        self._dic_backup = {}  # key :filename, value 队列 MyQueue
        self._lst_resore_callback = []  # 各个模块，撤回功能回调函数
        self.__mutex = Lock()

    def register(self, func):
        """
        注册函数
        :param func: func(action,undo) 参数为两个， 动作及回退情况
        :return:
        """
        self.__mutex.acquire()
        if func not in self._lst_resore_callback:
            self._lst_resore_callback.append(func)
        self.__mutex.release()

    def unregister(self, func):
        self.__mutex.acquire()
        if func in self._lst_resore_callback:
            self._lst_resore_callback.remove(func)
        self.__mutex.release()

    def new_queue(self, file, data):
        """
        初始创建队列
        :param file:
        :param data:
        :return:
        """
        self.destroy_queue(file)
        try:
            _data = copy.deepcopy(data)  # 深拷贝，防止被改动后意外掉。
        except Exception as e:
            _data = data

        _q = MyQueue(max_size=self.queue_size)
        _a = ActionData(ActionMode.ADD, ids=[0], data=_data)

        _q.put(_a)  # 队列设计的第一个缓存是基础数据，最终可回退的结果。

        self._dic_backup[file] = _q

    def destroy_queue(self, file):
        """
        销毁队列
        :param file:
        :return:
        """
        try:
            if file in self._dic_backup:
                q = self._dic_backup[file]
                q.reset()
                del self._dic_backup[file]
        except Exception as e:
            print('行:', sys._getframe().f_lineno, ' ', sys._getframe().f_code.co_name)
            print(e)

    def store(self, file, obj_action):
        self.__mutex.acquire()
        q = self._dic_backup.get(file, None)
        if q:
            q.put(obj_action)
            # print('行:', sys._getframe().f_lineno, ' ', sys._getframe().f_code.co_name)
            # print(obj_action.action)
            # print(obj_action.data[:, :3])
            # print(obj_action.ids)
            # print(obj_action.get_other_data())

        self.__mutex.release()

    def try_store(self, file, obj_action):
        """
        尝试存储， 替换当前位置堆栈，节约不必要存储
        :param file:
        :param obj_action:
        :return:
        """

        self.__mutex.acquire()
        q = self._dic_backup.get(file, None)
        if q:
            if not isinstance(q, MyQueue):
                return
            cur_action = q.getThis(move=0, def_ret=None)
            if self.is_replaceable(cur_action, obj_action):
                obj_action.data[0] = cur_action.data[0]
                q.setThis(obj_action)
                # print('try_store  1111111111 = ', q.index)
            else:
                q.put(obj_action)
                # print('try_store  2222222222 = ', q.index)
        self.__mutex.release()

    def is_replaceable(self, old, new):
        """
        检查是否可替换
        :param old:
        :param new:
        :return:
        """
        import numpy as np
        if not (isinstance(old, ActionData) and isinstance(new, ActionData)):
            return False

        if not (old.action == new.action == ActionMode.EDIT):
            # print('is_replaceable  11111111')
            return False
        if not np.array_equal(np.array(old.ids), np.array(new.ids)):
            # print('is_replaceable  2222222222')
            return False
        if old.get_other_data() != new.get_other_data():
            # print('is_replaceable  3333333333333')
            return False
        if new.timestamp - old.timestamp > self.time_threshold:
            # print('is_replaceable  4444444444444')
            return False

        return True



    def restore(self, file, undo=True):
        """

        :param file:
        :param undo:
        :return: 执行撤回成功 返回True  无效则返回False
        """
        self.__mutex.acquire()
        ret = True
        q = self._dic_backup.get(file, None)
        # if q:
        #     print('队列index = ', q.index)

        # 队列存储是ActionData类 ，undo 需要获取当前在前移动指针用getThis(-1) ，redo 需要获取当前下一项数据，固要用getNext
        if q and self.is_queue_restorable(q, undo):
            obj_action = q.getThis(-1) if undo else q.getNext()  # res ActionData类
            # print('行:', sys._getframe().f_lineno, ' ', sys._getframe().f_code.co_name)
            # print(obj_action.action)
            # print(obj_action.data[:, :3])
            # print(obj_action.ids)
            # print(obj_action.get_other_data())

            # 回调各个模块的restore
            for func in self._lst_resore_callback:
                func(obj_action, undo)

            ret = True
        else:
            ret = False
        self.__mutex.release()
        return ret

    def is_restorable(self, file, undo=True):
        """ 可回退？  """
        q = self._dic_backup.get(file, None)
        if not q:
            return False
        return self.is_queue_restorable(q, undo)

    def is_queue_restorable(self, queue, undo=True):
        return queue.isGetLast() if undo else queue.isGetNext()

    def file_check(self, file):
        return file in self._dic_backup

    def reset(self):
        for key in self._dic_backup.keys():
            self.destroy_queue(key)
        self._dic_backup.clear()


class Singleton(ActionManager):
    def foo(self):
        pass


action_manager = Singleton()  # 单例


#
# def main():
#     import numpy as np
#
#     testdata = np.arange(1, 10).reshape((-1, 3))
#     print(testdata)
#     action_manager.new_queue('file', testdata)
#     #
#     testdata= np.insert(testdata, 1, np.array([[1,2,6], [11,22,33]]), axis=0)
#     print(testdata)
#     a = ActionData(ActionMode.ADD, [1], data=np.array([[1, 2, 6], [11,22,33]]))
#     action_manager.store('file', a)
#
#     action_manager.restore('file', True)
#
#
#
#
# if __name__ == '__main__':
#     main()