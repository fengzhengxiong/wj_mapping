#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) <2022-5> An-Haiyang
# 文件读写管理

import sys
import os
import os.path as osp
import json
import yaml
import codecs
import re
import csv
import ast
import numpy as np


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def is_int_number(s):
    """ 判断字符串是否为整数，排除小数点 """
    try:
        return (float(s).is_integer() and s.count('.') == 0)
    except ValueError:
        return False


def natural_sort(list, key=lambda s: s):
    """
    Sort the list into natural alphanumeric order.
    """

    def get_alphanum_key_func(key):
        convert = lambda text: int(text) if text.isdigit() else text
        return lambda s: [convert(c) for c in re.split('([0-9]+)', key(s))]

    sort_key = get_alphanum_key_func(key)
    list.sort(key=sort_key)


def save_json_file(filename, dic, indent=None, def_ret=False):
    """
    写json文件
    :return: 成功 True， 失败 def_ret
    """
    try:
        with codecs.open(filename, 'w', encoding='utf-8') as f:
            # json.dump(data, f, ensure_ascii=False, indent=2)
            text = json.dumps(dic, ensure_ascii=False, indent=indent)
            f.write(text)
            f.close()
            del text
            return True
    except Exception as e:
        err_msg = 'In Func [{}], err is {}'.format(sys._getframe().f_code.co_name, e)
        print(err_msg)
        return def_ret


def read_json_file(filename, def_ret=None):
    """
    读json文件
    :return: 成功 字典， 失败 def_ret
    """

    def check_file(filename):
        extensions = ['json']
        return True if (filename and osp.isfile(filename) and filename.lower().endswith(tuple(extensions))) else False

    try:
        if not check_file(filename):
            return def_ret
        with codecs.open(filename, 'r', encoding='utf-8') as f:
            text = f.read()
            ret = json.loads(text) if text else {}
            f.close()
            del text
            return ret
    except Exception as e:
        err_msg = 'In Func [{}], err is {}'.format(sys._getframe().f_code.co_name, e)
        print(err_msg)
        return def_ret


def read_yaml_file(filename, def_ret=None):
    """
    读yaml文件
    :return: 成功 True， 失败 def_ret
    """

    def check_file(filename):
        extensions = ['.yaml', ',yml']
        return True \
            if (filename and osp.isfile(filename) and filename.lower().endswith(tuple(extensions))) \
            else False

    try:
        if not check_file(filename):
            return def_ret
        with codecs.open(filename, 'r', encoding='utf-8') as f:
            text = f.read()
            ret = yaml.safe_load(text) if text else {}
            f.close()
            del text
            return ret
    except Exception as e:
        err_msg = 'In Func [{}], err is {}'.format(sys._getframe().f_code.co_name, e)
        print(err_msg)
        return def_ret


def save_yaml_file(filename, data, def_ret=None):
    """
    写yml文件
    :return: 成功 True， 失败 def_ret
    """
    try:
        with codecs.open(filename, 'w', encoding='utf-8') as f:
            yaml.safe_dump(data, f, allow_unicode=True)
            return True
    except Exception as e:
        err_msg = 'In Func [{}], err is {}'.format(sys._getframe().f_code.co_name, e)
        print(err_msg)
        return def_ret


def scan_files(dirpath, ext=None, def_ret=None):
    """
    扫描当前文件夹文件
    """
    dirpath = dirpath if osp.isdir(dirpath) else osp.dirname(dirpath)
    if not osp.exists(dirpath):
        return def_ret
    result = []
    try:
        if ext is None:
            for file in os.listdir(dirpath):
                result.append(osp.join(dirpath, file))
        else:
            extensions = [ext] if type(ext) == str else ext
            for file in os.listdir(dirpath):
                result += [osp.join(dirpath, file)] if file.lower().endswith(tuple(extensions)) else []

        natural_sort(result, key=lambda x: x.lower())
        return result
    except Exception as e:
        err_msg = 'In Func [{}], err is {}'.format(sys._getframe().f_code.co_name, e)
        print(err_msg)
        return def_ret


def scan_all_files(dirpath, ext=None, def_ret=None):
    """
    扫描当前文件夹下所有文件，包含子文件夹
    """
    dirpath = dirpath if osp.isdir(dirpath) else osp.dirname(dirpath)
    if not osp.exists(dirpath):
        return def_ret
    result = []
    try:
        if ext is None:
            for root, dirs, files in os.walk(dirpath):
                # root 表示当前正在访问的文件夹路径
                # dirs 表示该文件夹下的子目录名list
                # files 表示该文件夹下的文件list
                for f in files:
                    result.append(osp.join(root, f))
        else:
            extensions = [ext] if type(ext) == str else ext
            for root, dirs, files in os.walk(dirpath):
                for f in files:
                    if f.lower().endswith(tuple(extensions)):
                        result.append(osp.join(root, f))
        # natural_sort(result, key=lambda x: x.lower())
        return result
    except Exception as e:
        err_msg = 'In Func [{}], err is {}'.format(sys._getframe().f_code.co_name, e)
        print(err_msg)
        return def_ret


def read_file(path, def_ret=None):
    if not (osp.exists(path) and osp.isfile(path)):
        return def_ret

    try:
        with open(path, 'r', encoding='utf-8') as f:
            text = f.read()
            return text
    except Exception as e:
        err_msg = 'In Func [{}], err is {}'.format(sys._getframe().f_code.co_name, e)
        print(err_msg)
        return def_ret


def write_file(path, text, def_ret=None):
    if not osp.exists(osp.dirname(path)):
        os.makedirs(osp.dirname(path))
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(text)
            f.close()
            return True
    except Exception as e:
        err_msg = 'In Func [{}], err is {}'.format(sys._getframe().f_code.co_name, e)
        print(err_msg)
        return def_ret


def read_csv_file(filename, def_ret=None):
    def check_file(filename):
        extensions = ['.csv']
        return True \
            if (filename and osp.isfile(filename) and filename.lower().endswith(tuple(extensions))) \
            else False

    result = []
    try:
        if not check_file(filename):
            return def_ret
        with open(filename, 'r', encoding='utf-8') as f:
            datas = csv.reader(f)
            for data in datas:
                # tmp = [ast.literal_eval(a) for a in data]  # 对于中文会报错
                tmp = data[:]
                for i in range(len(tmp)):
                    a = tmp[i]
                    if is_int_number(a):
                        tmp[i] = int(a)
                    elif is_number(a):
                        tmp[i] = float(a)
                    else:
                        pass
                # print(tmp)
                result.append(tmp)
            f.close()
            del datas
            return result
    except Exception as e:
        err_msg = 'In Func [{}], err is {}'.format(sys._getframe().f_code.co_name, e)
        print(err_msg)
        return def_ret


def save_csv_file(filename, data, def_ret=None):
    """
    写csv文件, data是list 二维格式
    :return: 成功 True， 失败 def_ret
    """
    try:
        with open(filename, 'w', encoding='utf-8', newline='') as f:
            w = csv.writer(f)
            for d in data:
                w.writerow(d)
            f.close()
            return True
    except Exception as e:
        err_msg = 'In Func [{}], err is {}'.format(sys._getframe().f_code.co_name, e)
        print(err_msg)
        return def_ret

    # 用下面方法也是可以的
    # res = []
    # for d in data:
    #     for a in d:
    #         d[d.index(a)] = str(a)
    #     res.append(','.join(d))
    # text = '\n'.join(res)
    # write_file(filename, text)
