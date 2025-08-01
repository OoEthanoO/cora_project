import os
import osmnx as ox
import logging
import geopandas as gpd
import hashlib
import json

ox.settings.log_console = True
ox.settings.use_cache = True
ox.settings.timeout = 180
logging.basicConfig(level=logging.INFO)

def _get_osm_cache_path(north, south, east, west, tags, cache_dir="cache"):
    os.makedirs(cache_dir, exist_ok=True)
    tags_str = json.dumps(tags, sort_keys=True)
    key_str = f"{north}_{south}_{east}_{west}_{tags_str}"
    hash_digest = hashlib.sha256(key_str.encode()).hexdigest()[:16]
    filename = f"osm_{hash_digest}.geojson"
    return os.path.join(cache_dir, filename)

def fetch_osm_geometries(north, south, east, west, tags):
    cache_path = _get_osm_cache_path(north, south, east, west, tags)
    if os.path.exists(cache_path):
        logging.info(f"Loading OSM data from cache: {cache_path}")
        gdf = gpd.read_file(cache_path)
        return gdf

    bbox = west, south, east, north
    logging.info(f"Fetching OSM data for bbox={bbox} and tags={tags}")
    gdf = ox.features.features_from_bbox(bbox, tags)
    if not gdf.empty:
        gdf.to_file(cache_path, driver="GeoJSON")
        logging.info(f"Saved OSM data to cache: {cache_path}")
    return gdf

def mark_critical_infrastructure(buildings_gdf):
    if buildings_gdf is None or buildings_gdf.empty:
        return buildings_gdf

    critical_amenities = {"hospital", "school", "fire_station", "police", "emergency"}
    def is_critical(row):
        amenity = row.get("amenity", None)
        return amenity in critical_amenities

    if "amenity" not in buildings_gdf.columns:
        buildings_gdf["amenity"] = None

    buildings_gdf["is_critical"] = buildings_gdf.apply(is_critical, axis=1)
    return buildings_gdf

if __name__ == "__main__":
    test_bbox = {
        "north": 40.684755,
        "south": 40.682282,
        "east": -73.945608,
        "west": -73.951536
    }
    test_tags = {"building": True}

    print("--- Testing OSM Fetching for a small bounding box ---")
    print(f"Bounding Box: {test_bbox}")
    print(f"Tags: {test_tags}")

    try:
        geometries_gdf = fetch_osm_geometries(
            north=test_bbox["north"],
            south=test_bbox["south"],
            east=test_bbox["east"],
            west=test_bbox["west"],
            tags=test_tags
        )

        if not geometries_gdf.empty:
            print("\n[SUCCESS] Successfully fetched geometries from OSM.")
            print(f"Number of geometries found: {len(geometries_gdf)}")
            print("GeoDataFrame head:")
            print(geometries_gdf.head())
        else:
            print("\n[INFO] The query was successful, but no building geometries were found for the given area.")

    except Exception as e:
        print(f"\n[ERROR] An error occurred during the test: {e}")

    print("\n--- Test finished ---")
