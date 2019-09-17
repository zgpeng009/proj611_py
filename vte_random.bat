set py=D:\Python27\python2.exe
set input=E:\work\611\vte\proj611\proj611_py\vte_random.py

call:running

:running
%py% %input% running E:\work\611\vte\random\random_product.bdf D:\MSC.Software\MSC_Nastran\20122/bin\nastranw.exe E:\work\611\vte\random
pause
exit

:rand
%py% %input% rand 1226 E:\work\611\vte\random\random_product.f06
pause
exit