#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import matplotlib
import matplotlib.pyplot as plt

current_dir_name = os.path.abspath(__file__)
current_dir = os.path.dirname(current_dir_name)
myfont_dir = os.path.join(current_dir, 'font', 'simhei.ttf')
myfont = matplotlib.font_manager.FontProperties(fname=myfont_dir)
# plt.rcParams['font.sans-serif'] = ['SimHei']

names = ['看看', '', '', '', '', '', '', '']
names = [unicode(item, 'utf-8') for item in names]
data1 = []
data2 = []
data_x = []

fig = plt.figure(num=u'相关性分析', figsize=(8, 8), facecolor='lightgrey')
ax1 = fig.add_subplot(211)
ax2 = fig.add_subplot(212)
if len(names) == 8:
    ax1.grid(True)
    ax1.set_title(names[0], fontsize=15, fontproperties=myfont)
    ax1.set_xlabel(names[1], fontsize=12)
    ax1.set_ylabel(names[2], fontsize=12)
    ax1.plot(data1, data1, 'k--', linewidth=0.7)
    ax1.scatter(data1, data2, s=40, c='', marker='o', edgecolor='c')
    ax2.grid(True)
    ax2.set_title(names[3], fontsize=15)
    ax2.set_xlabel(names[4], fontsize=12)
    ax2.set_ylabel(names[5], fontsize=12)
    ax2.plot(data_x, data1, c='r', marker='^', label=names[6])
    ax2.plot(data_x, data2, c='b', marker='o', label=names[7])
    ax2.legend(loc='upper left')
fig.tight_layout(h_pad=1.0)
plt.show()
