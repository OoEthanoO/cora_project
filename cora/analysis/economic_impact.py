import geopandas as gpd
import numpy as np
from typing import Dict, Tuple

DEFAULT_PROPERTY_VALUES = {
    'residential': 1500, # USD per m^2
    'commercial': 2000,
    'industrial': 800,
    'office': 2500,
    'retail': 2200,
    'hotel': 3000,
    'hospital': 4000,
    'school': 2800,
    'university': 3200,
    'warehouse': 600,
    'garage': 400,
    'church': 1800,
    'civic': 2500,
    'public': 2000,
    'default': 1200
}

DAMAGE_FACTORS = {
    'shallow': 0.15,
    'moderate': 0.35,
    'deep': 0.65
}

def estimate_building_area(geometry) -> float:
    if geometry.geom_type in ['Polygon', 'MultiPolygon']:
        return geometry.area
    elif geometry.geom_type in ['Point', 'MultiPoint']:
        return 150.0
    else:
        return 100.0
    
def classify_building_type(building_row) -> str:
    building_tag = building_row.get('building', '')
    if building_tag in DEFAULT_PROPERTY_VALUES:
        return building_tag
    
    amenity = building_row.get('amenity', '')
    if amenity in DEFAULT_PROPERTY_VALUES:
        return amenity
    
    shop = building_row.get('shop', '')
    if shop and shop != 'nan':
        return 'retail'
    
    landuse = building_row.get('landuse', '')
    if landuse in DEFAULT_PROPERTY_VALUES:
        return landuse
    
    if building_tag in ['house', 'apartments', 'detached', 'terrace']:
        return 'residential'
    elif building_tag in ['commercial', 'office']:
        return building_tag
    elif building_tag in ['industrial', 'warehouse']:
        return building_tag
    
    return 'default'

def estimate_flood_damage_factor(flood_depth_m: float = None) -> float:
    if flood_depth_m is None:
        return DAMAGE_FACTORS['moderate']
    
    if flood_depth_m <= 0.5:
        return DAMAGE_FACTORS['shallow']
    elif flood_depth_m <= 1.5:
        return DAMAGE_FACTORS['moderate']
    else:
        return DAMAGE_FACTORS['deep']
    
def calculate_building_damage(
    flooded_buildings_gdf: gpd.GeoDataFrame,
    property_values: Dict[str, float] = None,
    flood_depth_m: float = None
) -> Tuple[float, Dict[str, float]]:
    if flooded_buildings_gdf is None or flooded_buildings_gdf.empty:
        return 0.0, {}
    
    if property_values is None:
        property_values = DEFAULT_PROPERTY_VALUES

    damage_factor = estimate_flood_damage_factor(flood_depth_m)

    total_damage = 0.0
    damage_by_type = {}

    buildings_for_calc = flooded_buildings_gdf.copy()
    if buildings_for_calc.crs and buildings_for_calc.crs.is_geographic:
        try:
            centroid = buildings_for_calc.unary_union.centroid
            utm_zone = int((centroid.x + 180) / 6) + 1
            hemisphere = 'north' if centroid.y >= 0 else 'south'
            utm_crs = f"EPSG:{32600 + utm_zone if hemisphere == 'north' else 32700 + utm_zone}"
            buildings_for_calc = buildings_for_calc.to_crs(utm_crs)
        except:
            pass

    for idx, building in buildings_for_calc.iterrows():
        building_type = classify_building_type(building)

        building_area = estimate_building_area(building.geometry)

        value_per_m2 = property_values.get(building_type, property_values['default'])

        building_value = building_area * value_per_m2 * damage_factor
        building_damage = building_value * damage_factor

        total_damage += building_damage
        
        if building_type not in damage_by_type:
            damage_by_type[building_type] = 0.0
        damage_by_type[building_type] += building_damage

    return total_damage, damage_by_type

def format_currency(amount: float) -> str:
    if amount >= 1_000_000:
        return f"${amount/1_000_000:.1f}M"
    elif amount >= 1_000:
        return f"${amount/1_000:.0f}K"
    else:
        return f"${amount:.0f}"
    
def calculate_relocation_costs(
    flooded_buildings_gdf: gpd.GeoDataFrame,
    property_values: Dict[str, float] = None,
    relocation_multiplier: float = 1.2
) -> Tuple[float, Dict[str, float]]:
    if flooded_buildings_gdf is None or flooded_buildings_gdf.empty:
        return 0.0, {}
    
    if property_values is None:
        property_values = DEFAULT_PROPERTY_VALUES

    total_relocation_cost = 0.0
    costs_by_type = {}

    buildings_for_calc = flooded_buildings_gdf.copy()
    if buildings_for_calc.crs and buildings_for_calc.crs.is_geographic:
        try:
            centroid = buildings_for_calc.unary_union.centroid
            utm_zone = int((centroid.x + 180) / 6) + 1
            hemisphere = 'north' if centroid.y >= 0 else 'south'
            utm_crs = f"EPSG:{32600 + utm_zone if hemisphere == 'north' else 32700 + utm_zone}"
            buildings_for_calc = buildings_for_calc.to_crs(utm_crs)
        except:
            pass

    for idx, building in buildings_for_calc.iterrows():
        building_type = classify_building_type(building)
        building_area = estimate_building_area(building.geometry)
        value_per_m2 = property_values.get(building_type, property_values['default'])

        replacement_value = building_area * value_per_m2

        relocation_cost = replacement_value * relocation_multiplier

        total_relocation_cost += relocation_cost

        if building_type not in costs_by_type:
            costs_by_type[building_type] = 0.0
        costs_by_type[building_type] += relocation_cost

    return total_relocation_cost, costs_by_type

if __name__ == "__main__":
    print("Testing economic impact estimation...")

    test_building = {
        'building': 'residential',
        'amenity': None,
        'shop': None
    }
    building_type = classify_building_type(test_building)
    print(f"Building type: {building_type}")

    damage_factor = estimate_flood_damage_factor(1.0)
    print(f"Damage factor for 1m flood: {damage_factor}")

    test_amounts = [500, 15000, 1500000, 25000000]
    for amount in test_amounts:
        formatted = format_currency(amount)
        print(f"${amount} -> {formatted}")

    print("Economic impact module test complete.'")