# Coastal Risk Analyzer (CORA) - v0.2.0

CORA (Coastal Risk Analyzer) v0.2.0 introduces a Graphical User Interface (GUI) for enhanced usability and a more advanced flood modeling approach. While the original command-line tool for basic "bathtub" inundation remains, the primary focus of this version is the GUI which utilizes a "connected flood" model. This model considers hydraulic connectivity to coastal edges, providing a more realistic flood assessment.

## Key Features in v0.2.0

*   **Graphical User Interface (GUI)**: Built with PyQt6 for interactive analysis.
    *   Load Digital Elevation Model (DEM) files (GeoTIFF format).
    *   Adjust Sea Level Rise (SLR) using an intuitive slider.
    *   Perform flood risk analysis using the `connected_flood` model.
    *   Visualize the resulting flood map directly within the application on an embedded Matplotlib canvas.
*   **Connected Flood Model**: Inundation is calculated based on areas below the specified sea level that are also hydrologically connected to coastal seed points.
*   **CLI Tool**: The original v0.1.0 command-line interface for simple bathtub modeling is still available (see `run_cora.py --help`).

## Installation

Ensure you have Python installed. Then, install the necessary dependencies:

```bash
pip install numpy rasterio matplotlib PyQt6
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