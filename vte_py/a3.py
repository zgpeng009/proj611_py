import numpy as np


def computer_vect(node1, node2):
    """
    node1和node2分别为线单元的两个节点坐标，数据类型：float
    返回node_vect为线单元的向量值，数据类型：float
    """

    _node = node1 - node2
    _node = _node / (_node[0] ** 2 + _node[1] ** 2 + _node[2] ** 2) ** 0.5

    if _node[0] == 0.0:
        ref = _node[1]
        _node[1] = _node[2]
        _node[2] = -ref
    elif _node[1] == 0.0:
        ref = _node[0]
        _node[0] = _node[2]
        _node[2] = -ref
    elif _node[2] == 0.0:
        ref = _node[0]
        _node[0] = _node[1]
        _node[1] = -ref
    else:
        _node[0] = 0.0
        ref = _node[1]
        _node[1] = _node[2]
        _node[2] = -ref
    node_vect = _node / (_node[0] ** 2 + _node[1] ** 2 + _node[2] ** 2) ** 0.5

    return node_vect


if __name__ == '__main__':
    a1 = np.array([0.0, 0.00000, 1.0])
    a2 = np.array([0.0, 0.0000, 0.0])
    print(computer_vect(a1, a2))
