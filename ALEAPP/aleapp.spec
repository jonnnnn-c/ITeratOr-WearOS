# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(['aleapp.py'],
             pathex=['.\\scripts\\artifacts'],
             binaries=[],
             datas=[('.\\scripts', '.\\scripts')],
             hiddenimports=['simplekml'],
             hookspath=['.\\'],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='aleapp',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          version='aleapp-file_version_info.txt',
          console=True )