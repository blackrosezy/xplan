@echo off

REM build app
start pyuic4 xplan.ui -o xplanUI.py
pyrcc4 -o resource_rc.py resource.qrc

REM build dist
pyinstaller main.spec
copy main.exe.manifest dist\xplantool.exe.manifest /Y