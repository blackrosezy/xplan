# -*- mode: python -*-

##### include mydir in distribution #######
def extra_datas(mydir):
    def rec_glob(p, files):
        import os
        import glob
        for d in glob.glob(p):
            if os.path.isfile(d):
                files.append(d)
            rec_glob("%s/*" % d, files)
    files = []
    rec_glob("%s/*" % mydir, files)
    extra_datas = []
    for f in files:
        extra_datas.append((f, f, 'DATA'))

    return extra_datas
###########################################

a = Analysis(['dialog.py'],
             pathex=['C:\\rozi\\xplan\\xplantool'],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)
a.datas += extra_datas('data')
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='xplantool.exe',
          debug=False,
          strip=None,
          upx=True,
          console=True , icon='icon.ico')
