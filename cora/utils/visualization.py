import numpy as np
import matplotlib.pyplot as plt
import os


def export_flood_map_png(flood_mask: np.ndarray, output_filepath: str):
    if not isinstance(flood_mask, np.ndarray):
        raise TypeError("Input flood_mask must be a NumPy array.")
    if not isinstance(output_filepath, str):
        raise TypeError("Output filepath must be a string.")
    if not output_filepath.lower().endswith(".png"):
        raise ValueError("Output filepath must end with .png")

    output_dir = os.path.dirname(output_filepath)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    plt.figure()
    plt.imshow(flood_mask, cmap='Blues')
    plt.title("Flood Inundation Map")
    plt.xlabel("X-coordinate")
    plt.ylabel("Y-coordinate")
    plt.colorbar(label="Flood Status (1=Flooded, 0=Dry)")
    plt.savefig(output_filepath)
    plt.close()
    print(f"Flood map saved to: {output_filepath}")


if __name__ == '__main__':
    print("Running manual test for export_flood_map_png...")

    sample_flood_mask = np.array([
        [0, 0, 0, 1, 1],
        [0, 0, 1, 1, 1],
        [0, 1, 1, 1, 0],
        [1, 1, 1, 0, 0]
    ], dtype=np.int8)

    print("\nSample Flood Mask:")
    print(sample_flood_mask)

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    output_directory = os.path.join(project_root, 'output')
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    test_output_filepath = os.path.join(output_directory, 'test_flood_map.png')

    print(f"\nAttempting to save to: {test_output_filepath}")
    try:
        export_flood_map_png(sample_flood_mask, test_output_filepath)
        print(f"Manual test successful. Check the image at '{test_output_filepath}'")
    except Exception as e:
        print(f"An error occurred during the manual test: {e}")

    empty_mask = np.array([[]], dtype=np.int8)
    test_output_filepath_empty = os.path.join(output_directory, 'test_empty_flood_map.png')
    print(f"\nAttempting to save empty mask to: {test_output_filepath_empty}")
    try:
        export_flood_map_png(empty_mask, test_output_filepath_empty)
    except Exception as e:
        print(f"An error occurred with empty mask: {e}")

    large_mask = np.random.randint(0, 2, size=(100, 100), dtype=np.int8)
    test_output_filepath_large = os.path.join(output_directory, 'test_large_flood_map.png')
    print(f"\nAttempting to save large mask to: {test_output_filepath_large}")
    try:
        export_flood_map_png(large_mask, test_output_filepath_large)
        print(f"Manual test successful for large mask. Check the image at '{test_output_filepath_large}'")
    except Exception as e:
        print(f"An error occurred with large mask: {e}")

    print("\nManual test for export_flood_map_png finished.")