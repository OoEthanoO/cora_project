# Coastal Risk Analyzer (CORA) - v0.4.0

CORA (Coastal Risk Analyzer) v0.4.0 introduces improved user experience for sea wall drawing and DEM loading. If a user attempts to load a new DEM file while drawing a sea wall, the GUI now prompts for confirmation and cancels the current drawing if confirmed, or continues drawing if cancelled. This version also includes bug fixes for sea wall preview removal and drawing mode transitions.

## Key Features in v0.4.0

- **Sea Wall Drawing Confirmation:** When loading a new DEM during wall drawing, the user is prompted to confirm. If confirmed, the drawing mode is exited and the wall is discarded; if cancelled, drawing continues.
- **Robust Wall Preview Removal:** Improved logic prevents errors when removing wall preview lines after axes are cleared.
- **General Bug Fixes:** Enhanced error handling and UI feedback for drawing and analysis operations.

## Key Features in v0.3.0

- **Detailed Impact Assessment:** The GUI displays real-time metrics after an analysis, including:
  - Total number of flooded buildings.
  - Total length of flooded roads (in km).
  - Count of flooded critical infrastructure sites (e.g., hospitals, schools).
  - Percentage of specific facilities flooded (e.g., "X% of hospitals in flood zone").
- **Critical Infrastructure Identification:** Automatically tags buildings as 'critical' based on their OSM data (`amenity=hospital`, `school`, `fire_station`, etc.).
- **User-Defined Area of Interest:** Load infrastructure data (buildings, roads) for a specific location by entering a latitude and longitude, which defines the center of the analysis area.
- **OSM Data Caching:** Fetched OpenStreetMap data is cached locally to significantly speed up subsequent analyses of the same area. A "Clear Cache" button is provided for manual control.
- **Performance Enhancements:** Utilizes `rtree` for faster spatial indexing and intersection calculations, making the analysis more efficient.
- **Enhanced User Experience:** The GUI provides status bar messages for long-running operations and more robust error handling.

## Installation

Ensure you have Python installed. Then, install the necessary dependencies:

```bash
pip install numpy rasterio matplotlib PyQt6 osmnx rtree geopandas
```

## Running the GUI

To launch the CORA GUI, run the `cora_gui.py` script:

```bash
python cora_gui.py
```

## Using the CLI (Legacy Bathtub Model)

To use the command-line tool for the basic bathtub model:

```bash
python run_cora.py --dem_path /path/to/your/dem.tif --sea_level <level> --output_path /path/to/your/output.png
```

For more CLI options, use:

```bash
python run_cora.py --help
```
