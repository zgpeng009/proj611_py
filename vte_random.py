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


class RANDOM(BDF):
    def __init__(self):
        super(RANDOM, self).__init__()

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

    def rand_plot(self, node, f06_output):
        f = open(f06_output, 'r')
        random_lines = f.readlines()
        f.close()

        for line in random_lines:
            if 'FATAL' in line.split():
                raise RuntimeError(u'f06文件%s计算存在FATAL' % (f06_output))

        acce_psd_axis, acce_dpsd_x, acce_dpsd_y, acce_dpsd_z = [], [], [], []
        for i in range(len(random_lines)):
            if 'POINT-ID =' in random_lines[i]:
                if random_lines[i].split('=')[1].strip() == node:
                    if 'A C C E L E R A T I O N    V E C T O R' in random_lines[i + 1]:
                        if 'POWER SPECTRAL DENSITY FUNCTION' in random_lines[i + 2]:
                            j = i + 5
                            while 'PAGE' not in random_lines[j]:
                                random_lines_split = random_lines[j].split()
                                acce_psd_axis.append(float(random_lines_split[0]))
                                acce_dpsd_x.append(float(random_lines_split[2]))
                                acce_dpsd_y.append(float(random_lines_split[3]))
                                acce_dpsd_z.append(float(random_lines_split[4]))
                                j += 1

        fig = plt.figure(u'随机振动', facecolor='lightgrey')
        acce_psd_plot = fig.add_subplot(111)
        acce_psd_plot.plot(acce_psd_axis, acce_dpsd_x, color='r', label=u'X向加速度功率谱密度')
        acce_psd_plot.plot(acce_psd_axis, acce_dpsd_y, color='b', label=u'Y向加速度功率谱密度')
        acce_psd_plot.plot(acce_psd_axis, acce_dpsd_z, color='g', label=u'Z向加速度功率谱密度')
        acce_psd_plot.legend()
        acce_psd_plot.grid()
        acce_psd_plot.set_xlabel(u'频率（Hz）')
        acce_psd_plot.set_ylabel(u'加速度功率谱密度（mm2/Hz）')
        plt.show()


def main(sys_argv):
    # 参数1（函数识别字符串）、参数2（bdf文件路径）、参数3（nastran.exe路径）、参数2（计算结果输出路径）
    if sys_argv[1] == 'running':
        rand = RANDOM()
        rand.run(sys_argv[2], sys_argv[3], sys_argv[4])

    # 参数1（函数识别字符串）、参数2（输出曲线的Point）、参数3（f06文件路径）
    elif sys_argv[1] == 'rand':
        rand = RANDOM()
        rand.rand_plot(sys_argv[2], sys_argv[3])


def test():
    fun_str = 'rand'
    with open('E:\\work\\611\\vte\\proj611\\proj611_py\\vte_random.bat', 'r') as f:
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
