set py=D:\Python27\python2.exe
set input=E:\\work\\611\vte\\proj611\\proj611_py\\vte_static.py

call:correlation

:running
%py% %input% running E:\work\611\vte\proj611\proj611_py\aerofoil_product.bdf E:\work\611\vte\proj611\proj611_py\Result_Data\xx_loadInfo.txt D:\\MSC.Software\\MSC_Nastran\\20122\\bin\\nastran.exe E:\work\611\vte\proj611\proj611_py\Result_Data
pause
exit


:shear
%py% %input% shear E:\\work\\611\\vte\\proj611\\proj611_py\\aerofoil_product.bdf -345.0,99.3,122.7 241.5,6000.0,134.7 E:\\work\\611\vte\\proj611\\proj611_py\\Result_Data\\aerofoil_product_05.f06
pause
exit

:bend
%py% %input% bend E:\\work\\611\\vte\\proj611\\proj611_py\\aerofoil_product.bdf -345.0,99.3,122.7 241.5,6000.0,134.7 E:\\work\\611\vte\\proj611\\proj611_py\\Result_Data\\aerofoil_product_05.f06
pause
exit

:torque
%py% %input% torque E:\\work\\611\vte\\proj611\\proj611_py\\aerofoil_product.bdf -345.0,99.3,122.7 241.5,6000.0,134.7 E:\\work\\611\vte\\proj611\\proj611_py\\Result_Data\\aerofoil_product_05.f06
pause
exit

:correlation
%py% %input% correlatio= E:\\work\\611\\vte\\proj611\\proj611_py\\Result_Data\xx_loadInfo.txt E:\\work\\611\vte\\proj611\\proj611_py\\Result_Data\test_data_physical.txt E:\\work\\611\vte\\proj611\\proj611_py\\Result_Data\test_data_virtual.txt
pause
exit

:correlation
%py% %input% correlation 20,40,60,80,100 1.023694,6.933699,13.58325,20.25471,26.76528 0.523694,8.233699,11.68325,21.55471,23.86528
pause
exit

:bdfedit
%py% %input% bdfedit E:\\work\\611\\vte\\proj611\\proj611_py\\aerofoil_product.bdf E:\\work\\611\vte\\proj611\\proj611_py\\Result_Data\xx_loadInfo.txt E:\\work\\611\vte\\proj611\\proj611_py\\Result_Data\aerofoil_product_1.f06 E:\\work\\611\vte\\proj611\\proj611_py\\Pp_Data
pause
exit

:meval
%py% %input% meval D:\\MSC.Software\\MSC_Nastran\\20122/bin\\nastranw.exe E:\work\611\vte\proj611\proj611_py\Meval_Data 100 50 20
exit

:peval
%py% %input% peval E:\\work\\611\\vte\\proj611\\proj611_py\\aerofoil_product.bdf D:/MSC.Software/MSC_Nastran/20122/bin/nastranw.exe E:\\work\\611\\vte\\proj611\\proj611_py\\Meval_Data
pause
exit

:field
%py% %input% field E:\work\611\vte\aerofoil\shiyan.bdf
pause
exit



