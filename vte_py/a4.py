import os


def parse_tempload():
    _f = open('E:\\work\\611\\vte\\tempload_static\\tempload_static_product.bdf', 'r')
    lines = _f.readlines()
    _f.close()
    node = []
    for line in lines:
        _line = line.split()
        if _line[0] == 'GRID':
            node.append(_line[1])

    _f = open('E:\\work\\611\\vte\\thermal\\patran.rpt', 'r')
    lines = _f.readlines()
    _f.close()
    _str = ''

    node_t = []
    for line in lines:
        _line = line.split()
        node_t.append(_line[0])
        _str += 'Node ' + _line[0] + ',' + _line[1] + '\n'

    node_difference = list(set(node).difference(set(node_t)))

    for n in node_difference:
        _str += 'Node ' + n + ',' + '0.0' + '\n'

    _f = open('E:\\work\\611\\vte\\tempload_static\\tempload.csv.02', 'w')
    _f.write(_str)
    _f.close()


if __name__ == '__main__':
    parse_tempload()
