import numpy as np
from shapely.geometry import LineString
from rasterio.transform import Affine
import rasterio.features

def rasterize_line(line: LineString, dem_shape: tuple, transform: Affine) -> np.ndarray:
    if not isinstance(line, LineString):
        raise TypeError("Input 'line' must be a shapely LineString.")

    rasterized_line_mask = rasterio.features.rasterize(
        shapes=[(line, 1)],
        out_shape=dem_shape,
        transform=transform,
        fill=0,
        dtype=np.uint8
    )

    pixel_coords = np.argwhere(rasterized_line_mask == 1)

    return pixel_coords

def apply_sea_wall(
    dem: np.ndarray,
    wall_line: LineString,
    wall_height: float,
    transform: Affine
) -> np.ndarray:
    modified_dem = dem.copy()

    wall_pixels = rasterize_line(wall_line, dem.shape, transform)

    if wall_pixels.size > 0:
        rows, cols = wall_pixels[:, 0], wall_pixels[:, 1]

        current_elevations = modified_dem[rows, cols]
        new_elevations = np.maximum(current_elevations, wall_height)
        modified_dem[rows, cols] = new_elevations

    return modified_dem
