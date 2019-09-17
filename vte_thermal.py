#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import psutil
import numpy as np

import traceback
import tkinter
from tkinter import messagebox

from pyNastran.bdf.bdf import BDF

import matplotlib.pyplot as plt
from pylab import mpl

mpl.rcParams['font.sans-serif'] = ['SimHei']
mpl.rcParams['axes.unicode_minus'] = False


class THERMAL(BDF):
    def __init__(self):
        super(THERMAL, self).__init__()

    def nastran_psutil(self):
        while True:
            p_name = []
            p_id = psutil.pids()
            for p in p_id:
                try:
                    psn = psutil.Process(p).name()
                except:
                    pass
                else:
                    p_name.append(psn)
            if 'nastran.exe' not in p_name:
                break

    def run(self, bdf_input, nastran, f06_output):
        if os.path.exists(bdf_input):
            os.system(nastran + ' scr=yes delete=f04,log old=no out=%s %s' % (f06_output, bdf_input))
        else:
            raise RuntimeError(u'%s下bdf不存在' % (bdf_input))
        self.nastran_psutil()


def main(sys_argv):
    # 参数1（函数识别字符串）、参数2（bdf文件路径）、参数3（nastran.exe路径）、参数2（计算结果输出路径）
    if sys_argv[1] == 'running':
        therm = THERMAL()
        therm.run(sys_argv[2], sys_argv[3], sys_argv[4])


def test():
    fun_str = 'running'
    with open('E:\work\\611\\vte\proj611\\proj611_py\\vte_thermal.bat', 'r') as f:
        sys_test_lines = f.readlines()
        for line in sys_test_lines:
            if '%py% %input% ' + fun_str in line:
                sys_list = line.split()
                sys_list.pop(0)
                return sys_list


if __name__ == '__main__':
    try:
        main(sys.argv)
        # main(test())
    except:
        traceback.print_exc()
        wnd = tkinter.Tk()
        wnd.withdraw()
        messagebox.showinfo('ERROR', str(sys.exc_info()[1]))
        for line in sys.argv:
            print('--->' + line)
        os.system('pause')
