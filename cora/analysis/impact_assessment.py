import numpy as np
import geopandas as gpd
from shapely.geometry import shape
import rasterio.features

def count_flooded_buildings(buildings_gdf: gpd.GeoDataFrame, flood_mask: np.ndarray, dem_transform) -> int:
    if buildings_gdf is None or buildings_gdf.empty:
        return 0

    if hasattr(buildings_gdf, 'crs') and buildings_gdf.crs is not None:
        pass
    else:
        raise ValueError("buildings_gdf must have a valid CRS.")

    flooded_count = 0
    for geom in buildings_gdf.geometry:
        if geom.is_empty:
            continue
        centroid = geom.centroid
        col, row = ~dem_transform * (centroid.x, centroid.y)
        row, col = int(round(row)), int(round(col))
        if (0 <= row < flood_mask.shape[0]) and (0 <= col < flood_mask.shape[1]):
            if flood_mask[row, col]:
                flooded_count += 1
    return flooded_count

def raster_to_vector_polygons(raster_array: np.ndarray, transform) -> gpd.GeoDataFrame:
    mask_int = raster_array.astype(np.uint8)
    shapes_gen = rasterio.features.shapes(mask_int, mask=mask_int.astype(bool), transform=transform)
    polygons = []
    values = []
    for geom, value in shapes_gen:
        if value == 1:
            polygons.append(shape(geom))
            values.append(value)
    gdf = gpd.GeoDataFrame({'geometry': polygons, 'value': values})
    return gdf

def find_intersecting_features(infra_gdf: gpd.GeoDataFrame, flood_polygons_gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    if infra_gdf is None or infra_gdf.empty or flood_polygons_gdf is None or flood_polygons_gdf.empty:
        return gpd.GeoDataFrame(columns=infra_gdf.columns)

    if infra_gdf.crs != flood_polygons_gdf.crs:
        flood_polygons_gdf = flood_polygons_gdf.to_crs(infra_gdf.crs)

    infra_gdf = infra_gdf.copy().reset_index(drop=True)
    flood_polygons_gdf = flood_polygons_gdf.copy().reset_index(drop=True)

    intersecting_gdf = gpd.overlay(infra_gdf, flood_polygons_gdf, how='intersection')
    return intersecting_gdf
