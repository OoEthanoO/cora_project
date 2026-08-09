# Coastal Risk Analyzer (CORA) - v0.5.0

CORA (Coastal Risk Analyzer) v0.5.0 introduces comprehensive population exposure analysis, wetland restoration modeling, tidal gauge integration, and professional PDF reporting capabilities. This major release significantly enhances CORA's ability to assess climate adaptation strategies and provide detailed impact assessments for coastal communities.

## Key Features in v0.5.0

- **Population Exposure Analysis:** Integration with WorldPop demographic data to calculate exposed population counts and percentages during flood events. Supports automatic country detection and population raster processing.
- **Tidal Gauge Integration:** Real-time integration with NOAA tidal gauge stations to establish accurate sea level baselines. Automatically finds the nearest tidal station and applies measured mean sea level data for more accurate flood modeling.
- **Wetland Restoration Modeling:** Interactive wetland area drawing tool that simulates flood reduction benefits of wetland restoration projects. Users can draw wetland polygons and apply configurable flood reduction factors.
- **Professional PDF Reports:** Comprehensive PDF report generation including analysis summaries, impact metrics, flood maps, methodology descriptions, and adaptation strategy details.
- **Enhanced Adaptation Strategies:** Improved sea wall drawing with configurable heights and wetland restoration areas with flood reduction modeling.
- **Advanced Flood Modeling:** Connected flood algorithm with tidal baseline integration for more accurate coastal inundation predictions.
- **Economic Impact Assessment:** Detailed building damage calculations with standardized property values and depth-damage functions.

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
pip install numpy rasterio matplotlib PyQt6 osmnx rtree geopandas requests pyproj shapely reportlab
```

## Building the macOS Installer

To produce a standalone `CORA.app` and a `.dmg` installer:

```bash
python3.11 -m venv .venv
.venv/bin/pip install -r requirements.txt pyinstaller
./build_macos.sh
```

The disk image is written to `dist/CORA-<version>.dmg`. Pass `--skip-app` to
repackage an existing `dist/CORA.app` without rebuilding it.

The build is ad-hoc signed rather than signed with an Apple Developer ID, so
the first launch requires right-click → **Open** to get past Gatekeeper. The
bundled app stores its settings, DEM downloads and caches in
`~/Library/Application Support/CORA`; running from a source checkout keeps
using the project directory as before.

## Website

The download and presentation site lives in [`web/`](web/) and is a static
Next.js app. After building the installer, stage it for the site with:

```bash
cd web && npm install && npm run stage-release && npm run dev
```

See [`web/README.md`](web/README.md) for deployment and for how to point the
download button at a hosted release asset.

## Running the GUI

To launch the CORA GUI, run the `cora_gui.py` script:

```bash
python cora_gui.py
```

### GUI Features

- **DEM Management:** Load local DEM files or download Copernicus DEM data directly (requires OpenTopography API key)
- **Interactive Analysis:** Set coordinates, buffer zones, and sea level rise scenarios
- **Infrastructure Loading:** Fetch and display buildings and roads from OpenStreetMap
- **Adaptation Planning:** Draw sea walls and wetland restoration areas
- **Real-time Results:** View population exposure, economic damage, and infrastructure impacts
- **Professional Reporting:** Export comprehensive PDF reports with maps and analysis results

## Using the CLI (Legacy Bathtub Model)

To use the command-line tool for the basic bathtub model:

```bash
python run_cora.py --dem_path /path/to/your/dem.tif --sea_level <level> --output_path /path/to/your/output.png
```

For more CLI options, use:

```bash
python run_cora.py --help
```

## New in v0.5.0: Advanced Capabilities

### Population Exposure Analysis
CORA now automatically downloads and processes WorldPop demographic data to calculate population exposure during flood events. The system provides both absolute numbers and percentage exposure metrics.

### Tidal Baseline Integration
Real-time integration with NOAA tidal gauge stations ensures flood models use accurate local sea level baselines rather than generic elevations, significantly improving prediction accuracy for coastal areas.

### Adaptation Strategy Modeling
- **Sea Walls:** Draw custom sea wall alignments with configurable heights to test coastal protection effectiveness
- **Wetland Restoration:** Model the flood reduction benefits of wetland restoration projects with evidence-based reduction factors

### Professional Reporting
Generate comprehensive PDF reports including:
- Analysis parameters and methodology
- Infrastructure impact summaries
- Economic damage assessments
- Population exposure statistics
- High-resolution flood inundation maps
- Adaptation strategy effectiveness
