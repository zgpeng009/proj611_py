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


class TEMPLOAD(BDF):
    def __init__(self):
        super(TEMPLOAD, self).__init__()

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
        temp = TEMPLOAD()
        temp.run(sys_argv[2], sys_argv[3], sys_argv[4])


if __name__ == '__main__':
    try:
        main(sys.argv)
        # main([line.split()[1:] for line in
        #       open('E:\work\\611\\vte\\proj611\\proj611_py\\vte_tempload.bat', 'r').readlines()
        #       if ('running' in line and '%py% %input% ' in line)][0])
    except:
        traceback.print_exc()
        wnd = tkinter.Tk()
        wnd.withdraw()
        messagebox.showinfo('ERROR', str(sys.exc_info()[1]))
        for line in sys.argv:
            print('--->' + line)
        os.system('pause')
