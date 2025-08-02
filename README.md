# Coastal Risk Analyzer (CORA) - v0.3.0

CORA (Coastal Risk Analyzer) v0.3.0 significantly enhances the analytical capabilities of the GUI by introducing detailed impact assessment metrics, critical infrastructure identification, and performance improvements. This version allows users to not only visualize flood risk but also quantify its impact on buildings, roads, and critical facilities within a user-defined area of interest.

## Key Features in v0.3.0

- **Detailed Impact Assessment**: The GUI now displays real-time metrics after an analysis, including:
  - Total number of flooded buildings.
  - Total length of flooded roads (in km).
  - Count of flooded critical infrastructure sites (e.g., hospitals, schools).
  - Percentage of specific facilities flooded (e.g., "X% of hospitals in flood zone").
- **Critical Infrastructure Identification**: Automatically tags buildings as 'critical' based on their OSM data (`amenity=hospital`, `school`, `fire_station`, etc.).
- **User-Defined Area of Interest**: Load infrastructure data (buildings, roads) for a specific location by entering a latitude and longitude, which defines the center of the analysis area.
- **OSM Data Caching**: Fetched OpenStreetMap data is cached locally to significantly speed up subsequent analyses of the same area. A "Clear Cache" button is provided for manual control.
- **Performance Enhancements**: Utilizes `rtree` for faster spatial indexing and intersection calculations, making the analysis more efficient.
- **Enhanced User Experience**: The GUI provides status bar messages for long-running operations and more robust error handling.

## Core Functionality (from previous versions)

- **Graphical User Interface (GUI)**: Built with PyQt6 for interactive analysis.
- **Connected Flood Model**: Inundation is calculated based on areas below a specified sea level that are hydrologically connected to the coast.
- **CLI Tool**: The original v0.1.0 command-line interface for simple bathtub modeling remains available.

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
