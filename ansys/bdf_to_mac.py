# coding: utf-8

import os
import inspect

from pyNastran.bdf.bdf import BDF

CURRENT_DIR = os.path.dirname(__file__)
# BDF_DIR = os.path.join(CURRENT_DIR, 'aerofoil.bdf')
BDF_DIR = os.path.join('E:\\work\\611\\vte\\aerofoil\\VTE_catia', 'aerofoil_product.bdf')
# MAC_DIR = os.path.join(CURRENT_DIR, 'aerofoil.mac')
MAC_DIR = os.path.join('E:\\work\\611\\vte\\aerofoil\\ansys', 'file.mac')


def parse_bdf(lines):
    for line in lines:
        if 'BEGIN BULK' in line:
            return True
    return False


def bdf_to_mac():
    # open bdf file
    _f = open(BDF_DIR, 'r')
    bulk_data_lines = _f.readlines()
    _f.close()
    bdf_check = parse_bdf(bulk_data_lines)

    # parse bdf file
    bdf = BDF()
    if bdf_check:
        bdf.read_bdf(BDF_DIR)
    else:
        cards_list, cards_dict, card_count = bdf.get_bdf_cards(bulk_data_lines)
        bdf._parse_cards(cards_list, cards_dict, card_count)
    print('bdf finished')

    _f_mac = open(MAC_DIR, 'w')
    head = 'finish\n'
    head += '/clear\n'
    head += '/prep7\n'
    _f_mac.write(head)

    # convert mac file
    mac_xyz = ''
    for grid_key in bdf.nodes:
        grid = bdf.nodes[grid_key]
        node_id = grid.nid
        node_xyz = grid.xyz
        mac_xyz += 'n,{},{},{},{}\n'.format(node_id, node_xyz[0], node_xyz[1], node_xyz[2])
    _f_mac.write(mac_xyz)

    # element_pro = 'et,1,shell41\n'
    element_pro = 'et,1,shell181\n'
    element_pro += 'mp,dens,1,2700\n'
    element_pro += 'mp,ex,1,70e9\n'
    element_pro += 'mp,prxy,1,0.3\n'
    element_pro += 'r,1,0.5\n'
    element_pro += 'type,1\n'
    element_pro += 'mat,1\n'
    element_pro += 'real,1\n'
    # element_pro += 'sect,1,shell,,\n'
    # element_pro += 'secdata,1.0,1,0.0,3\n'  # 1(mp), 0.0(orientation), 3(integration)
    # element_pro += 'secoffset,MID\n'  # mid(section offset)
    elements_mac = ''
    for ele_key in bdf.elements:
        element = bdf.elements[ele_key]
        element_id = element.pid
        element_nodes = element.node_ids
        if element.type == 'CQUAD4':
            elements_mac += 'e,{},{},{},{}\n'.format(element_nodes[0], element_nodes[1], element_nodes[2],
                                                     element_nodes[3])
    if elements_mac:
        _f_mac.write(element_pro + elements_mac)

    element_pro = 'et,2,solid185\n'
    element_pro += 'mp,dens,2,2700\n'
    element_pro += 'mp,ex,2,70e9\n'
    element_pro += 'mp,prxy,2,0.3\n'
    element_pro += 'r,2\n'
    element_pro += 'type,2\n'
    element_pro += 'mat,2\n'
    element_pro += 'real,2\n'
    elements_mac = ''
    for ele_key in bdf.elements:
        element = bdf.elements[ele_key]
        element_id = element.pid
        element_nodes = element.node_ids
        if element.type == 'CHEXA':
            elements_mac += 'e,{},{},{},{},{},{},{},{}\n'.format(element_nodes[0], element_nodes[1], element_nodes[2],
                                                                 element_nodes[3], element_nodes[4], element_nodes[5],
                                                                 element_nodes[6], element_nodes[7])
    if elements_mac:
        _f_mac.write(element_pro + elements_mac)

    # element_pro = 'et,3,beam4\n'
    element_pro = 'et,3,beam188\n'
    element_pro += 'mp,dens,3,2700\n'
    element_pro += 'mp,ex,3,70e9\n'
    element_pro += 'mp,prxy,3,0.3\n'
    element_pro += 'sectype,3,beam,hrec\n'
    element_pro += 'secdata,100,100,10,10,10,10\n'
    # element_pro += 'r,3,50,1000,1000,,,,,500\n'  # Area, Izz, Iyy,,,,,Ixx
    element_pro += 'type,3\n'
    element_pro += 'mat,3\n'
    element_pro += 'secnum,3\n'
    # element_pro += 'real,3\n'
    elements_mac = ''
    for ele_key in bdf.elements:
        element = bdf.elements[ele_key]
        element_id = element.pid
        element_nodes = element.node_ids
        if element.type == 'CQUAD4' or element.type == 'CHEXA' or element.type == 'CPENTA':
            continue
        if element.type == 'CBAR' and element_id.pid == 2:
            elements_mac += 'e,{},{}\n'.format(element_nodes[0], element_nodes[1])
    if elements_mac:
        _f_mac.write(element_pro + elements_mac)

    element_pro = 'et,5,beam188\n'
    element_pro += 'mp,dens,5,2700\n'
    element_pro += 'mp,ex,5,70e9\n'
    element_pro += 'mp,prxy,5,0.3\n'
    element_pro += 'sectype,5,beam,csolid\n'
    element_pro += 'secdata,10\n'
    element_pro += 'type,5\n'
    element_pro += 'mat,5\n'
    element_pro += 'secnum,5\n'
    elements_mac = ''
    for ele_key in bdf.elements:
        element = bdf.elements[ele_key]
        element_id = element.pid
        element_nodes = element.node_ids
        if element.type == 'CBAR' and element_id.pid == 3:
            elements_mac += 'e,{},{}\n'.format(element_nodes[0], element_nodes[1])
    if elements_mac:
        _f_mac.write(element_pro + elements_mac)

    element_pro = 'et,4,link180\n'
    element_pro += 'mp,dens,4,2700\n'
    element_pro += 'mp,ex,4,70e9\n'
    element_pro += 'mp,prxy,4,0.3\n'
    element_pro += 'r,4,1e-06,0,0\n'  # Area, Unit mass, drag/press
    element_pro += 'type,4\n'
    element_pro += 'mat,4\n'
    element_pro += 'real,4\n'
    elements_mac = ''
    for ele_key in bdf.elements:
        element = bdf.elements[ele_key]
        element_id = element.pid
        element_nodes = element.node_ids
        if element.type == 'CGAP':
            elements_mac += 'e,{},{}\n'.format(element_nodes[0], element_nodes[1])
    if elements_mac:
        _f_mac.write(element_pro + elements_mac)

    others = ''
    others += 'nsle,u\n'
    others += 'ndele,all\n'
    others += 'allsel,all\n'
    others += 'nsel,,loc,y,-100,80\n'
    others += 'cp,next,all,all\n'
    others += 'nsel,all\n'
    others += 'cp,next,all,1173,2313\n'  # Node 1173 2313
    others += 'cp,next,all,2312,1170\n'  # Node 2312 1170
    others += 'cp,next,all,2310,685\n'  # Node 2310 685
    others += 'cp,next,all,2311,682\n'  # Node 2311 682
    others += 'cp,next,all,1167,2303\n'  # Node 1167 2303
    others += 'cp,next,all,1164,2304\n'  # Node 1164 2304
    others += 'cp,next,all,679,2302\n'  # Node 679 2302
    others += 'cp,next,all,676,2305\n'  # Node 676 2305
    others += 'allsel,all\n'
    _f_mac.write(others)

    spc = ''
    spc += 'd,2298,all\n'
    spc += 'nsel,,loc,y,-240,-200\n'
    spc += 'd,all,all\n'  # d,node_id,ux
    spc += 'allsel,all\n'
    _f_mac.write(spc)

    force = ''
    force += 'f,2301,fz,50000\n'
    _f_mac.write(force)

    solve = ''
    solve += 'allsel,all\n'
    solve += 'eplot\n'
    solve += 'finish\n'
    solve += '/sol\n'
    solve += 'antype,0\n'
    solve += '/status,solu\n'
    solve += 'solve\n'
    _f_mac.write(solve)

    result = ''
    result += 'finish\n'
    result += '/post1\n'
    result += '/efacet,1\n'
    result += 'prnsol,u,comp\n'  # /format: first table num (7 + node/element id) + n * 12  (G12.5)
    result += 'presol,f\n'
    result += 'finish\n'  # *use,E:\work\611\vte\aerofoil\ansys\a\aaa.mac == nastran include card
    _f_mac.write(result)  # /prep7 and finish     /sol and finish     /post1 and finish

    _f_mac.close()


if __name__ == '__main__':
    bdf_to_mac()
    # 'E:\work\demo\aerofoil.mac'
    # /INPUT,'a','mac','E:\WORK\611\VTE\AEROFOIL\ANSYS\',, 0
    # "D:\Program Files\ANSYS Inc\v145\ansys\bin\winx64\ANSYS145.exe" -b -i a.mac -o z1.dat

    # 读取dat结果数据、对f,2301,,,modify、剪力图弯矩图、bdfedit,,,,(另外编写py）
