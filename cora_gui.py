import os
import sys
import shutil
import osmnx as ox
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QDockWidget, QSlider, QMessageBox,
    QFileDialog
)
from PyQt6.QtCore import Qt
import pyproj
import rasterio
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import numpy as np

from cora.utils.data_loader import load_dem
from cora.core.flood_model import connected_flood
from cora.utils.osm_handler import fetch_osm_geometries


class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.subplots()
        super().__init__(self.fig)
        self.setParent(parent)

        self.axes.set_title("Map Canvas")
        self.axes.set_xlabel("X-coordinate")
        self.axes.set_ylabel("Y-coordinate")
        self.fig.tight_layout()

    def plot_flood_mask(self, flood_mask_array: np.ndarray, extent=None):
        if not isinstance(flood_mask_array, np.ndarray):
            print("Warning: plot_flood_mask expects a NumPy array.")
            self.axes.clear()
            self.axes.text(0.5, 0.5, "Invalid data for flood mask",
                           horizontalalignment='center', verticalalignment='center',
                           transform=self.axes.transAxes)
            self.axes.set_title("Map Canvas - Error")
            self.draw()
            return

        self.axes.clear()
        if flood_mask_array.size == 0 or (flood_mask_array.ndim == 2 and flood_mask_array.shape[0] == 0 and flood_mask_array.shape[1] == 0):
            self.axes.text(0.5, 0.5, "No data to display",
                           horizontalalignment='center', verticalalignment='center',
                           transform=self.axes.transAxes)
            self.axes.set_title("Map Canvas - No Data")
        else:
            im = self.axes.imshow(flood_mask_array, cmap='Blues', origin='upper', extent=extent)
            self.axes.set_title("Flood Inundation Map")
            self.axes.set_xlabel("X-coordinate")
            self.axes.set_ylabel("Y-coordinate")

        self.fig.tight_layout()
        self.draw()

    def plot_geodataframe(self, gdf, **plot_kwargs):
        gdf.plot(ax=self.axes, **plot_kwargs)
        self.draw()


class CoraGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.slr_value_label = QLabel()
        self.slr_slider = QSlider(Qt.Orientation.Horizontal)

        self.dem_array: np.ndarray | None = None
        self.dem_transform = None
        self.dem_crs = None
        self.current_dem_path: str | None = None
        self.buildings_gdf = None

        self.initUI()

    def initUI(self):
        self.setWindowTitle('CORA - Coastal Risk Analyzer GUI')
        self.setGeometry(100, 100, 800, 600)

        self.map_canvas = MplCanvas(self, width=7, height=5, dpi=100)
        self.setCentralWidget(self.map_canvas)

        initial_map_data = np.zeros((10, 10))
        self.map_canvas.plot_flood_mask(initial_map_data)

        self.controls_dock = QDockWidget("Controls", self)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.controls_dock)

        dock_widget_content = QWidget()
        dock_layout = QVBoxLayout(dock_widget_content)

        self.load_dem_button = QPushButton("Load DEM File...")
        self.load_dem_button.clicked.connect(self._load_dem_via_dialog)
        dock_layout.addWidget(self.load_dem_button)

        self.load_osm_button = QPushButton("Load Buildings")
        self.load_osm_button.clicked.connect(self._load_osm_buildings)
        dock_layout.addWidget(self.load_osm_button)

        self.clear_cache_button = QPushButton("Clear OSM Cache")
        self.clear_cache_button.clicked.connect(self._clear_osm_cache)
        dock_layout.addWidget(self.clear_cache_button)

        self.analyze_button = QPushButton("Analyze Flood Risk")
        self.analyze_button.clicked.connect(self._run_analysis)
        dock_layout.addWidget(self.analyze_button)

        lat_layout = QHBoxLayout()
        self.lat_label = QLabel("Latitude:")
        self.lat_input = QLineEdit()
        self.lat_input.setPlaceholderText("e.g., 25.7617")
        lat_layout.addWidget(self.lat_label)
        lat_layout.addWidget(self.lat_input)
        dock_layout.addLayout(lat_layout)

        lon_layout = QHBoxLayout()
        self.lon_label = QLabel("Longitude:")
        self.lon_input = QLineEdit()
        self.lon_input.setPlaceholderText("e.g., -80.1918")
        lon_layout.addWidget(self.lon_label)
        lon_layout.addWidget(self.lon_input)
        dock_layout.addLayout(lon_layout)

        slr_layout = QHBoxLayout()
        self.slr_label_text = QLabel("SLR:")
        slr_layout.addWidget(self.slr_label_text)

        self.slr_slider.setRange(0, 200)
        self.slr_slider.setValue(50)
        self.slr_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.slr_slider.setTickInterval(10)
        slr_layout.addWidget(self.slr_slider)

        slr_layout.addWidget(self.slr_value_label)
        dock_layout.addLayout(slr_layout)

        self.slr_slider.valueChanged.connect(self._on_slr_slider_changed)
        self._on_slr_slider_changed(self.slr_slider.value())

        dock_layout.addStretch(1)
        self.controls_dock.setWidget(dock_widget_content)

    def _clear_osm_cache(self):
        try:
            if hasattr(ox, 'utils') and hasattr(ox.utils, 'clear_cache'):
                ox.utils.clear_cache()
                QMessageBox.information(self, "Cache Cleared", "OSM cache has been successfully cleared.")
            else:
                cache_folder = 'cache'
                if os.path.exists(cache_folder):
                    shutil.rmtree(cache_folder)
                    os.makedirs(cache_folder)
                    QMessageBox.information(self, "Cache Cleared", f"OSM cache folder '{cache_folder}' has been successfully cleared.")
                else:
                    QMessageBox.warning(self, "Cache Clear Error", f"An error occurred while clearing the cache: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Cache Clear Error", f"An error occurred while clearing the cache: {e}")

    def _load_osm_buildings(self):
        if self.dem_array is None or self.dem_transform is None or self.dem_crs is None:
            QMessageBox.warning(self, "OSM Load Error", "Please load a DEM file first.")
            return

        height, width = self.dem_array.shape
        bounds = rasterio.transform.array_bounds(height, width, self.dem_transform)

        src_crs = self.dem_crs
        dst_crs = pyproj.CRS("EPSG:4326")

        transformer = pyproj.Transformer.from_crs(src_crs, dst_crs, always_xy=True)

        west, south = transformer.transform(bounds[0], bounds[1])
        east, north = transformer.transform(bounds[2], bounds[3])

        if north < south:
            north, south = south, north
        if east < west:
            east, west = west, east

        bbox_info = f"N={north:.4f}, S={south:.4f}, E={east:.4f}, W={west:.4f}"
        reply = QMessageBox.question(self, "Confirm Bounding Box",
                                     f"About to fetch building data for the following bounding box (WGS84):\n\n{bbox_info}\n\nIs this correct?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.Yes)

        if reply == QMessageBox.StandardButton.No:
            QMessageBox.information(self, "Operation Cancelled", "OSM data fetch cancelled by user.")
            return

        tags = {"building": True}

        try:
            print(f"Fetching OSM building data for bbox: N={north}, S={south}, E={east}, W={west}")
            self.buildings_gdf = fetch_osm_geometries(north, south, east, west, tags)
            
            count = len(self.buildings_gdf) if self.buildings_gdf is not None else 0
            print(f"Buildings GDF loaded, count: {count}")

            if self.buildings_gdf is not None and not self.buildings_gdf.empty:
                QMessageBox.information(self, "OSM Data Loaded", f"Successfully fetched {count} building geometries.")

                if self.buildings_gdf.crs is None:
                    self.buildings_gdf.set_crs("EPSG:4326", inplace=True)

                projected_gdf = self.buildings_gdf.to_crs(self.dem_crs)

                self.map_canvas.plot_geodataframe(projected_gdf, facecolor='none', edgecolor='blue', linewidth=0.5)
            else:
                QMessageBox.warning(self, "OSM Data", "No building geometries were found for the given area.")

        except Exception as e:
            error_message = f"Failed to fetch OSM data: {e}"
            print(error_message)
            QMessageBox.critical(self, "OSM Load Error", error_message)
            self.buildings_gdf = None

    def _on_slr_slider_changed(self, value):
        slr_meters = value / 100.0
        self.slr_value_label.setText(f"{slr_meters:.2f}m")

    def _load_dem_via_dialog(self):
        data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
        start_dir = data_dir if os.path.isdir(data_dir) else os.path.expanduser("~")

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open DEM File",
            start_dir,
            "GeoTIFF Files (*.tif *.tiff);;All Files (*)"
        )

        if not file_path:
            return

        self.current_dem_path = file_path

        try:
            print(f"Loading DEM from: {self.current_dem_path}...")
            self.dem_array, self.dem_transform, self.dem_crs = load_dem(self.current_dem_path)
            print(f"DEM loaded successfully. Shape: {self.dem_array.shape}, Transform: {self.dem_transform}, CRS: {self.dem_crs}")

            if self.dem_array is not None:
                self.map_canvas.axes.clear()
                
                height, width = self.dem_array.shape
                extent = rasterio.transform.array_bounds(height, width, self.dem_transform)

                src_crs = self.dem_crs
                dst_crs = pyproj.CRS("EPSG:4326")
                transformer = pyproj.Transformer.from_crs(src_crs, dst_crs, always_xy=True)
                west, south = transformer.transform(extent[0], extent[1])
                east, north = transformer.transform(extent[2], extent[3])
                wgs84_extent = [west, east, south, north]

                self.map_canvas.axes.imshow(self.dem_array, cmap='gray', origin='upper', extent=wgs84_extent)
                self.map_canvas.axes.set_title(f"Loaded DEM: {os.path.basename(self.current_dem_path)}")
                self.map_canvas.axes.set_xlabel("Longitude")
                self.map_canvas.axes.set_ylabel("Latitude")
                self.map_canvas.fig.tight_layout()
                self.map_canvas.draw()
                QMessageBox.information(self, "DEM Loaded",
                                        f"DEM '{os.path.basename(self.current_dem_path)}' loaded successfully.")
            else:
                QMessageBox.critical(self, "DEM Load Error", "DEM data is None after loading attempt.")
                print("DEM data is None after loading attempt.")
                self.current_dem_path = None

        except FileNotFoundError:
            QMessageBox.critical(self, "DEM Load Error", f"DEM file not found at '{self.current_dem_path}'.")
            print(f"Error: DEM file not found at '{self.current_dem_path}'.")
            self.dem_array = None
            self.dem_transform = None
            self.dem_crs = None
            self.current_dem_path = None
        except Exception as e:
            QMessageBox.critical(self, "DEM Load Error",
                                 f"An error occurred while loading DEM '{os.path.basename(self.current_dem_path)}': {e}")
            print(f"An error occurred while loading DEM: {e}")
            self.dem_array = None
            self.dem_transform = None
            self.dem_crs = None
            self.current_dem_path = None

    def _run_analysis(self):
        if self.dem_array is None:
            QMessageBox.warning(self, "Analysis Error", "No DEM loaded. Please load a DEM file first.")
            return

        slr_value_cm = self.slr_slider.value()
        slr_value_meters = slr_value_cm / 100.0
        print(f"Running analysis with SLR: {slr_value_meters:.2f}m")

        try:
            flood_mask = connected_flood(self.dem_array, slr_value_meters)
            print(f"Flood analysis complete. Flooded cells: {np.sum(flood_mask)}")

            height, width = self.dem_array.shape
            extent = rasterio.transform.array_bounds(height, width, self.dem_transform)
            self.map_canvas.plot_flood_mask(flood_mask, extent=extent)

            if self.buildings_gdf is not None and not self.buildings_gdf.empty:
                projected_gdf = self.buildings_gdf.to_crs(self.dem_crs)
                self.map_canvas.plot_geodataframe(projected_gdf, facecolor='red', edgecolor='red', alpha=0.5)

            QMessageBox.information(self, "Analysis Complete", f"Flood risk analysis finished for SLR {slr_value_meters:.2f}m.")

        except Exception as e:
            QMessageBox.critical(self, "Analysis Error", f"An error occurred during flood analysis: {e}")
            print(f"An error occurred during flood analysis: {e}")

def main():
    app = QApplication(sys.argv)
    ex = CoraGUI()
    ex.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()