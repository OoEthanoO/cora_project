import osmnx as ox
import logging

# Configure osmnx to show detailed logs and set a timeout
ox.settings.log_console = True
ox.settings.use_cache = True
ox.settings.timeout = 180
logging.basicConfig(level=logging.INFO)

def fetch_osm_geometries(north, south, east, west, tags):
    """
    Fetch geometries from OpenStreetMap within a given bounding box.
    """
    bbox = west, south, east, north
    logging.info(f"Fetching OSM data for bbox={bbox} and tags={tags}")
    gdf = ox.features.features_from_bbox(bbox, tags)
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
