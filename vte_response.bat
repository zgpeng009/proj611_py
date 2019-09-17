set py=D:\Python27\python2.exe
set input=E:\work\611\vte\proj611\proj611_py\vte_response.py

call:run

:running
%py% %input% running E:\work\611\vte\response\response_product.bdf D:\MSC.Software\MSC_Nastran\20122/bin\nastranw.exe E:\work\611\vte\response
pause
exit

:resp
%py% %input% resp 1226 E:\work\611\vte\response\\response_product.f06
pause
exit

:correlation
%py% %input% correlation E:\\work\\611\\vte\\proj611\\proj611_py\\Result_Data\xx_loadInfo.txt E:\\work\\611\vte\\proj611\\proj611_py\\Result_Data\test_data_physical.txt E:\\work\\611\vte\\proj611\\proj611_py\\Result_Data\test_data_virtual.txt
pause
exit