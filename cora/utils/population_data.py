import requests
import rasterio
import numpy as np
import os
from typing import Optional, Tuple
import logging

logging.basicConfig(level=logging.INFO)

class WorldPopHandler:
    BASE_URL = "https://www.worldpop.org/rest/data/pop/wpgppop"

    def __init__(self, cache_dir: str = "population_cache"):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)

    def get_population_raster(self, country_code: str, year: int = 2020) -> Optional[Tuple[np.ndarray, rasterio.transform.Affine, rasterio.crs.CRS]]:
        cache_filename = f"worldpop_{country_code}_{year}.tif"
        cache_path = os.path.join(self.cache_dir, cache_filename)

        if os.path.exists(cache_path):
            logging.info(f"Loading cached population data: {cache_path}")
            try:
                with rasterio.open(cache_path) as src:
                    data = src.read(1)
                    transform = src.transform
                    crs = src.crs
                    
                    print(f"DEBUG: Loaded population data - shape: {data.shape}, dtype: {data.dtype}")
                    print(f"DEBUG: Population data min/max: {np.min(data):.2f} / {np.max(data):.2f}")
                    print(f"DEBUG: Population data has negative values: {np.any(data < 0)}")
                    print(f"DEBUG: Population data has NaN values: {np.isnan(data).any()}")
                    
                    if np.any(data < 0):
                        print("WARNING: Found negative population values, setting to 0")
                        data = np.where(data < 0, 0, data)
                
                return data, transform, crs
            except Exception as e:
                logging.warning(f"Error loading cached file, will re-download: {e}")
        
        try:
            download_url = f"https://data.worldpop.org/GIS/Population/Global_2000_2020_1km_UNadj/{year}/{country_code.upper()}/{country_code.lower()}_ppp_{year}_1km_Aggregated_UNadj.tif"

            logging.info(f"Downloading population data for {country_code} ({year})...")
            response = requests.get(download_url, stream=True, timeout=300)
            response.raise_for_status()

            with open(cache_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            with rasterio.open(cache_path) as src:
                data = src.read(1)
                transform = src.transform
                crs = src.crs
            
            logging.info(f"Population data downloaded and cached: {cache_path}")
            return data, transform, crs
        
        except requests.RequestException as e:
            logging.error(f"Error downloading population data: {e}")
            return None
        except Exception as e:
            logging.error(f"Error processing population data: {e}")
            return None
        
    def estimate_country_from_coords(self, lat: float, lon: float) -> str:
        if 24 <= lat <= 49 and -125 <= lon <= -66:
            return "USA"
        elif 41 <= lat <= 83 and -141 <= lon <= -52:
            return "CAN"
        elif 14 <= lat <= 33 and -118 <= lon <= -86:
            return "MEX"
        else:
            logging.warning(f"Could not determine country for {lat}, {lon}, defaulting to USA")
            return "USA"
        
def calculate_population_exposure(
    flood_mask: np.ndarray,
    flood_transform: rasterio.transform.Affine,
    flood_crs: rasterio.crs.CRS,
    population_array: np.ndarray,
    population_transform: rasterio.transform.Affine,
    population_crs: rasterio.crs.CRS
) -> Tuple[float, dict]:
    try:
        from rasterio.warp import reproject, Resampling
        from rasterio.enums import Resampling

        print(f"DEBUG: Population array shape: {population_array.shape}, dtype: {population_array.dtype}")
        print(f"DEBUG: Population array min/max: {np.min(population_array):.2f} / {np.max(population_array):.2f}")
        print(f"DEBUG: Population array has NaN values: {np.isnan(population_array).any()}")
        print(f"DEBUG: Flood mask shape: {flood_mask.shape}, dtype: {flood_mask.dtype}")
        print(f"DEBUG: Flood mask sum (flooded cells): {np.sum(flood_mask)}")
        print(f"DEBUG: Population CRS: {population_crs}")
        print(f"DEBUG: Flood CRS: {flood_crs}")
        print(f"DEBUG: Population transform: {population_transform}")
        print(f"DEBUG: Flood transform: {flood_transform}")
        
        pop_height, pop_width = population_array.shape
        pop_bounds = rasterio.transform.array_bounds(pop_height, pop_width, population_transform)
        print(f"DEBUG: Population bounds: {pop_bounds}")
        
        flood_height, flood_width = flood_mask.shape
        flood_bounds = rasterio.transform.array_bounds(flood_height, flood_width, flood_transform)
        print(f"DEBUG: Flood bounds: {flood_bounds}")

        pop_reprojected = np.zeros_like(flood_mask, dtype=np.float32)

        reproject(
            source=population_array,
            destination=pop_reprojected,
            src_transform=population_transform,
            src_crs=population_crs,
            dst_transform=flood_transform,
            dst_crs=flood_crs,
            resampling=Resampling.sum
        )

        print(f"DEBUG: Reprojected population shape: {pop_reprojected.shape}, dtype: {pop_reprojected.dtype}")
        print(f"DEBUG: Reprojected population min/max: {np.min(pop_reprojected):.2f} / {np.max(pop_reprojected):.2f}")
        print(f"DEBUG: Reprojected population has NaN values: {np.isnan(pop_reprojected).any()}")
        
        pop_reprojected = np.nan_to_num(pop_reprojected, nan=0.0, posinf=0.0, neginf=0.0)

        pop_reprojected = np.maximum(pop_reprojected, 0.0)

        print(f"DEBUG: After nan_to_num - min/max: {np.min(pop_reprojected):.2f} / {np.max(pop_reprojected):.2f}")

        exposed_population = pop_reprojected * flood_mask.astype(np.float32)
        total_exposed = np.sum(exposed_population)

        valid_pop_mask = pop_reprojected > 0
        total_population_in_area = np.sum(pop_reprojected[valid_pop_mask])

        print(f"DEBUG: Total exposed: {total_exposed:.2f}")
        print(f"DEBUG: Total in area (valid cells only): {total_population_in_area:.2f}")
        print(f"DEBUG: Valid population cells: {np.sum(valid_pop_mask)}")

        total_exposed = max(0.0, float(total_exposed))
        total_population_in_area = max(0.0, float(total_population_in_area))
        
        print(f"DEBUG: After ensuring non-negative - Total exposed: {total_exposed:.2f}")
        print(f"DEBUG: After ensuring non-negative - Total in area: {total_population_in_area:.2f}")

        exposure_percentage = (total_exposed / total_population_in_area * 100) if total_population_in_area > 0 else 0

        stats = {
            'total_exposed': total_exposed,
            'total_in_area': total_population_in_area,
            'exposure_percentage': exposure_percentage,
            'flooded_cells_with_population': np.sum((exposed_population > 0).astype(int))
        }

        return total_exposed, stats
    
    except Exception as e:
        logging.error(f"Error calculating population exposure: {e}")
        return 0.0, {'error': str(e)}
    
if __name__ == "__main__":
    handler = WorldPopHandler()

    pop_data = handler.get_population_raster("USA", 2020)
    if pop_data:
        pop_array, transform, crs = pop_data
        print(f"Population data loaded: {pop_array.shape}, max: {np.max(pop_array)}")
    else:
        print("Failed to load population data")