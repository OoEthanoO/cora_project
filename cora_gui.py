import os
import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QDockWidget, QSlider, QMessageBox
)
from PyQt6.QtCore import Qt

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import numpy as np

from cora.utils.data_loader import load_dem
from cora.core.flood_model import connected_flood


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

    def plot_flood_mask(self, flood_mask_array: np.ndarray):
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
            im = self.axes.imshow(flood_mask_array, cmap='Blues', origin='upper')
            self.axes.set_title("Flood Inundation Map")
            self.axes.set_xlabel("X-coordinate")
            self.axes.set_ylabel("Y-coordinate")

        self.fig.tight_layout()
        self.draw()


class CoraGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.slr_value_label = QLabel()
        self.slr_slider = QSlider(Qt.Orientation.Horizontal)

        self.dem_array: np.ndarray | None = None
        self.dem_transform = None

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

        self.load_dem_button = QPushButton("Load Sample DEM (Miami)")
        self.load_dem_button.clicked.connect(self._load_sample_dem)
        dock_layout.addWidget(self.load_dem_button)

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

    def _on_slr_slider_changed(self, value):
        slr_meters = value / 100.0
        self.slr_value_label.setText(f"{slr_meters:.2f}m")

    def _load_sample_dem(self):
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.abspath(__file__))
            sample_dem_path = os.path.join(project_root, "data", "n25_w081_1arc_v3_miami.tif")

            if not os.path.exists(sample_dem_path):
                QMessageBox.warning(self, "DEM Load Error", f"Sample DEM file not found at {sample_dem_path}")
                self.dem_array = None
                self.dem_transform = None
                return

            print(f"Loading DEM from: {sample_dem_path}...")
            self.dem_array, self.dem_transform = load_dem(sample_dem_path)
            print(f"DEM loaded successfully. Shape: {self.dem_array.shape}, Transform: {self.dem_transform}")
            if self.dem_array is not None:
                self.map_canvas.axes.clear()
                self.map_canvas.axes.imshow(self.dem_array, cmap='gray', origin='upper')
                self.map_canvas.axes.set_title("Loaded DEM")
                self.map_canvas.axes.set_xlabel("X-coordinate")
                self.map_canvas.axes.set_ylabel("Y-coordinate")
                self.map_canvas.fig.tight_layout()
                self.map_canvas.draw()
                QMessageBox.information(self, "DEM Loaded", f"DEM '{os.path.basename(sample_dem_path)}' loaded successfully.")
            else:
                QMessageBox.critical(self, "DEM Load Error", "DEM data is None after loading attempt.")
                print("DEM data is None after loading attempt.")


        except FileNotFoundError:
            QMessageBox.critical(self, "DEM Load Error", f"DEM file not found. Please check the path.")
            print(f"Error: DEM file not found at. Please check the path.")
            self.dem_array = None
            self.dem_transform = None
        except Exception as e:
            QMessageBox.critical(self, "DEM Load Error", f"An error occurred while loading DEM: {e}")
            print(f"An error occurred while loading DEM: {e}")
            self.dem_array = None
            self.dem_transform = None

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

            self.map_canvas.plot_flood_mask(flood_mask)
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