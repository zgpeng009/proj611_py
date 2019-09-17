#!/usr/bin/env python
# -*- coding: utf-8 -*-

from matplotlib.ticker import FormatStrFormatter
from matplotlib import rc
import sys
import os
import commands
import traceback
import shutil
from time import sleep
import psutil
from six import string_types, iteritems
import time
import operator
from operator import attrgetter, itemgetter

from pyNastran.bdf.bdf import BDF
import tkinter
from tkinter import messagebox
import numpy as np
from numpy import array, cov, corrcoef
import matplotlib.pyplot as plt
from pylab import mpl

mpl.rcParams['font.sans-serif'] = ['SimHei']
mpl.rcParams['axes.unicode_minus'] = False


class STATIC(BDF):
    def __init__(self):
        BDF.__init__(self)
        self.displacement_increment = np.array([0.0, 0.0, 0.0])
        self.load_node_xyz = np.array([0.0, 0.0, 0.0])
        self.load_node_cos = np.array([0.0, 0.0, 0.0])
        self.re_new_bdf = []
        self.grid_force_dict = {}
        self.bdf_data = []

        self.dir = ''
        self.name = ''
        self.bdf_name = ''
        self.f06_name = ''

        self.deformed_displacement = {}
        self.judge_elem_list = []
        self.judge_node_list = []
        self.bdf_node_sum = []
        self.force_sum = np.array([0.0, 0.0, 0.0])

        self.a1 = []
        self.a2 = []
        self.force_loc = []

        self.new_node_xyz = {}
        self.node_increment_xyz = {}

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

    def run_nast_increment(self, force_file, input_bdf, output_dir, nastran):
        # get force
        force = []
        _dict = {}
        try:
            _f = open(force_file, 'r')
            lines = _f.readlines()
            _f.close()
        except:
            raise RuntimeError('no force file')

        new_lines = lines[:]
        line = lines.pop(0)
        _list = line.split(',')
        min_num = int((len(_list) - 1) / 2)
        for line in lines:
            _list = line.split(',')
            min_num = min(min_num, int((len(_list) - 1) / 2))

        for i in range(min_num):
            _dict = {}
            for line in new_lines:
                _list = line.split(',')
                _dict[int(_list[0])] = float(_list[2 * i + 2])
            _dict["stage"] = [i, int(_list[2 * i + 1])]
            force.append(_dict)

        # run many steps
        if force != []:
            for i in range(len(force)):
                bdf_list = []
                force_load = force[i]
                my_stage = int(force_load["stage"][0]) + 1
                my_stage = '{:0>2d}'.format(my_stage)

                run_output_dir = output_dir.rstrip('\\').rstrip('/')
                run_f06_name = os.path.basename(input_bdf).split('.')[
                                   0] + '_' + str(my_stage) + '.f06'
                run_f06 = os.path.join(run_output_dir, run_f06_name)

                run_input_dir = os.path.dirname(input_bdf)
                run_bdf_name = os.path.basename(input_bdf).split('.')[
                                   0] + '_' + str(my_stage) + '.bdf'
                run_bdf = os.path.join(run_output_dir, run_bdf_name)

                model = BDF()
                model.read_bdf(input_bdf)

                loads_card_dict = model.loads
                spc1_card_dict = model.spcs

                for j in spc1_card_dict:
                    for spc_card in spc1_card_dict[j]:
                        if type(spc_card).__name__ == 'SPC1':
                            spc_id = spc_card.conid
                            break
                    break

                for i in loads_card_dict:
                    for force_card in loads_card_dict[i]:
                        if type(force_card).__name__ == 'FORCE' and force_card.node in force_load.keys():
                            force_xyz = force_card.xyz
                            if np.linalg.norm(force_xyz) != 0.0:
                                force_cos = force_load[force_card.node] / np.linalg.norm(force_xyz) * force_xyz
                            else:
                                raise Exception('Force value is 0.0, bdf file can not run')
                            force_card.xyz = force_cos
                            force_xyz_1 = np.abs(force_xyz)
                            max_loc = np.where(force_xyz_1 == max(force_xyz_1))[0][0]
                            if 'spc_id' in vars():
                                model.add_card(['SPC1', spc_id, int('123'.replace(str(max_loc + 1), '')),
                                                force_card.node], 'SPC1')
                            else:
                                raise Exception('SPC1 card is not exist')
                model.write_bdf(run_bdf)

                os.system(nastran + ' scr=yes delete=f04,log old=no out=%s %s' % (run_output_dir, run_bdf))
                self.nastran_psutil()

                if os.path.exists(run_f06):
                    _f = open(run_f06, 'r')
                    lines = _f.readlines()
                    _f.close()
                    for i in range(len(lines)):
                        _line = lines[i].split()
                        if 'FATAL' in _line:
                            raise Exception('F06 File Error : ' + '\n' + str(lines[i]) + str(lines[i + 1]))

    def get_section_list(self, begin_loc, end_loc, normal_vector, point_number):
        section_d = (end_loc - begin_loc) / point_number
        judge_elem_list = [[] for m in range(point_number + 1)]
        judge_node_list_1 = [[] for m in range(point_number + 1)]
        judge_node_list = [[] for m in range(point_number + 1)]

        for i in range(point_number + 1):
            ori = begin_loc + section_d * np.array([i, i, i])
            for line in self.elements:
                if self.elements[line].type == u'CQUAD4':
                    node = [0, 0, 0, 0]
                    for j, nid in enumerate(self.elements[line].node_ids):
                        node_j = np.inner(
                            normal_vector, (self.nodes[nid].xyz - ori))
                        node[j] = round(node_j, 0)
                    if node[0] > 0.0:
                        if node[1] > 0.0:
                            if node[2] > 0.0:
                                if node[3] > 0.0:
                                    pass
                                else:
                                    judge_elem_list[i].append(
                                        self.elements[line].eid)
                                    judge_node_list_1[i] = judge_node_list_1[i] + \
                                                           self.elements[line].node_ids
                            else:
                                judge_elem_list[i].append(
                                    self.elements[line].eid)
                                judge_node_list_1[i] = judge_node_list_1[i] + \
                                                       self.elements[line].node_ids
                        else:
                            judge_elem_list[i].append(self.elements[line].eid)
                            judge_node_list_1[i] = judge_node_list_1[i] + \
                                                   self.elements[line].node_ids
                    elif node[0] < 0.0:
                        if node[1] < 0.0:
                            if node[2] < 0.0:
                                if node[3] < 0.0:
                                    pass
                                else:
                                    judge_elem_list[i].append(
                                        self.elements[line].eid)
                                    judge_node_list_1[i] = judge_node_list_1[i] + \
                                                           self.elements[line].node_ids
                            else:
                                judge_elem_list[i].append(
                                    self.elements[line].eid)
                                judge_node_list_1[i] = judge_node_list_1[i] + \
                                                       self.elements[line].node_ids
                        else:
                            judge_elem_list[i].append(self.elements[line].eid)
                            judge_node_list_1[i] = judge_node_list_1[i] + \
                                                   self.elements[line].node_ids
                    else:
                        judge_elem_list[i].append(self.elements[line].eid)
                        judge_node_list_1[i] = judge_node_list_1[i] + \
                                               self.elements[line].node_ids
                elif self.elements[line].type == u'TRIA3':
                    node = [0, 0, 0]
                    for j, line_1 in enumerate(self.elements[line].nodes_ref):
                        xyz = line_1.xyz
                        node[j] = round(normal_vector[0] * (xyz[0] - ori[0]) + normal_vector[1] * (xyz[1] - ori[1]) +
                                        normal_vector[2] * (xyz[2] - ori[2]), 0)
                    judge_1 = node[0] > 0 and node[1] > 0 and node[2] > 0
                    judge_2 = node[0] < 0 and node[1] < 0 and node[2] < 0
                    judge = judge_1 or judge_2
                    if not judge:
                        judge_elem_list[i].append(self.elements[line].eid)
                        judge_node_list_1[i] = judge_node_list_1[i] + \
                                               self.elements[line].node_ids
                judge_node_list_1[i] = list(set(judge_node_list_1[i]))

            for k in judge_node_list_1[i]:
                xyz = self.nodes[k].xyz
                get_node = round(normal_vector[0] * (xyz[0] - ori[0]) + normal_vector[1] * (xyz[1] - ori[1]) +
                                 normal_vector[2] * (xyz[2] - ori[2]), 0)
                if get_node < 0.0:
                    judge_node_list[i].append(k)

        self.judge_elem_list = judge_elem_list
        self.judge_node_list = judge_node_list
        return judge_elem_list, judge_node_list

    def create_gridforce_dict(self, line):
        judge_str = 'G R I D   P O I N T   F O R C E   B A L A N C E'
        for i in range(len(line)):
            line_num = []
            if judge_str in line[i]:
                j = i
                while 'PAGE' not in line[j]:
                    j += 1
                for h in range(i + 3, j + 1):
                    if 'QUAD4' in line[h]:
                        line_num.append(h)
                for m in line_num:
                    list_in = line[m].split()
                    a1 = int(list_in[0]) is 0
                    if a1:
                        self.grid_force_dict[(int(list_in[1]), int(list_in[2]))] = np.array(
                            [float(list_in[4]), float(list_in[5]), float(list_in[6]), float(list_in[7]),
                             float(list_in[8]), float(list_in[9])])
                    else:
                        self.grid_force_dict[(int(list_in[0]), int(list_in[1]))] = np.array(
                            [float(list_in[3]), float(list_in[4]), float(list_in[5]), float(list_in[6]),
                             float(list_in[7]), float(list_in[8])])
        return self.grid_force_dict

    def f06_force_sum(self, line, cross_section_list):
        elem_list = cross_section_list[0]
        node_list = cross_section_list[1]
        force_sum = [np.array([0.0, 0.0, 0.0]) for m in range(len(elem_list))]
        torque_sum = [m * 0.0 for m in range(len(elem_list))]
        shear_force = self.create_gridforce_dict(line)
        for i in range(len(elem_list)):
            for elem in elem_list[i]:
                for node in node_list[i]:
                    if (node, elem) in shear_force:
                        Fx = shear_force[(node, elem)][0]
                        Fy = shear_force[(node, elem)][1]
                        Fz = shear_force[(node, elem)][2]
                        shear = np.array([Fx, Fy, Fz])
                        force_sum[i] = force_sum[i] + shear

                        loc_x = self.nodes[node].xyz[0]
                        loc_y = self.nodes[node].xyz[1]
                        loc_z = self.nodes[node].xyz[2]
                        torque_force = Fx * loc_z + Fz * loc_x
                        torque_sum[i] = torque_sum[i] + torque_force

        return force_sum, torque_sum

    def create_shear_section_plot(self, begin_loc, end_loc, normal_vector, point_number, f06_dir_str):
        my_judge_list = self.get_section_list(
            begin_loc, end_loc, normal_vector, point_number)
        f = open(f06_dir_str, 'r')
        line = f.readlines()

        force = self.f06_force_sum(line, my_judge_list)
        shear_force = force[0]
        shear_force_x = [shear_force[i][0] for i in range(len(shear_force))]
        shear_force_y = [shear_force[i][1] for i in range(len(shear_force))]
        shear_force_z = [shear_force[i][2] for i in range(len(shear_force))]

        fig = plt.figure(u'剪力', facecolor='lightgrey', figsize=(10, 7))
        fig.tight_layout(True, pad=3.0)
        ax = fig.add_subplot(111)
        ax.set_title(u'剪力图', fontsize=18)

        incre = (end_loc[1] - begin_loc[1]) / point_number
        plot_x = [j * incre for j in range(point_number + 1)]

        ax.plot(plot_x, shear_force_z, color='r', marker='o', label=u'Z向剪力')
        ax.plot(plot_x, shear_force_x, color='b', marker='^', label=u'X向剪力')
        ax.plot(plot_x, shear_force_y, color='m', marker='s', label=u'轴向力')
        ax.legend(loc='upper right', ncol=1)

        ax.grid(True)
        ax.xaxis.grid(True, which='minor')
        ax.yaxis.grid(True, which='minor')
        ax.yaxis.get_major_formatter().set_powerlimits((0, 1))  # 将坐标轴的base number设置为一位。
        ax.set_xlabel(u'机翼长度 (单位：mm) ', fontsize=15)
        ax.set_ylabel(u'剪力 (单位：N) ', fontsize=15)
        plt.show()

    def create_bend_section_plot(self, begin_loc, end_loc, normal_vector, point_number, f06_dir_str):
        my_judge_list = self.get_section_list(
            begin_loc, end_loc, normal_vector, point_number)
        f = open(f06_dir_str, 'r')
        line = f.readlines()

        incre = (end_loc[1] - begin_loc[1]) / point_number
        plot_x = [j * incre for j in range(point_number + 1)]

        force = self.f06_force_sum(line, my_judge_list)
        shear_force = force[0]
        shear_force_z = [shear_force[i][2] for i in range(len(shear_force))]
        shear_force_x = [shear_force[i][0] for i in range(len(shear_force))]

        Mx = []
        for m in range(1, point_number + 1):
            Mx_value = 0.0
            for n in range(m, point_number + 1):
                Mx_value = Mx_value + (shear_force_z[n - 1] + shear_force_z[n]) * incre / 2
            Mx.append(round(Mx_value, 2))
        Mx.append(0.0)

        Mz = []
        for m in range(1, point_number + 1):
            Mz_value = 0.0
            for n in range(m, point_number + 1):
                Mz_value = Mz_value + (shear_force_x[n - 1] + shear_force_x[n]) * incre / 2
            Mz.append(round(Mz_value, 2))
        Mz.append(0.0)

        fig = plt.figure(u'弯矩', facecolor='lightgrey', figsize=(10, 7))
        fig.tight_layout(True, pad=3.0)
        ax = fig.add_subplot(111)
        ax.set_title(u'弯矩图', fontsize=18)

        ax.plot(plot_x, Mz, color='r', marker='o', label=u'侧向弯矩')
        ax.plot(plot_x, Mx, color='b', marker='^', label=u'沿翼展弯矩')
        ax.legend(loc='upper right', ncol=1)
        ax.grid(True)
        ax.xaxis.grid(True, which='minor')
        ax.yaxis.grid(True, which='minor')
        ax.yaxis.get_major_formatter().set_powerlimits((0, 1))  # 将坐标轴的base number设置为一位。
        ax.set_xlabel(u'机翼长度 (单位：mm) ', fontsize=15)
        ax.set_ylabel(u'弯矩 (单位：N.mm) ', fontsize=15)
        plt.show()

    def create_torque_section_plot(self, begin_loc, end_loc, normal_vector, point_number, f06_dir_str):
        my_judge_list = self.get_section_list(
            begin_loc, end_loc, normal_vector, point_number)
        f = open(f06_dir_str, 'r')
        line = f.readlines()
        force = self.f06_force_sum(line, my_judge_list)
        shear_force = force[0]
        torque_force = force[1]
        fig = plt.figure(u'扭矩', facecolor='lightgrey', figsize=(10, 7))
        fig.tight_layout(True, pad=3.0)
        ax = fig.add_subplot(111)
        ax.set_title(u'扭矩图', fontsize=18)
        incre = (end_loc[1] - begin_loc[1]) / point_number
        plot_x = [j * incre for j in range(point_number + 1)]
        ax.plot(plot_x, [torque_force[i] for i in range(len(torque_force))],
                color='r', marker='o', label=u'扭矩')
        ax.legend(loc='upper right', ncol=1)
        ax.grid(True)
        ax.xaxis.grid(True, which='minor')
        ax.yaxis.grid(True, which='minor')
        ax.yaxis.get_major_formatter().set_powerlimits((0, 1))  # 将坐标轴的base number设置为一位。
        ax.set_xlabel(u'机翼长度 (单位：mm) ', fontsize=15)
        ax.set_ylabel(u'扭矩 (单位：N.mm) ', fontsize=15)
        plt.show()

    def create_correlation_plot(self, data1=[], data2=[], data_x=[], names=['' for i in range(8)]):
        names = [unicode(item, 'utf-8') for item in names]
        data = array([data1, data2])
        value_cov = cov(data)
        value_corrcoef = corrcoef(data)

        fig = plt.figure(num=u'相关性分析', figsize=(8, 8), facecolor='lightgrey')
        ax1 = fig.add_subplot(211)
        ax2 = fig.add_subplot(212)
        if len(names) == 8:
            ax1.grid(True)
            ax1.set_title(names[0], fontsize=15)
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
        con_str = u'杰尔逊相关系数 ' + str(round(value_corrcoef[0, 1], 3))
        fig.text(0.1, 0.37, con_str)
        fig.tight_layout(h_pad=1.0)
        plt.show()

    def create_new_node_xyz(self, f06_dir_str):
        try:
            f = open(f06_dir_str, 'r')
        except IOError:
            print ('not exist' + f06_dir_str)
        else:
            line = f.readlines()
            for i in range(len(line)):
                if 'D I S P L A C E M E N T   V E C T O R' in line[i]:
                    j = i
                    while 'PAGE' not in line[j]:
                        j += 1
                    for m in range(i + 3, j):
                        line_list = line[m].split()
                        self.node_increment_xyz[int(line_list[0])] = np.array(
                            [float(line_list[2]), float(line_list[3]), float(line_list[4])])
            f.close()
        for i in self.node_increment_xyz:
            self.new_node_xyz[i] = self.node_increment_xyz[i] + \
                                   self.nodes[i].xyz
        return self.new_node_xyz

    def create_new_grid_dat(self, my_input_bdf, my_input_f06, my_output_dir, n):
        name = os.path.basename(my_input_bdf).split('.')[0]
        self.read_bdf(my_input_bdf)

        for i in range(1, n + 1):
            my_stage = '{:0>2d}'.format(i)
            txtnew1 = open(my_output_dir + '//' + name +
                           '_' + str(my_stage) + '_grid.dat', "w")
            new_node_xyz = self.create_new_node_xyz(
                my_input_f06 + '//' + name + '_' + str(my_stage) + '.f06')
            msg = ''
            for j in new_node_xyz:
                grid = 'GRID,%i,,%s,%s,%s\n' % (
                    j, new_node_xyz[j][0], new_node_xyz[j][1], new_node_xyz[j][2])
                msg += grid
            txtnew1.write(msg)
            txtnew1.close()

    # def mesh_evaluate(self, long, width, mesh_length, my_output_dir, nastran_dir):
    #     x = long
    #     y = width
    #     v = mesh_length
    #
    #     if x > y:
    #         if v > y:
    #             nx = int(float(x) / float(v)) + 1
    #             ny = 2
    #         else:
    #             nx = int(float(x) / float(v)) + 1
    #             ny = int(float(y) / float(v)) + 1
    #     elif y > x:
    #         if v > x:
    #             nx = 2
    #             ny = int(float(y) / float(v)) + 1
    #         else:
    #             nx = int(float(x) / float(v)) + 1
    #             ny = int(float(y) / float(v)) + 1
    #
    #     bdf_str = 'SOL 101\nCEND\nSUBCASE 1\n' \
    #               '   SUBTITLE=Default\n' \
    #               '   SPC = 2\n' \
    #               '   LOAD = 2\n' \
    #               '   DISPLACEMENT(SORT1,REAL)=ALL\n' \
    #               '   SPCFORCES(SORT1,REAL)=ALL\n' \
    #               '   STRESS(SORT1,REAL,VONMISES,BILIN)=ALL\n' \
    #               'BEGIN BULK\nPARAM,POST,-1\nPARAM   PRTMAXIM YES\n'
    #
    #     for j in range(1, ny + 1):
    #         for i in range(1, nx + 1):
    #             lx = (i - 1) * float(x) / (nx - 1)
    #             ly = (j - 1) * float(y) / (ny - 1)
    #             bdf_str += 'GRID,{},,{},{},0.0\n'.format(
    #                 (j - 1) * nx + i, lx, ly)
    #
    #     for j in range(1, ny):
    #         for i in range(1, nx):
    #             nid = (j - 1) * (nx - 1) + i
    #             g1 = (j - 1) * nx + i
    #             g2 = (j - 1) * nx + i + 1
    #             g3 = j * nx + i
    #             g4 = j * nx + i + 1
    #             bdf_str += 'CQUAD4,{},1,{},{},{},{}\n'.format(
    #                 nid, g1, g2, g4, g3)
    #
    #     bdf_str += 'PSHELL   1       1      .01      1               1\n' \
    #                'MAT1     1      7.+10           .3      2700.   2.32-5\n'
    #     bdf_str += 'SPCADD,2,1\nLOAD,2,1.,1.,1\nSPC1,1,123456,{},{}\n'.format(
    #         1, (ny - 1) * nx + 1)
    #     bdf_str += 'FORCE,1,{},,1.0,0.0,0.0,{}\n'.format(nx * ny, 1000.0 / 2)
    #     bdf_str += 'ENDDATA\n'
    #
    #     bdf = my_output_dir + 'mesh_eval.bdf'
    #     f06 = my_output_dir + 'mesh_eval.f06'
    #     f1 = open(bdf, 'w')
    #     f1.write(bdf_str)
    #     f1.close()
    #
    #     if os.path.exists(bdf):
    #         os.system(
    #             nastran_dir + ' scr=yes delete=f04,log,xdb old=no out=%s %s' % (my_output_dir, bdf))
    #     else:
    #         raise RuntimeError(u'%s下bdf不存在' % (my_output_dir))
    #
    #     self.nastran_psutil()
    #
    #     if os.path.exists(f06):
    #         f1 = open(f06, 'r')
    #         f06_lines = f1.readlines()
    #         f1.close()
    #         for line in f06_lines:
    #             if 'FATAL' not in line.split():
    #                 pass
    #             else:
    #                 raise RuntimeError(u'f06文件%s计算有FATAL错误' % (f06))
    #         deformed_displacement = {}
    #         for i in range(len(f06_lines)):
    #             if 'D I S P L A C E M E N T   V E C T O R' in f06_lines[i]:
    #                 j = i
    #                 while 'PAGE' not in f06_lines[j]:
    #                     j += 1
    #                 for m in range(i + 3, j):
    #                     transient_list = f06_lines[m].split()
    #                     deformed_displacement[int(transient_list[0])] = np.array(
    #                         [float(transient_list[2]), float(transient_list[3]), float(transient_list[4]),
    #                          float(transient_list[5]), float(transient_list[6]), float(transient_list[7])])
    #             elif ' MAXIMUM  DISPLACEMENTS ' in f06_lines[i]:
    #                 r3 = float(f06_lines[i + 3].split()[4])
    #     else:
    #         raise RuntimeError(u'f06文件%s不存在' % (f06))
    #     return r3, nx * ny

    def mesh_evaluate(self, mesh_length, mesh):
        assert len(mesh) == 5, 'len(mesh) error'
        x = mesh[2]
        y = mesh[3]
        v = mesh_length
        h = mesh[4]
        my_output_dir = mesh[1]
        nastran_dir = mesh[0]

        if x > y:
            if v > y:
                nx = int(float(x) / float(v)) + 1
                ny = 2
            else:
                nx = int(float(x) / float(v)) + 1
                ny = int(float(y) / float(v)) + 1
        elif y > x:
            if v > x:
                nx = 2
                ny = int(float(y) / float(v)) + 1
            else:
                nx = int(float(x) / float(v)) + 1
                ny = int(float(y) / float(v)) + 1

        bdf_str = 'SOL 101\nCEND\nSUBCASE 1\n' \
                  '   SUBTITLE=Default\n' \
                  '   SPC = 2\n' \
                  '   LOAD = 2\n' \
                  '   DISPLACEMENT(SORT1,REAL)=ALL\n' \
                  '   SPCFORCES(SORT1,REAL)=ALL\n' \
                  '   STRESS(SORT1,REAL,VONMISES,BILIN)=ALL\n' \
                  'BEGIN BULK\nPARAM,POST,-1\nPARAM   PRTMAXIM YES\n'

        for j in range(1, ny + 1):
            for i in range(1, nx + 1):
                lx = (i - 1) * float(x) / (nx - 1)
                ly = (j - 1) * float(y) / (ny - 1)
                bdf_str += 'GRID,{},,{},{},0.0\n'.format(
                    (j - 1) * nx + i, lx, ly)

        for j in range(1, ny):
            for i in range(1, nx):
                nid = (j - 1) * (nx - 1) + i
                g1 = (j - 1) * nx + i
                g2 = (j - 1) * nx + i + 1
                g3 = j * nx + i
                g4 = j * nx + i + 1
                bdf_str += 'CQUAD4,{},1,{},{},{},{}\n'.format(
                    nid, g1, g2, g4, g3)

        bdf_str += 'PSHELL,1,1,{},1,,1\nMAT1     1      7.+10           .3      2700.   2.32-5\n'.format(h)
        bdf_str += 'SPCADD,2,1\nLOAD,2,1.,1.,1\nSPC1,1,123456,{},{}\n'.format(1, (ny - 1) * nx + 1)
        bdf_str += 'FORCE,1,{},,1.0,0.0,0.0,{}\n'.format(nx * ny, 1000.0 / 2)
        bdf_str += 'ENDDATA\n'

        bdf = my_output_dir + 'mesh_eval.bdf'
        f06 = my_output_dir + 'mesh_eval.f06'
        f1 = open(bdf, 'w')
        f1.write(bdf_str)
        f1.close()

        if os.path.exists(bdf):
            os.system(
                nastran_dir + ' scr=yes delete=f04,log,xdb old=no out=%s %s' % (my_output_dir, bdf))
        else:
            raise RuntimeError(u'%s下bdf不存在' % (my_output_dir))

        self.nastran_psutil()

        if os.path.exists(f06):
            f1 = open(f06, 'r')
            f06_lines = f1.readlines()
            f1.close()
            for line in f06_lines:
                if 'FATAL' not in line.split():
                    pass
                else:
                    raise RuntimeError(u'f06文件%s计算有FATAL错误' % (f06))
            deformed_displacement = {}
            for i in range(len(f06_lines)):
                if 'D I S P L A C E M E N T   V E C T O R' in f06_lines[i]:
                    j = i
                    while 'PAGE' not in f06_lines[j]:
                        j += 1
                    for m in range(i + 3, j):
                        transient_list = f06_lines[m].split()
                        deformed_displacement[int(transient_list[0])] = np.array(
                            [float(transient_list[2]), float(transient_list[3]), float(transient_list[4]),
                             float(transient_list[5]), float(transient_list[6]), float(transient_list[7])])
                elif ' MAXIMUM  DISPLACEMENTS ' in f06_lines[i]:
                    r3 = float(f06_lines[i + 3].split()[4])
        else:
            raise RuntimeError(u'f06文件%s不存在' % (f06))
        return r3, nx * ny

    def normal_modes(self, my_output_dir, nastran_dir):
        model_eval_bdf = my_output_dir + 'model_eval.bdf'
        model_eval_f06 = my_output_dir + 'model_eval.f06'

        self.sol = 103
        self.add_card(['EIGRL', 1, None, None, 10, 0], 'EIGRL')
        self.case_control_deck.add_parameter_to_local_subcase(
            1, 'VECTOR = ALL')
        self.case_control_deck.add_parameter_to_local_subcase(
            1, 'METHOD = 1')
        self.write_bdf(model_eval_bdf)
        if os.path.exists(model_eval_bdf):
            os.system(
                nastran_dir + ' scr=yes delete=f04,log,xdb old=no out=%s %s' % (my_output_dir, model_eval_bdf))
        else:
            raise RuntimeError(u'%s下bdf不存在' % (my_output_dir))
        self.nastran_psutil()
        nomal_f = []
        if os.path.exists(model_eval_f06):
            f2 = open(model_eval_f06, 'r')
            f06_lines = f2.readlines()
            for line in f06_lines:
                if 'FATAL' not in line.split():
                    pass
                else:
                    raise RuntimeError(u'f06文件%s计算有FATAL错误' % (model_eval_f06))
            for i in range(len(f06_lines)):
                if '  R E A L   E I G E N V A L U E S' in f06_lines[i]:
                    j = i
                    while 'PAGE' not in f06_lines[j]:
                        j += 1
                    for m in range(i + 3, j):
                        rt = f06_lines[m].split()[4]
                        nomal_f.append(rt)
            f2.close()
        else:
            raise RuntimeError(u'f06文件%s不存在' % (model_eval_f06))
        return float(nomal_f[0])


