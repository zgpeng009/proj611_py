import os

import xml.etree.ElementTree as ET


def parse_xml():
    path = "C:\\Users\\Administrator.SC-201808281805\\Desktop\\workbench\\material"
    parents = os.listdir(path)
    param_name = []
    for parent in parents:
        xml_dir = path + '\\' + parent
        tree = ET.parse(xml_dir)
        root = tree.getroot()
        Materials = root.find('Materials')
        MatML_Doc = Materials.find('MatML_Doc')
        Metadata = MatML_Doc.find('Metadata')
        ParameterDetails = Metadata.findall('ParameterDetails')
        for ParameterDetail in ParameterDetails:
            p_name = ParameterDetail.find('Name').text
            if '[' in p_name:
                continue
            param_name.append(p_name)
    param_name_1 = set(param_name)
    param_name = list(param_name_1)

    _f = open(os.path.split(path)[0] + '\\' + 'param_name.txt', 'w')
    _f.write('\n'.join(param_name))
    _f.close()


def property_param_txt():
    path = 'C:\\Users\\Administrator.SC-201808281805\\Desktop\\workbench'
    _f = open(path + '\\property_param.txt', 'r')
    lines = _f.readlines()
    for line in lines:
        print('aaa')


if __name__ == '__main__':
    parse_xml()
