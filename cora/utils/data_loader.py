import numpy as np
import rasterio
from rasterio.transform import Affine
from rasterio.crs import CRS


def load_dem(tif_path: str) -> tuple[np.ndarray, Affine, CRS]:
    """
    Loads a Digital Elevation Model (DEM) from a GeoTIFF file.

    Args:
        tif_path (str): The file path to the GeoTIFF file.

    Returns:
        tuple[np.ndarray, Affine, CRS]: A tuple containing:
            - The DEM data as a NumPy array.
            - The Affine transformation object.
            - The Coordinate Reference System (CRS) of the DEM.
    """
    with rasterio.open(tif_path) as src:
        dem_array = src.read(1)
        transform = src.transform
        crs = src.crs
    return dem_array, transform, crs


if __name__ == '__main__':
    sample_file_path = None

    try:
        import os

        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        sample_file_path = os.path.join(project_root, 'data', 'output_hh.tif')

        if not os.path.exists(sample_file_path):
            print(f"Test file not found: {sample_file_path}")
            print("Please download a sample SRTM DEM .tif file and place it in `cora_project/data/`")
            print("For example, name it 'sample_dem.tif'.")
        else:
            dem_data, affine_transform, dem_crs = load_dem(sample_file_path)
            print("DEM Loaded Successfully!")
            print(f"DEM Array Shape: {dem_data.shape}")
            print(f"DEM Data Type: {dem_data.dtype}")
            print(f"Affine Transform:\n{affine_transform}")
            print(f"CRS: {dem_crs}")
            print(f"Min elevation: {np.min(dem_data)}")
            print(f"Max elevation: {np.max(dem_data)}")

    except ImportError as e:
        print(f"Import error: {e}. Make sure rasterio and numpy are installed.")
    except rasterio.errors.RasterioIOError as e:
        print(f"Error opening or reading TIFF file: {e}")
        print(f"Ensure the file '{sample_file_path}' is a valid GeoTIFF.")
    except FileNotFoundError:
        print(f"Test file not found: {sample_file_path}")
        print("Please download a sample SRTM DEM .tif file and place it in `cora_project/data/`")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")