# -*- mode: python ; coding: utf-8 -*-
import sys
import os

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

_version_ns = {}
with open(os.path.join(os.getcwd(), 'cora', '_version.py')) as _vf:
    exec(_vf.read(), _version_ns)
VERSION = _version_ns['__version__']

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

for pkg in ['osmnx', 'geopandas', 'networkx', 'shapely', 'rasterio', 'pyproj', 'pyogrio']:
    metadata = get_pkg_metadata_path(pkg)
    if metadata:
        datas.append(metadata)

# rasterio has no PyInstaller hook: its Cython modules import submodules
# dynamically, and its bundled GDAL/PROJ data must ship with the app.
collected_hiddenimports = []
for pkg in ['rasterio', 'pyogrio', 'osmnx', 'geopandas', 'pyproj']:
    collected_hiddenimports += collect_submodules(pkg)
    datas += collect_data_files(pkg)

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
        'pyogrio',
        'pyogrio._geometry',
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
    ] + collected_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['pyi_rth_gdal_data.py'],
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
    console=False,
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
        bundle_identifier='org.cora.coastal-risk-analyzer',
        version=VERSION,
        info_plist={
            'NSPrincipalClass': 'NSApplication',
            'NSHighResolutionCapable': 'True',
            'LSBackgroundOnly': False,
            'CFBundleName': 'CORA',
            'CFBundleDisplayName': 'CORA - Coastal Risk Analyzer',
            'CFBundleShortVersionString': VERSION,
            'CFBundleVersion': VERSION,
            'LSMinimumSystemVersion': '11.0',
            'NSHumanReadableCopyright': 'Coastal Risk Analyzer (CORA)',
        },
    )