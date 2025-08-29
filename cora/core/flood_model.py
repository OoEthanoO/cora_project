import numpy as np
import scipy.ndimage
from cora.core.geospatial_utils import is_coastal_edge
from cora.utils.tidal_gauge import get_tidal_baseline
from typing import Optional, Tuple
import logging

def bathtub_inundation(dem: np.ndarray, sea_level: float) -> np.ndarray:
    if not isinstance(dem, np.ndarray):
        raise TypeError("Input DEM must be a NumPy array.")
    if not isinstance(sea_level, (int, float)):
        raise TypeError("Sea level must be a numeric value.")

    return np.where(dem <= sea_level, 1, 0)

def binary_flood_fill(seed_points: np.ndarray, potential_flood_area: np.ndarray) -> np.ndarray:
    if not isinstance(seed_points, np.ndarray) or not isinstance(potential_flood_area, np.ndarray):
        raise TypeError("Inputs seed_points and potential_flood_area must be NumPy arrays.")
    if seed_points.shape != potential_flood_area.shape:
        raise ValueError("Inputs seed_points and potential_flood_area must have the same shape.")
    if seed_points.dtype != bool or potential_flood_area.dtype != bool:
        if seed_points.dtype != bool:
            seed_points = seed_points.astype(bool)
        if potential_flood_area.dtype != bool:
            potential_flood_area = potential_flood_area.astype(bool)

    valid_seed_points = seed_points & potential_flood_area

    filled_area = scipy.ndimage.binary_propagation(
        input=valid_seed_points,
        mask=potential_flood_area
    )
    return filled_area

def connected_flood(dem: np.ndarray, sea_level: float) -> np.ndarray:
    if not isinstance(dem, np.ndarray):
        raise TypeError("Input DEM must be a NumPy array.")
    if dem.ndim != 2:
        raise ValueError("Input DEM must be a 2D array.")
    if not isinstance(sea_level, (int, float)):
        raise TypeError("Sea level must be a numeric value.")

    potential_flood_area = (dem <= sea_level)
    coastal_edges = is_coastal_edge(dem)

    ocean_seed_points = potential_flood_area & coastal_edges

    flood_mask = binary_flood_fill(ocean_seed_points, potential_flood_area)

    return flood_mask

def connected_flood_with_tidal_baseline(
    dem: np.ndarray, 
    slr: float, 
    lat: float, 
    lon: float,
    use_tidal_baseline: bool = True
) -> Tuple[np.ndarray, Optional[dict]]:
    if not isinstance(dem, np.ndarray):
        raise TypeError("Input DEM must be a NumPy array.")
    if dem.ndim != 2:
        raise ValueError("Input DEM must be a 2D array.")
    if not isinstance(slr, (int, float)):
        raise TypeError("Sea level rise must be a numeric value.")
    
    tidal_info = None
    effective_sea_level = slr
    
    if use_tidal_baseline:
        try:
            logging.info(f"Looking up tidal baseline for coordinates ({lat:.4f}, {lon:.4f})")
            baseline, station_info = get_tidal_baseline(lat, lon)
            
            if baseline is not None and station_info is not None:
                effective_sea_level = baseline + slr
                tidal_info = {
                    'baseline_m': baseline,
                    'station_name': station_info['name'],
                    'station_id': station_info['id'],
                    'distance_km': station_info['distance_km'],
                    'effective_sea_level': effective_sea_level
                }
                logging.info(f"Applied tidal baseline: {baseline:.3f}m from station {station_info['name']}")
                logging.info(f"Effective sea level: {effective_sea_level:.3f}m (baseline + {slr:.3f}m SLR)")
            else:
                logging.warning("Could not retrieve tidal baseline, using SLR value directly")
                tidal_info = {'error': 'No tidal data available'}
                
        except Exception as e:
            logging.error(f"Error retrieving tidal baseline: {e}")
            tidal_info = {'error': str(e)}
    
    flood_mask = connected_flood(dem, effective_sea_level)
    
    return flood_mask, tidal_info

