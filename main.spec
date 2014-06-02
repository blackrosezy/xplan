# -*- mode: python -*-
a = Analysis(['dialog.py'],
             pathex=[os.path.dirname(os.path.realpath(__file__))],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          Tree('images', prefix='images'),
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='xplantool.exe',
          debug=False,
          strip=None,
          upx=True,
          console=True , icon='icon.ico')
