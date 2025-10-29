# -*- mode: python ; coding: utf-8 -*-
import sys
import os

block_cipher = None

def get_pkg_metadata_path(package_name):
    """Get the path to package metadata"""
    import importlib.metadata
    try:
        dist = importlib.metadata.distribution(package_name)
        if dist._path:
            return (str(dist._path), f'{package_name}.dist-info')
    except:
        pass
    return None

datas = [
    ('cora', 'cora'),
]

for pkg in ['osmnx', 'geopandas', 'networkx', 'shapely', 'rasterio', 'pyproj', 'fiona']:
    metadata = get_pkg_metadata_path(pkg)
    if metadata:
        datas.append(metadata)

a = Analysis(
    ['cora_gui.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'rasterio',
        'rasterio._shim',
        'rasterio.control',
        'rasterio.crs',
        'rasterio.sample',
        'rasterio.vrt',
        'rasterio.warp',
        'rasterio.enums',
        'rasterio.transform',
        'rasterio._env',
        'rasterio.errors',
        
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'PyQt6.sip',
        
        'matplotlib.backends.backend_qtagg',
        'matplotlib.backends.backend_qt5agg',
        
        'geopandas',
        'geopandas.datasets',
        'shapely',
        'shapely.geometry',
        'fiona',
        'fiona.schema',
        'pyproj',
        'pyproj.datadir',
        
        'scipy',
        'scipy.ndimage',
        'scipy.spatial',
        'numpy',
        
        'reportlab.platypus',
        'reportlab.lib',
        'reportlab.lib.pagesizes',
        'reportlab.lib.styles',
        'reportlab.lib.units',
        'reportlab.lib.colors',
        
        'osmnx',
        'networkx',
        'networkx.algorithms',
        
        'requests',
        'urllib3',
        
        'pkg_resources',
        'pkg_resources.py2_warn',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='CORA',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.icns' if sys.platform == 'darwin' else 'icon.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='CORA',
)

if sys.platform == 'darwin':
    app = BUNDLE(
        coll,
        name='CORA.app',
        icon='icon.icns',
        bundle_identifier='com.yourcompany.cora',
        info_plist={
            'NSPrincipalClass': 'NSApplication',
            'NSHighResolutionCapable': 'True',
            'LSBackgroundOnly': False,
        },
    )