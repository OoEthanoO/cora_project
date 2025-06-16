import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QDockWidget
)
from PyQt6.QtCore import Qt


class CoraGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.map_canvas_placeholder = QWidget()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('CORA - Coastal Risk Analyzer GUI')
        self.setGeometry(100, 100, 800, 600)

        self.setCentralWidget(self.map_canvas_placeholder)
        self.map_canvas_placeholder.setStyleSheet("background-color: lightgrey; border: 1px solid black;")

        self.controls_dock = QDockWidget("Controls", self)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.controls_dock)

        dock_widget_content = QWidget()
        dock_layout = QVBoxLayout(dock_widget_content)

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

        dock_layout.addStretch(1)

        self.controls_dock.setWidget(dock_widget_content)


def main():
    app = QApplication(sys.argv)
    ex = CoraGUI()
    ex.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()