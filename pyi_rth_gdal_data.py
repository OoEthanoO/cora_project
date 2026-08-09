"""PyInstaller runtime hook: point GDAL and PROJ at the bundled data.

rasterio normally locates gdal_data/proj_data relative to its installed
package directory. Inside a frozen app that lookup is unreliable, so the
environment variables are set explicitly before rasterio is imported.
"""
import os
import sys

_bundle = getattr(sys, '_MEIPASS', None)

if _bundle:
    _gdal_data = os.path.join(_bundle, 'rasterio', 'gdal_data')
    if os.path.isdir(_gdal_data):
        os.environ.setdefault('GDAL_DATA', _gdal_data)

    for _candidate in (
        os.path.join(_bundle, 'rasterio', 'proj_data'),
        os.path.join(_bundle, 'pyproj', 'proj_dir', 'share', 'proj'),
    ):
        if os.path.isdir(_candidate):
            os.environ.setdefault('PROJ_LIB', _candidate)
            os.environ.setdefault('PROJ_DATA', _candidate)
            break