def main(sys_argv):
    static_nast = STATIC()
    if sys_argv[1] == 'running':
        try:
            input_bdf = sys_argv[2]
            force_file = sys_argv[3]
            nastran = sys_argv[4]
            output_dir = sys_argv[5]
        except:
            raise RuntimeError('running input error at c++ to python')
        static_nast.run_nast_increment(force_file, input_bdf, output_dir, nastran)

    elif sys_argv[1] == 'shear' or sys_argv[1] == 'bend' or sys_argv[1] == 'torque':
        static_nast.read_bdf(sys_argv[2])
        my_begin_loc = np.array([float(x) for x in sys_argv[3].split(',')])
        my_end_loc = np.array([float(x) for x in sys_argv[4].split(',')])
        my_normal_vector = my_end_loc - my_begin_loc
        my_point_number = 10
        my_f06 = sys_argv[5]

        if sys_argv[1] == 'shear':
            static_nast.create_shear_section_plot(
                my_begin_loc, my_end_loc, my_normal_vector, my_point_number, my_f06)
        elif sys_argv[1] == 'bend':
            static_nast.create_bend_section_plot(
                my_begin_loc, my_end_loc, my_normal_vector, my_point_number, my_f06)
        elif sys_argv[1] == 'torque':
            static_nast.create_torque_section_plot(
                my_begin_loc, my_end_loc, my_normal_vector, my_point_number, my_f06)

    elif sys_argv[1] == 'correlation':
        # get force
        force = []
        _dict = {}
        min_num = None
        try:
            _f = open(sys_argv[2], 'r')
            lines = _f.readlines()
            _f.close()
        except:
            raise RuntimeError('no force file')

        new_lines = lines[:]
        if lines:
            line = lines.pop(0)
            _list = line.split(',')
            min_num = int((len(_list) - 1) / 2)
            for line in lines:
                _list = line.split(',')
                min_num = min(min_num, int((len(_list) - 1) / 2))

            for i in range(min_num):
                _dict = {}
                for line in new_lines:
                    _list = line.split(',')
                    _dict[int(_list[0])] = float(_list[2 * i + 2])
                _dict["stage"] = [i, int(_list[2 * i + 1])]
                force.append(_dict)

        my_data_x = []
        if force:
            my_data_x = [force[i]['stage'][1] for i in range(len(force))]

        with open(sys_argv[3], 'r') as fp:
            p_lines = fp.readlines()
        with open(sys_argv[4], 'r') as fv:
            v_lines = fv.readlines()

        data1 = [round(float(line.strip(' ')), 3)
                 for line in v_lines[0].split(',')]
        data2 = [round(float(line.strip(' ')), 3)
                 for line in p_lines[0].split(',')]

        names = ['散点图', '虚拟试验位移', '物理试验位移', '折线图', '加载级', '位移', '虚拟试验', '物理试验']

        if my_data_x:
            static_nast.create_correlation_plot(data1, data2, my_data_x, names)
        else:
            raise RuntimeError('loadInfo txt file error')

    elif sys_argv[1] == 'bdfedit':
        input_bdf_dir = sys_argv[2]

        # get force
        force = []
        _dict = {}
        min_num = None
        try:
            _f = open(sys_argv[3], 'r')
            lines = _f.readlines()
            _f.close()
        except:
            raise RuntimeError('no force file')
        new_lines = lines[:]
        if lines:
            line = lines.pop(0)
            _list = line.split(',')
            min_num = int((len(_list) - 1) / 2)
            for line in lines:
                _list = line.split(',')
                min_num = min(min_num, int((len(_list) - 1) / 2))

            for i in range(min_num):
                _dict = {}
                for line in new_lines:
                    _list = line.split(',')
                    _dict[int(_list[0])] = float(_list[2 * i + 2])
                _dict["stage"] = [i, int(_list[2 * i + 1])]
                force.append(_dict)
        my_data_x = []
        if force:
            my_data_x = [force[i]['stage'][1] for i in range(len(force))]

        input_f06_dir = os.path.dirname(sys_argv[4])
        output_dir = sys_argv[5] + '\\'
        static_nast.create_new_grid_dat(
            input_bdf_dir, input_f06_dir, output_dir, len(my_data_x))

    # elif sys_argv[1] == 'meval':
    #     nastran = sys_argv[2]
    #     output_dir = sys_argv[3] + '\\'
    #     x = 4
    #     y = 2
    #     # v_list = [(10 - 0.5 * i) for i in range(1, 11)]
    #     v_list = [0.02, 0.025, 0.03, 0.04, 0.06,
    #               0.08, 0.1, 0.2, 0.4, 0.6, 0.8, 1.0, 2.0]
    #     my_max = []
    #     my_num = []
    #     if v_list:
    #         for v in v_list:
    #             r = static_nast.mesh_evaluate(x, y, v, output_dir, nastran)
    #             my_max.append(r[0])
    #             my_num.append(r[1])
    #     else:
    #         raise RuntimeError(u'v_list不存在')
    #
    #     fig = plt.figure(u'网格评估', facecolor='lightgrey', figsize=(10, 7))
    #     fig.tight_layout(True, pad=3.0)
    #     ax = fig.add_subplot(111)
    #     ax.set_title(u'网格评估', fontsize=18)
    #     ax.plot(my_num, my_max, color='r', marker='o', label=u'网格')
    #     # ax.legend(loc='upper right', ncol=1)
    #     ax.grid(True)
    #     ax.xaxis.grid(True, which='minor')
    #     ax.yaxis.grid(True, which='minor')
    #     ax.set_xlabel(u'单元数量  ', fontsize=15)
    #     ax.set_ylabel(u'加载点的位移 (单位：mm) ', fontsize=15)
    #     plt.show()

    elif sys_argv[1] == 'meval':
        import copy
        # nastran, output_dir, x, y, h
        assert len(sys_argv) == 7, 'meval函数输入的参数有误'
        meval_input = copy.copy(sys_argv[2:7])
        if ':' in meval_input[0] and ':' in meval_input[1]:
            meval_input[1] += '\\'
            _a = min(float(meval_input[2]), float(meval_input[3]))
            v_list = [_a / i for i in range(1, 101, 9)]
            my_max = []
            my_num = []
            if v_list:
                for v in v_list:
                    r = static_nast.mesh_evaluate(v, meval_input)
                    my_max.append(r[0])
                    my_num.append(r[1])
            else:
                raise RuntimeError(u'meval中v_list不存在')
        else:
            raise RuntimeError('meval前两个参数不是路径')

        fig = plt.figure(u'网格评估', facecolor='lightgrey', figsize=(10, 7))
        fig.tight_layout(True, pad=3.0)
        ax = fig.add_subplot(111)
        ax.set_title(u'网格评估', fontsize=18)
        ax.plot(my_num, my_max, color='r', marker='o', label=u'网格')
        # ax.legend(loc='upper right', ncol=1)
        ax.grid(True)
        ax.xaxis.grid(True, which='minor')
        ax.yaxis.grid(True, which='minor')
        ax.set_xlabel(u'单元数量  ', fontsize=15)
        ax.set_ylabel(u'加载点的位移 (单位：mm) ', fontsize=15)
        plt.show()

    elif sys_argv[1] == 'peval':
        input_bdf = sys_argv[2]
        nastran = sys_argv[3]
        output_dir = sys_argv[4] + '\\'
        static_nast.read_bdf(input_bdf)
        mass, cg, I = static_nast.mass_properties()
        Ixx, Iyy, Izz, Ixy, Ixz, Iyz = I
        Fre = static_nast.normal_modes(output_dir, nastran)
        data1 = [cg[0], cg[1], cg[2], mass, Ixx, Iyy, Izz, Fre]
        data2 = [data1[ii] * 0.8 if ii > 5 or ii < 2 else data1[ii]
                 for ii in range(len(data1))]
        data = array([data1, data2])
        value_cov = cov(data)
        value_corrcoef = corrcoef(data)[0, 1]
        model_txt_str = ''
        for ii in range(len(data1)):
            model_txt_str += '{:.3e}{}{:.3e}\n'.format(
                data1[ii], 7 * ' ', data2[ii])
        model_txt_str += '{:.4f}\n'.format(value_corrcoef)

        with open(output_dir + 'model_eval.txt', 'w') as f2:
            f2.write(model_txt_str)

    else:
        wnd = tkinter.Tk()
        wnd.withdraw()
        messagebox.showinfo('ERROR', 'No Method')


if __name__ == '__main__':
    try:
        # main(sys.argv)
        main([line.split()[1:] for line in
              open('E:\work\\611\\vte\\proj611\\proj611_py\\vte_static.bat', 'r').readlines()
              if ('correlation' in line and '%py% %input% ' in line)][0])
    except:
        traceback.print_exc()
        wnd = tkinter.Tk()
        wnd.withdraw()
        messagebox.showinfo('ERROR', str(sys.exc_info()[1]))
        for line in sys.argv:
            print('--->' + line)
        os.system('pause')
