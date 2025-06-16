import numpy as np

def bathtub_inundation(dem: np.ndarray, sea_level: float) -> np.ndarray:
    if not isinstance(dem, np.ndarray):
        raise TypeError("Input DEM must be a NumPy array.")
    if not isinstance(sea_level, (int, float)):
        raise TypeError("Sea level must be a numeric value.")

    return np.where(dem <= sea_level, 1, 0)

if __name__ == '__main__':
    print("Running manual test for bathtub_inundation...")

    sample_dem = np.array([
        [5, 6, 7, 8, 9],
        [3, 4, 5, 6, 7],
        [1, 2, 3, 4, 5],
        [0, 1, 2, 3, 4]
    ], dtype=np.float32)

    print("\nSample DEM:")
    print(sample_dem)
    print(f"Shape: {sample_dem.shape}, Data Type: {sample_dem.dtype}")

    sea_level_1 = 2.5
    flood_mask_1 = bathtub_inundation(sample_dem, sea_level_1)
    print(f"\nTest Case 1: Sea Level = {sea_level_1}")
    print("Flood Mask:")
    print(flood_mask_1)
    print(f"Shape: {flood_mask_1.shape}, Data Type: {flood_mask_1.dtype}")
    print(f"Number of flooded cells: {np.sum(flood_mask_1)}")

    sea_level_2 = 0.0
    flood_mask_2 = bathtub_inundation(sample_dem, sea_level_2)
    print(f"\nTest Case 2: Sea Level = {sea_level_2}")
    print("Flood Mask:")
    print(flood_mask_2)
    print(f"Number of flooded cells: {np.sum(flood_mask_2)}")

    sea_level_3 = 10.0
    flood_mask_3 = bathtub_inundation(sample_dem, sea_level_3)
    print(f"\nTest Case 3: Sea Level = {sea_level_3}")
    print("Flood Mask:")
    print(flood_mask_3)
    print(f"Number of flooded cells: {np.sum(flood_mask_3)}")

    sea_level_4 = -1.0
    flood_mask_4 = bathtub_inundation(sample_dem, sea_level_4)
    print(f"\nTest Case 4: Sea Level = {sea_level_4}")
    print("Flood Mask:")
    print(flood_mask_4)
    print(f"Number of flooded cells: {np.sum(flood_mask_4)}")

    print("\nManual test finished.")