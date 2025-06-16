import numpy as np

def is_coastal_edge(dem: np.ndarray) -> np.ndarray:
    if not isinstance(dem, np.ndarray):
        raise TypeError("Input DEM must be a NumPy array.")
    if dem.ndim != 2:
        raise ValueError("Input DEM must be a 2D array.")

    edge_mask = np.zeros_like(dem, dtype=bool)

    edge_mask[0, :] = True
    edge_mask[-1, :] = True

    edge_mask[:, 0] = True
    edge_mask[:, -1] = True

    return edge_mask

if __name__ == '__main__':
    sample_dem = np.array([
        [5, 6, 7, 8, 9],
        [3, 4, 5, 6, 7],
        [1, 2, 3, 4, 5],
        [0, 1, 2, 3, 4]
    ])
    print("Sample DEM:")
    print(sample_dem)

    coastal_edges = is_coastal_edge(sample_dem)
    print("\nCoastal Edge Mask:")
    print(coastal_edges)

    empty_dem = np.array([[]])

    single_row_dem = np.array([[1, 2, 3, 4, 5]])
    print("\nSingle Row DEM:")
    print(single_row_dem)
    coastal_edges_single_row = is_coastal_edge(single_row_dem)
    print("\nCoastal Edge Mask for Single Row DEM:")
    print(coastal_edges_single_row)

    single_col_dem = np.array([[1], [2], [3], [4]])
    print("\nSingle Column DEM:")
    print(single_col_dem)
    coastal_edges_single_col = is_coastal_edge(single_col_dem)
    print("\nCoastal Edge Mask for Single Column DEM:")
    print(coastal_edges_single_col)