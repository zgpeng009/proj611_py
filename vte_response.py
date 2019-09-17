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
from vte_static import STATIC

import matplotlib.pyplot as plt
from pylab import mpl

mpl.rcParams['font.sans-serif'] = ['SimHei']
mpl.rcParams['axes.unicode_minus'] = False


class RESPONSE(BDF):
    def __init__(self):
        super(RESPONSE, self).__init__()

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

    def resp_plot(self, node, output):
        random_f06 = output.replace('f06', 'pch')
        _f = open(random_f06, 'r')
        lines = _f.readlines()
        _f.close()
        for i in range(len(lines)):
            if lines[i].startswith('$ACCELERATION'):
                if lines[i + 3].split()[3].strip() == node:
                    j = i + 4
                    resp = []
                    while '$' not in lines[j]:
                        for ii in range(4):
                            if ii == 0:
                                resp.append(float(lines[ii + j][0:17]))
                                for jj in range(3):
                                    resp.append(float(lines[ii + j][(jj + 1) * 18:(jj + 2) * 18]))
                            else:
                                for jj in range(3):
                                    resp.append(float(lines[ii + j][(jj + 1) * 18:(jj + 2) * 18]))
                        j += 4
        _a = np.ones(13)
        try:
            _a = np.array(resp)
        except:
            Exception('resp error')
        resp_np = _a.reshape((int(len(_a) / 13), 13))

        fig = plt.figure(u'加速度响应', facecolor='lightgrey')
        resp_plot = fig.add_subplot(111)
        x_axis = resp_np[:, 0]
        resp_plot.plot(x_axis, resp_np[:, 1], color='r', label=u'X向加速度响应')
        resp_plot.plot(x_axis, resp_np[:, 2], color='b', label=u'Y向加速度响应')
        resp_plot.plot(x_axis, resp_np[:, 3], color='g', label=u'Z向加速度响应')
        resp_plot.legend()
        resp_plot.grid()
        resp_plot.set_xlabel(u'频率（Hz）')
        resp_plot.set_ylabel(u'加速度响应（m/s-2）')
        plt.show()


def main(sys_argv):
    # 参数1（函数识别字符串）、参数2（bdf文件路径）、参数3（nastran.exe路径）、参数2（计算结果输出路径）
    if sys_argv[1] == 'running':
        re = RESPONSE()
        re.run(sys_argv[2], sys_argv[3], sys_argv[4])

    # 参数1（函数识别字符串）、参数2（输出曲线的Point）、参数3（f06文件路径）
    elif sys_argv[1] == 'resp':
        re = RESPONSE()
        re.resp_plot(sys_argv[2], sys_argv[3])

    elif sys_argv[1] == 'correlation':
        data1 = [1.023694, 6.933699, 13.58325, 20.25471, 26.76528]
        data2 = [0.523694, 8.233699, 11.68325, 21.55471, 23.86528]
        my_data_x = [1, 2, 3, 4, 5]
        names = ['散点图', '虚拟试验位移', '物理试验位移', '折线图', '加载级', '位移', '虚拟试验', '物理试验']

        static_nast = STATIC()
        if my_data_x:
            static_nast.create_correlation_plot(data1, data2, my_data_x, names)
        else:
            raise RuntimeError('loadInfo txt file error')


def test():
    fun_str = 'correlation'
    with open(r'vte_response.bat', 'r') as f:
        sys_test_lines = f.readlines()
        for line in sys_test_lines:
            if '%py% %input% ' + fun_str in line:
                sys_list = line.split()
                sys_list.pop(0)
                return sys_list


if __name__ == '__main__':
    try:
        # main(sys.argv)
        main(test())
    except:
        traceback.print_exc()
        wnd = tkinter.Tk()
        wnd.withdraw()
        messagebox.showinfo('ERROR', str(sys.exc_info()[1]))
        for line in sys.argv:
            print('--->' + line)
        os.system('pause')
