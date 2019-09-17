# coding: utf-8

# pyreverse -ASmy -o png D:\Python36\Lib\site-packages\tensorflow\python\client\session.py
# pyreverse -ASmy -o png D:\Python36\Lib\site-packages\tensorflow\python\client
# pyreverse -ASmy -o png D:\Python36\Lib\site-packages\pyNastran\bdf (png太大，模糊)
# pyreverse -ASmy -o png D:\Python36\Lib\site-packages\pyNastran\bdf\bdf.py


import subprocess
import os
import psutil

ansys_dir = 'D:/Program Files/ANSYS Inc/v193/ANSYS/bin/winx64/launcher.exe'
# process = subprocess.call([ansys_dir, '-runae'])
# os.system('\"D:/Program Files/ANSYS Inc/v193/ANSYS/bin/winx64/launcher.exe\" -runae')
# os.system('\"D:\\Program Files\\ANSYS Inc\\v145\\ansys\\bin\\winx64\\ANSYS145.exe\" -b -j file -dir E:\\work\\611\\vte\\aerofoil\\ansys -i E:\\work\\611\\vte\\aerofoil\\ansys\\file.mac -o E:\\work\\611\\vte\\aerofoil\\ansys\\file.dat')
os.system('\"D:\\Program Files\\ANSYS Inc\\v145\ANSYS\\bin\\winx64\\launcher145.exe\" -runae')

p_id = psutil.pids()
for p in p_id:
    process = psutil.Process(p)
    psn = process.name()
    if 'ANSYS' in psn:
        process.kill()
    elif 'MAPDL' in psn:
        process.kill()

# *cfopen,aaa,f06
# 	allsel,all
# 	*get,nmax,node,0,num,max
# 	*get,nmin,node,0,num,min
# 	*do,i,nmin,nmax
# 		uxn = nx(i)
# 		uyn = ny(i)
# 		uzn = nz(i)
# 		*vwrite,'node', '%i%' ,uxn,uyn,uzn
# 		(a8,a8,3f14.5)
# 	*enddo
# *cfclos
#
#
# /post1
# /output,zzzzz1,dat
# PRNSOL,U,COMP
# /output
#
# /post1
# set,lastplns,s,1
# *get,numnode,node,,count
# *dim,nd_sig1,array,numnode
# *vget,nd_sig1(1),node,,s,1
# *cfopen,'myfile','txt'
# *vlen,1
# *vwrite,'Nodal','Stress_1'
# (A8,X,A8)
# *vwrite,sequ,nd_sig1(1)
# (F8.0,X,E13.6,X,E13.6)
# *cfclos
