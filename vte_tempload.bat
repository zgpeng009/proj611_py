set py=D:\Python27\python2.exe
set input=E:\work\611\vte\proj611\proj611_py\vte_tempload.py

call:running

:run
%py% %input% running E:\work\611\vte\tempload\tempload.bdf D:\MSC.Software\MSC_Nastran\20122/bin\nastranw.exe E:\work\611\vte\tempload
pause
exit