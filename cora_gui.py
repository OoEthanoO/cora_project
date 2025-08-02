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
from shapely.geometry import LineString

from cora.utils.data_loader import load_dem
from cora.core.flood_model import connected_flood
from cora.utils.osm_handler import fetch_osm_geometries, mark_critical_infrastructure
from cora.analysis.impact_assessment import raster_to_vector_polygons, find_intersecting_features
from cora.core.adaptation import apply_sea_wall

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
            self.axes.set_xlabel("Longitude")
            self.axes.set_ylabel("Latitude")

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
        self.roads_gdf = None

        self.is_drawing_wall = False
        self.sea_wall_points = []
        self.sea_wall_geometry = None
        self.sea_wall_plot = None

        self.initUI()

    def initUI(self):
        self.setWindowTitle('CORA - Coastal Risk Analyzer GUI')
        self.setGeometry(100, 100, 800, 600)

        self.map_canvas = MplCanvas(self, width=7, height=5, dpi=100)
        self.setCentralWidget(self.map_canvas)

        self.map_canvas.mpl_connect('button_press_event', self._on_map_click)

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

        self.load_roads_button = QPushButton("Load Roads")
        self.load_roads_button.clicked.connect(self._load_osm_roads)
        dock_layout.addWidget(self.load_roads_button)

        self.clear_cache_button = QPushButton("Clear OSM Cache")
        self.clear_cache_button.clicked.connect(self._clear_osm_cache)
        dock_layout.addWidget(self.clear_cache_button)

        self.analyze_button = QPushButton("Analyze Flood Risk")
        self.analyze_button.clicked.connect(self._run_analysis)
        dock_layout.addWidget(self.analyze_button)

        self.draw_wall_button = QPushButton("Draw Sea Wall")
        self.draw_wall_button.clicked.connect(self._toggle_drawing_mode)
        dock_layout.addWidget(self.draw_wall_button)

        self.clear_wall_button = QPushButton("Clear Sea Wall")
        self.clear_wall_button.clicked.connect(self._clear_sea_wall)
        dock_layout.addWidget(self.clear_wall_button)

        wall_height_layout = QHBoxLayout()
        self.wall_height_label = QLabel("Wall Height (m):")
        self.wall_height_input = QLineEdit()
        self.wall_height_input.setText("3.0")  # Default value
        self.wall_height_input.setPlaceholderText("e.g., 3.0")
        wall_height_layout.addWidget(self.wall_height_label)
        wall_height_layout.addWidget(self.wall_height_input)
        dock_layout.addLayout(wall_height_layout)

        self.flooded_buildings_label = QLabel("Flooded Buildings: N/A")
        dock_layout.addWidget(self.flooded_buildings_label)

        self.flooded_critical_label = QLabel("Flooded Critical Infra: N/A")
        dock_layout.addWidget(self.flooded_critical_label)

        self.flooded_hospitals_pct_label = QLabel("Flooded Hospitals: N/A")
        dock_layout.addWidget(self.flooded_hospitals_pct_label)

        self.flooded_roads_label = QLabel("Flooded Roads (km): N/A")
        dock_layout.addWidget(self.flooded_roads_label)

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

    def _get_bbox_from_inputs(self, buffer_deg=0.01):
        try:
            lat = float(self.lat_input.text())
            lon = float(self.lon_input.text())
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Please enter valid numeric values for latitude and longitude.")
            return None

        north = lat + buffer_deg
        south = lat - buffer_deg
        east = lon + buffer_deg
        west = lon - buffer_deg
        return north, south, east, west

    def _load_osm_buildings(self):
        bbox = self._get_bbox_from_inputs()
        if bbox is not None:
            north, south, east, west = bbox
        else:
            return

        tags = {"building": True}
        self.statusBar().showMessage("Fetching OSM building data...", 5000)
        try:
            print(f"Fetching OSM building data for bbox: N={north}, S={south}, E={east}, W={west}")
            self.buildings_gdf = fetch_osm_geometries(north, south, east, west, tags)
            self.statusBar().showMessage("Processing building data...", 5000)
            self.buildings_gdf = mark_critical_infrastructure(self.buildings_gdf)
            count = len(self.buildings_gdf) if self.buildings_gdf is not None else 0
            print(f"Buildings GDF loaded, count: {count}")

            self.map_canvas.axes.clear()
            self.map_canvas.axes.imshow(self.dem_array, cmap='gray', origin='upper', extent=self.wgs84_extent)


            if self.roads_gdf is not None and not self.roads_gdf.empty:
                projected_roads = self.roads_gdf.to_crs(self.dem_crs)
                self.map_canvas.plot_geodataframe(projected_roads, edgecolor='grey', zorder=2)
                
            if self.buildings_gdf is not None and not self.buildings_gdf.empty:
                QMessageBox.information(self, "OSM Data Loaded", f"Successfully fetched {count} building geometries.")

                if self.buildings_gdf.crs is None:
                    self.buildings_gdf.set_crs("EPSG:4326", inplace=True)

                projected_gdf = self.buildings_gdf.to_crs(self.dem_crs)
                self.map_canvas.plot_geodataframe(projected_gdf, facecolor='none', edgecolor='blue', linewidth=0.5, zorder=3)
            else:
                QMessageBox.warning(self, "OSM Data", "No building geometries were found for the given area.")

            self.map_canvas.axes.set_xlabel("Longitude")
            self.map_canvas.axes.set_ylabel("Latitude")
            self.map_canvas.fig.tight_layout()
            self.map_canvas.draw()
            self.statusBar().showMessage(f"Loaded {count} buildings.", 5000)
        except Exception as e:
            error_message = f"Failed to fetch OSM data: {e}"
            print(error_message)
            QMessageBox.critical(self, "OSM Load Error", error_message)
            self.buildings_gdf = None
            self.statusBar().showMessage("Failed to load building data.", 5000)

    def _load_osm_roads(self):
        bbox = self._get_bbox_from_inputs()
        if bbox is not None:
            north, south, east, west = bbox
        else:
            return

        tags = {"highway": True}
        self.statusBar().showMessage("Fetching OSM road data...", 5000)
        try:
            print(f"Fetching OSM road data for bbox: N={north}, S={south}, E={east}, W={west}")
            self.roads_gdf = fetch_osm_geometries(north, south, east, west, tags)
            count = len(self.roads_gdf) if self.roads_gdf is not None else 0
            print(f"Roads GDF loaded, count: {count}")

            self.map_canvas.axes.clear()
            self.map_canvas.axes.imshow(self.dem_array, cmap='gray', origin='upper', extent=self.wgs84_extent)

            if self.roads_gdf is not None and not self.roads_gdf.empty:
                QMessageBox.information(self, "OSM Roads Loaded", f"Successfully fetched {count} road geometries.")

                if self.roads_gdf.crs is None:
                    self.roads_gdf.set_crs("EPSG:4326", inplace=True)

                projected_gdf = self.roads_gdf.to_crs(self.dem_crs)
                self.map_canvas.plot_geodataframe(projected_gdf, edgecolor='grey', zorder=2)
            else:
                QMessageBox.warning(self, "OSM Roads", "No road geometries were found for the given area.")


            if self.buildings_gdf is not None and not self.buildings_gdf.empty:
                projected_buildings = self.buildings_gdf.to_crs(self.dem_crs)
                self.map_canvas.plot_geodataframe(projected_buildings, facecolor='none', edgecolor='blue', linewidth=0.5, zorder=3)

            self.map_canvas.axes.set_xlabel("Longitude")
            self.map_canvas.axes.set_ylabel("Latitude")
            self.map_canvas.fig.tight_layout()
            self.map_canvas.draw()
            self.statusBar().showMessage(f"Loaded {count} roads.", 5000)
        except Exception as e:
            error_message = f"Failed to fetch OSM road data: {e}"
            print(error_message)
            QMessageBox.critical(self, "OSM Load Error", error_message)
            self.roads_gdf = None
            self.statusBar().showMessage("Failed to load road data.", 5000)

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

                self.wgs84_extent = [west, east, south, north]
                self.map_canvas.axes.imshow(self.dem_array, cmap='gray', origin='upper', extent=self.wgs84_extent)
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
            dem_to_analyze = self.dem_array
            if self.sea_wall_geometry is not None and len(self.sea_wall_points) >= 2:
                try:
                    wall_height_str = self.wall_height_input.text()
                    wall_height = float(wall_height_str)
                except Exception:
                    wall_height = 3.0
                dem_to_analyze = apply_sea_wall(
                    dem_to_analyze,
                    self.sea_wall_geometry,
                    wall_height,
                    self.dem_transform
                )
                print(f"Applied sea wall at height {wall_height}m.")

            flood_mask = connected_flood(dem_to_analyze, slr_value_meters)
            print(f"Flood analysis complete. Flooded cells: {np.sum(flood_mask)}")

            height, width = self.dem_array.shape
            extent = rasterio.transform.array_bounds(height, width, self.dem_transform)

            src_crs = self.dem_crs
            dst_crs = pyproj.CRS("EPSG:4326")
            transformer = pyproj.Transformer.from_crs(src_crs, dst_crs, always_xy=True)
            west, south = transformer.transform(extent[0], extent[1])
            east, north = transformer.transform(extent[2], extent[3])
            wgs84_extent = [west, east, south, north]

            flood_polygons_gdf = raster_to_vector_polygons(flood_mask, self.dem_transform)
            if hasattr(flood_polygons_gdf, 'set_crs') and (flood_polygons_gdf.crs is None):
                flood_polygons_gdf.set_crs(self.dem_crs, inplace=True)

            if self.buildings_gdf is not None and not self.buildings_gdf.empty:
                poly_buildings_gdf = self.buildings_gdf[
                    self.buildings_gdf.geometry.type.isin(['Polygon', 'MultiPolygon'])
                ]
                if not poly_buildings_gdf.empty:
                    flooded_buildings_gdf = find_intersecting_features(poly_buildings_gdf, flood_polygons_gdf)
                    flooded_buildings_count = len(flooded_buildings_gdf)
                    print(f"Flooded buildings count: {flooded_buildings_count}")
                    self.flooded_buildings_label.setText(f"Flooded Buildings: {flooded_buildings_count}")

                    if "is_critical" in flooded_buildings_gdf.columns:
                        flooded_critical_gdf = flooded_buildings_gdf[flooded_buildings_gdf["is_critical"] == True]
                    else:
                        flooded_critical_gdf = flooded_buildings_gdf.iloc[0:0]  # Empty DataFrame if column missing

                    flooded_critical_count = len(flooded_critical_gdf)
                    print(f"Flooded critical infrastructure count: {flooded_critical_count}")
                    self.flooded_critical_label.setText(f"Flooded Critical Infra: {flooded_critical_count}")

                    if "amenity" in self.buildings_gdf.columns:
                        total_hospitals = self.buildings_gdf[self.buildings_gdf["amenity"] == "hospital"]
                        n_total_hospitals = len(total_hospitals)
                        if n_total_hospitals > 0:
                            flooded_hospitals = flooded_buildings_gdf[flooded_buildings_gdf["amenity"] == "hospital"]
                            n_flooded_hospitals = len(flooded_hospitals)
                            pct = (n_flooded_hospitals / n_total_hospitals) * 100
                            self.flooded_hospitals_pct_label.setText(
                                f"Flooded Hospitals: {n_flooded_hospitals}/{n_total_hospitals} ({pct:.1f}%)"
                            )
                        else:
                            self.flooded_hospitals_pct_label.setText("Flooded Hospitals: 0/0 (0.0%)")
                    else:
                        self.flooded_hospitals_pct_label.setText("Flooded Hospitals: N/A")
                else:
                    print("No polygonal buildings to analyze for flooding.")
                    self.flooded_buildings_label.setText("Flooded Buildings: N/A")
            else:
                self.flooded_buildings_label.setText("Flooded Buildings: N/A")

            if self.roads_gdf is not None and not self.roads_gdf.empty:
                line_roads_gdf = self.roads_gdf[
                    self.roads_gdf.geometry.type.isin(['LineString', 'MultiLineString'])
                ]
                if not line_roads_gdf.empty:
                    flooded_roads_gdf = find_intersecting_features(line_roads_gdf, flood_polygons_gdf)
                    if flooded_roads_gdf.crs is None:
                        flooded_roads_gdf.set_crs(self.dem_crs, inplace=True)
                    try:
                        centroid = flooded_roads_gdf.unary_union.centroid
                        utm_crs = pyproj.CRS.from_user_input(pyproj.database.query_utm_crs_info(
                            datum_name="WGS 84",
                            area_of_interest=pyproj.aoi.AreaOfInterest(
                                west_lon_degree=centroid.x,
                                south_lat_degree=centroid.y,
                                east_lon_degree=centroid.x,
                                north_lat_degree=centroid.y,
                            ),
                        )[0].code)
                        flooded_roads_proj = flooded_roads_gdf.to_crs(utm_crs)
                        total_length_m = flooded_roads_proj.geometry.length.sum()
                        total_length_km = total_length_m / 1000.0
                        print(f"Flooded roads total length: {total_length_km:.2f} km")
                        self.flooded_roads_label.setText(f"Flooded Roads (km): {total_length_km:.2f}")
                    except Exception as e:
                        print(f"Could not project flooded roads for length calculation: {e}")
                        total_length = flooded_roads_gdf.geometry.length.sum()
                        self.flooded_roads_label.setText(f"Flooded Roads: {total_length:.2f} (map units)")
                else:
                    print("No linear roads to analyze for flooding.")
                    self.flooded_roads_label.setText("Flooded Roads (km): N/A")
            else:
                self.flooded_roads_label.setText("Flooded Roads (km): N/A")

            self.map_canvas.plot_flood_mask(flood_mask, extent=self.wgs84_extent)
            self.map_canvas.axes.set_xlabel("Longitude")
            self.map_canvas.axes.set_ylabel("Latitude")

            if self.roads_gdf is not None and not self.roads_gdf.empty:
                projected_roads = self.roads_gdf.to_crs(self.dem_crs)
                self.map_canvas.plot_geodataframe(projected_roads, edgecolor='grey', zorder=2)
            if self.buildings_gdf is not None and not self.buildings_gdf.empty:
                projected_buildings = self.buildings_gdf.to_crs(self.dem_crs)
                self.map_canvas.plot_geodataframe(projected_buildings, facecolor='red', edgecolor='red', alpha=0.5, zorder=3)

            QMessageBox.information(self, "Analysis Complete", f"Flood risk analysis finished for SLR {slr_value_meters:.2f}m.")

        except Exception as e:
            QMessageBox.critical(self, "Analysis Error", f"An error occurred during flood analysis: {e}")
            print(f"An error occurred during flood analysis: {e}")

    def _toggle_drawing_mode(self):
        self.is_drawing_wall = not self.is_drawing_wall

        if self.is_drawing_wall:
            self.draw_wall_button.setText("Finish Drawing")
            self.statusBar().showMessage("Click on the map to add points for the sea wall.")
            self.sea_wall_points = []
            self.sea_wall_geometry = None
            if self.sea_wall_plot:
                self.sea_wall_plot[0].remove()
                self.sea_wall_plot = None
            self.map_canvas.draw()
        else:
            self.draw_wall_button.setText("Draw Sea Wall")
            if len(self.sea_wall_points) >= 2:
                self.sea_wall_geometry = LineString(self.sea_wall_points)
                self.statusBar().showMessage(f"Sea wall path finalized with {len(self.sea_wall_points)} points.", 5000)
                print(f"Sea wall geometry created: {self.sea_wall_geometry}")
            else:
                self.statusBar().showMessage("Sea wall drawing cancelled (not enough points).", 5000)
                self.sea_wall_points = []
                if self.sea_wall_plot:
                    self.sea_wall_plot[0].remove()
                    self.sea_wall_plot = None
                self.map_canvas.draw()

    def _on_map_click(self, event):
        if self.is_drawing_wall and event.xdata is not None and event.ydata is not None:
            self.sea_wall_points.append((event.xdata, event.ydata))
            self._update_wall_preview()

    def _update_wall_preview(self):
        if self.sea_wall_plot:
            self.sea_wall_plot[0].remove()
            self.sea_wall_plot = None

        if len(self.sea_wall_points) >= 2:
            x, y = zip(*self.sea_wall_points)
            self.sea_wall_plot = self.map_canvas.axes.plot(x, y, color='orange', linewidth=2, marker='o', zorder=10)
        self.map_canvas.draw()

    def _clear_sea_wall(self):
        self.sea_wall_points = []
        self.sea_wall_geometry = None
        if self.sea_wall_plot:
            try:
                self.sea_wall_plot[0].remove()
            except Exception:
                self.map_canvas.axes.clear()
                if self.dem_array is not None and hasattr(self, "wgs84_extent"):
                    self.map_canvas.axes.imshow(self.dem_array, cmap='gray', origin='upper', extent=self.wgs84_extent)
            self.sea_wall_plot = None
        self.map_canvas.draw()
        self.statusBar().showMessage("Sea wall cleared.", 3000)

def main():
    app = QApplication(sys.argv)
    ex = CoraGUI()
    ex.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
