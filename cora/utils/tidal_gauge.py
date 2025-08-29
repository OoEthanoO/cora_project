import requests
import json
import numpy as np
from typing import Optional, Tuple, Dict
import logging

logging.basicConfig(level=logging.INFO)

class NOAATidalGauge:
    BASE_URL = "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter"
    STATIONS_URL = "https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations.json"
    
    def __init__(self):
        self.stations_cache = None
    
    def find_nearest_station(self, lat: float, lon: float, max_distance_km: float = 100) -> Optional[Dict]:
        try:
            if self.stations_cache is None:
                logging.info("Fetching NOAA tidal gauge stations...")
                response = requests.get(self.STATIONS_URL, timeout=30)
                response.raise_for_status()
                self.stations_cache = response.json()
            
            stations = self.stations_cache.get('stations', [])
            
            water_level_stations = [
                station for station in stations 
                if station.get('tidal', False) and 
                   ('datums' in station or 'products' in station)
            ]
            
            if not water_level_stations:
                logging.warning("No water level stations found in NOAA database")
                return None
            
            min_distance = float('inf')
            nearest_station = None
            
            for station in water_level_stations:
                try:
                    station_lat = float(station['lat'])
                    station_lon = float(station['lng'])
                    
                    distance_km = self._calculate_distance(lat, lon, station_lat, station_lon)
                    
                    if distance_km < min_distance and distance_km <= max_distance_km:
                        min_distance = distance_km
                        nearest_station = station
                        nearest_station['distance_km'] = distance_km
                        
                except (ValueError, KeyError) as e:
                    logging.warning(f"Invalid station data: {e}")
                    continue
            
            if nearest_station:
                logging.info(f"Found nearest station: {nearest_station['name']} "
                           f"(ID: {nearest_station['id']}, Distance: {min_distance:.1f} km)")
            else:
                logging.warning(f"No tidal gauge stations found within {max_distance_km} km")
                
            return nearest_station
            
        except requests.RequestException as e:
            logging.error(f"Error fetching tidal gauge stations: {e}")
            return None
        except Exception as e:
            logging.error(f"Unexpected error finding nearest station: {e}")
            return None
    
    def get_mean_sea_level(self, station_id: str, years_back: int = 5) -> Optional[float]:
        try:
            params = {
                'product': 'water_level',
                'application': 'CORA',
                'format': 'json',
                'station': station_id,
                'time_zone': 'gmt',
                'units': 'metric',
                'datum': 'MLLW',
                'range': '30'
            }
            
            logging.info(f"Fetching water level data for station {station_id}...")
            response = requests.get(self.BASE_URL, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if 'data' not in data or not data['data']:
                logging.info(f"No recent water level data, trying monthly means for station {station_id}...")
                params_monthly = {
                    'product': 'monthly_mean',
                    'application': 'CORA',
                    'format': 'json',
                    'station': station_id,
                    'time_zone': 'gmt',
                    'units': 'metric',
                    'datum': 'MLLW',
                    'range': f'{years_back * 12}'
                }
                
                response = requests.get(self.BASE_URL, params=params_monthly, timeout=30)
                response.raise_for_status()
                data = response.json()
                
                if 'data' not in data or not data['data']:
                    logging.warning(f"No mean sea level data available for station {station_id}")
                    return None
            
            water_levels = []
            for record in data['data']:
                try:
                    level = float(record['v'])
                    water_levels.append(level)
                except (ValueError, KeyError):
                    continue
            
            if not water_levels:
                logging.warning(f"No valid water level data for station {station_id}")
                return None
            
            mean_level = np.mean(water_levels)
            logging.info(f"Calculated mean sea level: {mean_level:.3f} m for station {station_id}")
            
            return mean_level
            
        except requests.RequestException as e:
            logging.error(f"Error fetching mean sea level data: {e}")
            return None
        except Exception as e:
            logging.error(f"Unexpected error calculating mean sea level: {e}")
            return None
    
    def get_station_datum_info(self, station_id: str) -> Optional[Dict]:
        try:
            params = {
                'product': 'datums',
                'application': 'CORA',
                'format': 'json',
                'station': station_id,
                'units': 'metric'
            }
            
            response = requests.get(self.BASE_URL, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if 'datums' in data:
                return data['datums']
            else:
                logging.warning(f"No datum information available for station {station_id}")
                return None
                
        except requests.RequestException as e:
            logging.error(f"Error fetching datum information: {e}")
            return None
        except Exception as e:
            logging.error(f"Unexpected error getting datum info: {e}")
            return None
    
    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        R = 6371
        
        lat1_rad = np.radians(lat1)
        lat2_rad = np.radians(lat2)
        delta_lat = np.radians(lat2 - lat1)
        delta_lon = np.radians(lon2 - lon1)
        
        a = (np.sin(delta_lat / 2) ** 2 + 
             np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(delta_lon / 2) ** 2)
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
        
        return R * c

def get_tidal_baseline(lat: float, lon: float) -> Tuple[Optional[float], Optional[Dict]]:
    gauge = NOAATidalGauge()
    
    station = gauge.find_nearest_station(lat, lon)
    if not station:
        return None, None
    
    mean_level = gauge.get_mean_sea_level(station['id'])
    if mean_level is None:
        return None, station
    
    return mean_level, station

if __name__ == "__main__":
    test_lat, test_lon = 25.7617, -80.1918
    
    print(f"Testing tidal gauge integration for Miami ({test_lat}, {test_lon})")
    
    gauge = NOAATidalGauge()
    
    station = gauge.find_nearest_station(test_lat, test_lon)
    if station:
        print(f"\nNearest station: {station['name']}")
        print(f"Station ID: {station['id']}")
        print(f"Distance: {station['distance_km']:.1f} km")
        
        mean_level = gauge.get_mean_sea_level(station['id'])
        if mean_level is not None:
            print(f"Mean sea level: {mean_level:.3f} m")
        else:
            print("Could not retrieve mean sea level data")
    else:
        print("No nearby tidal gauge station found")
    
    print("\nTesting convenience function:")
    baseline, station_info = get_tidal_baseline(test_lat, test_lon)
    if baseline is not None:
        print(f"Tidal baseline: {baseline:.3f} m")
        print(f"Station: {station_info['name']}")
    else:
        print("Could not establish tidal baseline")