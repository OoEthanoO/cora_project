import argparse
import sys
try:
    from cora.utils.data_loader import load_dem
    from cora.core.flood_model import bathtub_inundation
    from cora.utils.visualization import export_flood_map_png
except ImportError as e:
    print(f"Error: Could not import CORA modules. {e}")
    print("Please ensure that the 'cora' package is correctly structured and accessible.")

    def load_dem():
        raise ModuleNotFoundError("Cannot load DEM: Required CORA module not found")

    def bathtub_inundation():
        raise ModuleNotFoundError("Cannot perform inundation: Required CORA module not found")

    def export_flood_map_png():
        raise ModuleNotFoundError("Cannot export flood map: Required CORA module not found")

    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Coastal Risk Analyzer (CORA) CLI - Perform bathtub flood modeling."
    )

    parser.add_argument(
        "--dem_path",
        required=True,
        help="Path to the Digital Elevation Model (DEM) GeoTIFF file."
    )
    parser.add_argument(
        "--sea_level",
        type=float,
        required=True,
        help="Sea level value (in units consistent with DEM) for inundation analysis."
    )
    parser.add_argument(
        "--output_path",
        required=True,
        help="Path to save the output flood map PNG file."
    )

    args = parser.parse_args()

    try:
        print(f"1. Loading DEM from: '{args.dem_path}'...")
        dem_data, affine_transform = load_dem(args.dem_path)
        print(f"   DEM loaded successfully. Shape: {dem_data.shape}, dtype: {dem_data.dtype}.")
        if affine_transform:
            print(f"   Affine transform: {affine_transform}")

        print(f"2. Calculating bathtub inundation for sea level: {args.sea_level}...")
        flood_mask = bathtub_inundation(dem_data, args.sea_level)
        flooded_cell_count = flood_mask.sum()
        total_cells = flood_mask.size
        percentage_flooded = (flooded_cell_count / total_cells) * 100 if total_cells > 0 else 0
        print(f"   Inundation calculated. Flooded cells: {flooded_cell_count}/{total_cells} "
              f"({percentage_flooded:.2f}%).")

        print(f"3. Exporting flood map to: '{args.output_path}'...")
        export_flood_map_png(flood_mask, args.output_path)

        print(f"\nProcessing complete. Flood map saved to '{args.output_path}'")

    except FileNotFoundError:
        print(f"Error: DEM file not found at '{args.dem_path}'. Please check the path.")
        sys.exit(1)
    except ImportError as import_error:
        print(f"Error: A required library is missing. {import_error}")
        sys.exit(1)
    except Exception as exception_error:
        if 'rasterio' in str(type(exception_error)).lower() and 'ioerror' in str(type(exception_error)).lower():
            print(f"Error reading DEM file '{args.dem_path}': {exception_error}")
            print("Ensure the file is a valid GeoTIFF and accessible.")
        elif isinstance(exception_error, TypeError):
            print(f"Error: Invalid data type provided. {exception_error}")
        else:
            print(f"An unexpected error occurred: {exception_error}")
        sys.exit(1)


if __name__ == "__main__":
    main()