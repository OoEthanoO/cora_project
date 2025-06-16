# Coastal Risk Analyzer (CORA) - v0.1.0

CORA (Coastal Risk Analyzer) v0.1.0 is a command-line tool for performing basic flood inundation modeling. Given a Digital Elevation Model (DEM) and a specified sea level, it generates a flood map indicating areas at or below that sea level. This version utilizes a simple "bathtub" model, meaning it considers all land below the specified sea level as inundated, without accounting for hydraulic connectivity.

## Installation

Ensure you have Python installed. Then, install the necessary dependencies:

```bash
pip install numpy rasterio matplotlib