if __name__ == '__main__':
    print("Running manual test for bathtub_inundation...")

    sample_dem = np.array([
        [5, 6, 7, 8, 9],
        [3, 4, 5, 6, 7],
        [1, 2, 3, 4, 5],
        [0, 1, 2, 3, 4]
    ], dtype=np.float32)

    print("\nSample DEM:")
    print(sample_dem)
    print(f"Shape: {sample_dem.shape}, Data Type: {sample_dem.dtype}")

    sea_level_1 = 2.5
    flood_mask_1 = bathtub_inundation(sample_dem, sea_level_1)
    print(f"\nTest Case 1: Sea Level = {sea_level_1}")
    print("Flood Mask:")
    print(flood_mask_1)
    print(f"Shape: {flood_mask_1.shape}, Data Type: {flood_mask_1.dtype}")
    print(f"Number of flooded cells: {np.sum(flood_mask_1)}")

    sea_level_2 = 0.0
    flood_mask_2 = bathtub_inundation(sample_dem, sea_level_2)
    print(f"\nTest Case 2: Sea Level = {sea_level_2}")
    print("Flood Mask:")
    print(flood_mask_2)
    print(f"Number of flooded cells: {np.sum(flood_mask_2)}")

    sea_level_3 = 10.0
    flood_mask_3 = bathtub_inundation(sample_dem, sea_level_3)
    print(f"\nTest Case 3: Sea Level = {sea_level_3}")
    print("Flood Mask:")
    print(flood_mask_3)
    print(f"Number of flooded cells: {np.sum(flood_mask_3)}")

    sea_level_4 = -1.0
    flood_mask_4 = bathtub_inundation(sample_dem, sea_level_4)
    print(f"\nTest Case 4: Sea Level = {sea_level_4}")
    print("Flood Mask:")
    print(flood_mask_4)
    print(f"Number of flooded cells: {np.sum(flood_mask_4)}")

    print("\nManual test finished.")

    print("\nRunning manual test for connected_flood...")
    sample_dem_cf = np.array([
        [5, 5, 5, 5, 5],
        [5, 1, 1, 1, 5],
        [5, 1, 0, 1, 5],
        [5, 1, 1, 1, 5],
        [0, 0, 0, 0, 0]
    ], dtype=np.float32)
    sea_level_cf = 0.5

    print("\nSample DEM for connected_flood:")
    print(sample_dem_cf)
    print(f"Sea Level: {sea_level_cf}")

    connected_flood_mask = connected_flood(sample_dem_cf, sea_level_cf)
    print("\nConnected Flood Mask (expected: bottom row True, others False):")
    print(connected_flood_mask)
    print(f"Number of connected flooded cells: {np.sum(connected_flood_mask)}")

    sample_dem_internal = np.array([
        [10, 10, 10, 10, 10],
        [10, 1, 1, 1, 10],
        [10, 1, 0, 1, 10],
        [10, 1, 1, 1, 10],
        [10, 2, 2, 2, 10]
    ], dtype=np.float32)
    sea_level_internal = 2.0
    print("\nSample DEM with internal low area:")
    print(sample_dem_internal)
    print(f"Sea Level: {sea_level_internal}")
    connected_flood_mask_internal = connected_flood(sample_dem_internal, sea_level_internal)
    print("\nConnected Flood Mask (internal low area should NOT be flooded, parts of bottom edge should):")
    print(connected_flood_mask_internal)
    print(f"Number of connected flooded cells: {np.sum(connected_flood_mask_internal)}")

    sample_dem_high_edges = np.array([
        [10, 10, 10],
        [10, 0, 10],
        [10, 10, 10]
    ], dtype=np.float32)
    sea_level_high_edges = 1.0
    print("\nSample DEM with high edges and internal low point:")
    print(sample_dem_high_edges)
    print(f"Sea Level: {sea_level_high_edges}")
    connected_flood_mask_high_edges = connected_flood(sample_dem_high_edges, sea_level_high_edges)
    print("\nConnected Flood Mask (should be all False as no edge seeds are <= sea_level):")
    print(connected_flood_mask_high_edges)
    print(f"Number of connected flooded cells: {np.sum(connected_flood_mask_high_edges)}")

    print("\nManual test for connected_flood finished.")
    
    print("\nTesting tidal baseline integration...")
    test_lat, test_lon = 25.7617, -80.1918
    test_slr = 1.0
    
    try:
        flood_mask_tidal, tidal_info = connected_flood_with_tidal_baseline(
            sample_dem_cf, test_slr, test_lat, test_lon, use_tidal_baseline=True
        )
        print(f"Flood analysis with tidal baseline completed.")
        print(f"Tidal info: {tidal_info}")
        print(f"Flooded cells: {np.sum(flood_mask_tidal)}")
    except Exception as e:
        print(f"Error in tidal baseline test: {e}")
    
    print("\nTidal baseline integration test finished.")