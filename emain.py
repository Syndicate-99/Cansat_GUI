import sys
from PyQt5.QtGui import QFont, QPixmap, QPalette, QColor, QIcon
from PyQt5.QtCore import Qt, QTimer, QTime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QStackedWidget, QGroupBox, QGridLayout,
    QStyleFactory, QFrame, QSizePolicy, QProgressBar, QComboBox
)
import pyqtgraph as pg
import numpy as np
from communication import Communication
from dataBase import data_base
import sys
from PyQt5.QtGui import QFont, QPixmap, QPalette, QColor, QIcon, QVector3D
from PyQt5.QtCore import Qt, QTimer, QTime, QDateTime, QUrl
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QStackedWidget, QGroupBox, QGridLayout,
    QStyleFactory, QFrame, QSizePolicy, QProgressBar, QComboBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QLCDNumber, QTextEdit,
    QFileDialog, QInputDialog, QLineEdit
)
from PyQt5.QtWebEngineWidgets import QWebEngineView
import pyqtgraph as pg
import pyqtgraph.opengl as gl
import numpy as np
from datetime import datetime
import pandas as pd
import json
import os
from communication import Communication
from dataBase import data_base


# Set dark theme for pyqtgraph
pg.setConfigOption('background', '#1e1e1e')
pg.setConfigOption('foreground', '#ffffff')
class CanSat3DVisualizer(gl.GLViewWidget):
    def __init__(self):
        super().__init__()
        # Set initial camera position and parameters
        self.setCameraPosition(distance=40, elevation=30, azimuth=45)
        self.setBackgroundColor('#2d2d2d')
        
        # Create the main body of the CanSat (cylinder)
        vertices, faces = self.create_cylinder(radius=2, height=6, segments=32)
        meshdata = gl.MeshData(vertexes=vertices, faces=faces)
        self.cansat_body = gl.GLMeshItem(
            meshdata=meshdata,
            smooth=True,
            color=(0.8, 0.8, 0.8, 1),
            shader='shaded',
            glOptions='opaque'
        )
        
        # Create antenna (thin cylinder on top)
        ant_vertices, ant_faces = self.create_cylinder(radius=0.2, height=2, segments=16)
        ant_meshdata = gl.MeshData(vertexes=ant_vertices, faces=ant_faces)
        self.antenna = gl.GLMeshItem(
            meshdata=ant_meshdata,
            smooth=True,
            color=(0.3, 0.3, 0.3, 1),
            shader='shaded',
            glOptions='opaque'
        )
        self.antenna.translate(0, 0, 3)  # Position on top of main body
        
        # Create solar panels (rectangles on sides)
        self.solar_panels = []
        panel_positions = [
            (2.2, 0, 0),  # Right
            (-2.2, 0, 0), # Left
            (0, 2.2, 0),  # Front
            (0, -2.2, 0)  # Back
        ]
        
        for pos in panel_positions:
            panel = gl.GLBoxItem(
                size=pg.Vector(0.1, 2, 4),
                color=(0.2, 0.5, 0.8, 1)
            )
            panel.translate(*pos)
            self.solar_panels.append(panel)
        
        # Create coordinate axes for reference
        self.axes = gl.GLAxisItem()
        self.axes.setSize(x=10, y=10, z=10)
        
        # Add grid for reference
        self.grid = gl.GLGridItem()
        self.grid.setSize(x=20, y=20)
        self.grid.translate(0, 0, -5)
        
        # Add items to view
        self.addItem(self.cansat_body)
        self.addItem(self.antenna)
        for panel in self.solar_panels:
            self.addItem(panel)
        self.addItem(self.axes)
        self.addItem(self.grid)
        
        # Add orientation labels
        self.orientation_text = {}
        positions = [(15, 0, 0), (0, 15, 0), (0, 0, 15)]
        labels = ['X', 'Y', 'Z']
        for pos, label in zip(positions, labels):
            text = gl.GLTextItem(pos=pos, text=label, color=(1, 1, 1, 1))
            self.addItem(text)
            self.orientation_text[label] = text

        # Initial orientation
        self.current_rotation = [0, 0, 0]

    def create_cylinder(self, radius=1, height=2, segments=32):
        # Create vertices
        theta = np.linspace(0, 2*np.pi, segments)
        x = radius * np.cos(theta)
        y = radius * np.sin(theta)
        z_bottom = np.zeros_like(theta) - height/2
        z_top = np.zeros_like(theta) + height/2
        
        vertices = []
        # Add bottom circle
        vertices.extend(list(zip(x, y, z_bottom)))
        # Add top circle
        vertices.extend(list(zip(x, y, z_top)))
        # Add center points for caps
        vertices.append((0, 0, -height/2))  # Bottom center
        vertices.append((0, 0, height/2))   # Top center
        
        vertices = np.array(vertices)
        
        # Create faces
        faces = []
        # Side faces
        for i in range(segments-1):
            faces.append([i, i+1, i+segments])
            faces.append([i+1, i+segments+1, i+segments])
        # Connect last segment to first
        faces.append([segments-1, 0, segments*2-1])
        faces.append([0, segments, segments*2-1])
        
        # Bottom cap faces
        for i in range(segments-1):
            faces.append([i, i+1, segments*2])
        faces.append([segments-1, 0, segments*2])
        
        # Top cap faces
        for i in range(segments-1):
            faces.append([i+segments, i+segments+1, segments*2+1])
        faces.append([segments*2-1, segments, segments*2+1])
        
        faces = np.array(faces)
        
        return vertices, faces

    def update_orientation(self, roll, pitch, yaw):
        """Update the CanSat orientation based on gyroscope data"""
        # Reset transformations
        self.cansat_body.resetTransform()
        self.antenna.resetTransform()
        for panel in self.solar_panels:
            panel.resetTransform()
        
        # Apply rotations
        # Convert angles to radians
        roll_rad = np.radians(roll)
        pitch_rad = np.radians(pitch)
        yaw_rad = np.radians(yaw)
        
        # Create rotation matrices
        def rot_x(angle):
            return np.array([
                [1, 0, 0],
                [0, np.cos(angle), -np.sin(angle)],
                [0, np.sin(angle), np.cos(angle)]
            ])
        
        def rot_y(angle):
            return np.array([
                [np.cos(angle), 0, np.sin(angle)],
                [0, 1, 0],
                [-np.sin(angle), 0, np.cos(angle)]
            ])
        
        def rot_z(angle):
            return np.array([
                [np.cos(angle), -np.sin(angle), 0],
                [np.sin(angle), np.cos(angle), 0],
                [0, 0, 1]
            ])
        
        # Combine rotations
        rotation = rot_z(yaw_rad) @ rot_y(pitch_rad) @ rot_x(roll_rad)
        
        # Apply rotations to all components
        self.cansat_body.rotate(roll, 1, 0, 0)
        self.cansat_body.rotate(pitch, 0, 1, 0)
        self.cansat_body.rotate(yaw, 0, 0, 1)
        
        self.antenna.translate(0, 0, 3)  # Reset position
        self.antenna.rotate(roll, 1, 0, 0)
        self.antenna.rotate(pitch, 0, 1, 0)
        self.antenna.rotate(yaw, 0, 0, 1)
        
        for panel, pos in zip(self.solar_panels, [(2.2, 0, 0), (-2.2, 0, 0), (0, 2.2, 0), (0, -2.2, 0)]):
            panel.resetTransform()
            panel.translate(*pos)
            panel.rotate(roll, 1, 0, 0)
            panel.rotate(pitch, 0, 1, 0)
            panel.rotate(yaw, 0, 0, 1)
        
        self.current_rotation = [roll, pitch, yaw]
              
class GPSMapView(QWebEngineView):
    def __init__(self):
        super().__init__()
        self.setHtml('''
            <!DOCTYPE html>
            <html>
            <head>
                <title>CanSat GPS Tracking</title>
                <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/leaflet.css" />
                <script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/leaflet.js"></script>
                <style>
                    #map { height: 100%; width: 100%; }
                </style>
            </head>
            <body>
                <div id="map"></div>
                <script>
                    var map = L.map('map').setView([0, 0], 13);
                    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                        maxZoom: 19,
                    }).addTo(map);
                    var marker = L.marker([0, 0]).addTo(map);
                    var path = L.polyline([], {color: 'red'}).addTo(map);
                    
                    function updatePosition(lat, lon) {
                        marker.setLatLng([lat, lon]);
                        path.addLatLng([lat, lon]);
                        map.setView([lat, lon]);
                    }
                </script>
            </body>
            </html>
        ''')
        self.positions = []

    def update_position(self, lat, lon):
        self.positions.append([lat, lon])
        self.page().runJavaScript(f"updatePosition({lat}, {lon});")
        
class SystemDiagnostics(QGroupBox):
    def __init__(self):
        super().__init__("System Diagnostics")
        self.init_ui()

    def init_ui(self):
        layout = QGridLayout(self)
        
        # Create diagnostic indicators
        self.indicators = {
            'cpu_usage': self.create_diagnostic("CPU Usage", "0%"),
            'memory_usage': self.create_diagnostic("Memory Usage", "0%"),
            'storage_space': self.create_diagnostic("Storage Space", "0%"),
            'signal_strength': self.create_diagnostic("Signal Strength", "0%"),
            'packet_loss': self.create_diagnostic("Packet Loss", "0%"),
            'battery_temp': self.create_diagnostic("Battery Temp", "0°C"),
            'system_temp': self.create_diagnostic("System Temp", "0°C"),
            'data_rate': self.create_diagnostic("Data Rate", "0 B/s")
        }
        
        # Add indicators to layout
        row = 0
        col = 0
        for name, (label, value) in self.indicators.items():
            layout.addWidget(label, row, col * 2)
            layout.addWidget(value, row, col * 2 + 1)
            col += 1
            if col > 1:
                col = 0
                row += 1

    def create_diagnostic(self, name, initial_value):
        label = QLabel(name)
        value = QLabel(initial_value)
        value.setStyleSheet("color: #00ff00;")
        return label, value

    def update_diagnostic(self, name, value, status="ok"):
        if name in self.indicators:
            colors = {
                "ok": "#00ff00",
                "warning": "#ffff00",
                "error": "#ff0000"
            }
            self.indicators[name][1].setText(str(value))
            self.indicators[name][1].setStyleSheet(f"color: {colors.get(status, '#00ff00')};")

class DataExporter:
    def __init__(self, parent=None):
        self.parent = parent
        self.data_buffer = []

    def add_data_point(self, data):
        """Add a data point to the buffer"""
        self.data_buffer.append(data)

    def export_csv(self):
        """Export data buffer to CSV"""
        if not self.data_buffer:
            return False
            
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self.parent,
                "Export Data",
                "",
                "CSV Files (*.csv);;All Files (*)"
            )
            
            if filename:
                df = pd.DataFrame(self.data_buffer)
                df.to_csv(filename, index=False)
                return True
        except Exception as e:
            print(f"Export error: {e}")
            return False

    def export_json(self):
        """Export data buffer to JSON"""
        if not self.data_buffer:
            return False
            
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self.parent,
                "Export Data",
                "",
                "JSON Files (*.json);;All Files (*)"
            )
            
            if filename:
                with open(filename, 'w') as f:
                    json.dump(self.data_buffer, f)
                return True
        except Exception as e:
            print(f"Export error: {e}")
            return False

class CustomCommandInterface(QGroupBox):
    def __init__(self, serial_connection):
        super().__init__("Custom Command Interface")
        self.serial = serial_connection
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Command history
        self.history = QTextEdit()
        self.history.setReadOnly(True)
        self.history.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #00ff00;
                font-family: monospace;
            }
        """)
        
        # Command input
        input_layout = QHBoxLayout()
        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText("Enter custom command...")
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_command)
        
        input_layout.addWidget(self.command_input)
        input_layout.addWidget(self.send_button)
        
        # Preset commands
        preset_layout = QHBoxLayout()
        self.preset_combo = QComboBox()
        self.preset_combo.addItems([
            "Select Preset",
            "Request Status",
            "Reset Sensors",
            "Toggle Debug Mode",
            "Force Data Sync"
        ])
        self.load_preset = QPushButton("Load")
        self.load_preset.clicked.connect(self.load_preset_command)
        
        preset_layout.addWidget(self.preset_combo)
        preset_layout.addWidget(self.load_preset)
        
        # Add all to main layout
        layout.addWidget(self.history)
        layout.addLayout(input_layout)
        layout.addLayout(preset_layout)

    def send_command(self):
        command = self.command_input.text()
        if command:
            try:
                # Add command to history
                self.history.append(f">> {command}")
                
                # Send command through serial connection
                self.serial.write(command.encode() + b'\n')
                
                # Clear input
                self.command_input.clear()
            except Exception as e:
                self.history.append(f"Error: {str(e)}")

    def load_preset_command(self):
        command = self.preset_combo.currentText()
        if command != "Select Preset":
            self.command_input.setText(command)
            


class ModernButton(QPushButton):
    def __init__(self, text, icon_path=None):
        super().__init__(text)
        if icon_path:
            self.setIcon(QIcon(icon_path))
        self.setStyleSheet("""
            QPushButton {
                background-color: #2d5ca8;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3873cf;
            }
            QPushButton:pressed {
                background-color: #1d3c6a;
            }
        """)

class DataCard(QGroupBox):
    def __init__(self, title):
        super().__init__(title)
        self.setStyleSheet("""
            QGroupBox {
                background-color: #2d2d2d;
                border: 2px solid #3d3d3d;
                border-radius: 10px;
                margin-top: 1em;
                padding: 10px;
                color: white;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Parikshit Student Satellite \n CanSat Ground Station')
        self.setStyleSheet("background-color: #1e1e1e; color: white;")
        self.resize(1400, 800)

        # Initialize data buffers
        self.data_length = 100  # Number of points to display
        self.times = np.zeros(self.data_length)
        self.altitudes = np.zeros(self.data_length)
        self.speeds = np.zeros(self.data_length)
        self.accelerations = np.zeros(self.data_length)
        self.gyro_x = np.zeros(self.data_length)
        self.gyro_y = np.zeros(self.data_length)
        self.gyro_z = np.zeros(self.data_length)

        # Initialize plots
        self.setup_plots()

        # Initialize communication and database
        self.ser = Communication()
        self.db = data_base()
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        
        # Create header
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Create navigation
        nav = self.create_navigation()
        main_layout.addWidget(nav)
        
        # Create stacked widget for pages
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.addWidget(self.create_monitoring_page())
        self.stacked_widget.addWidget(self.create_gps_page())
        self.stacked_widget.addWidget(self.create_telemetry_page())
        main_layout.addWidget(self.stacked_widget)
        
        # Setup timers
        self.setup_timers()

    def setup_plots(self):
        # Altitude plot
        self.altitude_plot = pg.PlotWidget()
        self.altitude_plot.setBackground('#2d2d2d')
        self.altitude_plot.setTitle("Altitude (m)", color='w')
        self.altitude_line = self.altitude_plot.plot(pen=pg.mkPen(color='#00ff00', width=2))

        # Speed plot
        self.speed_plot = pg.PlotWidget()
        self.speed_plot.setBackground('#2d2d2d')
        self.speed_plot.setTitle("Speed (m/s)", color='w')
        self.speed_line = self.speed_plot.plot(pen=pg.mkPen(color='#00ffff', width=2))

        # Acceleration plot
        self.acceleration_plot = pg.PlotWidget()
        self.acceleration_plot.setBackground('#2d2d2d')
        self.acceleration_plot.setTitle("Acceleration (m/s²)", color='w')
        self.acceleration_line = self.acceleration_plot.plot(pen=pg.mkPen(color='#ff00ff', width=2))

        # Gyroscope plot
        self.gyro_plot = pg.PlotWidget()
        self.gyro_plot.setBackground('#2d2d2d')
        self.gyro_plot.setTitle("Gyroscope (deg/s)", color='w')
        self.gyro_x_line = self.gyro_plot.plot(pen=pg.mkPen(color='r', width=2), name='X')
        self.gyro_y_line = self.gyro_plot.plot(pen=pg.mkPen(color='g', width=2), name='Y')
        self.gyro_z_line = self.gyro_plot.plot(pen=pg.mkPen(color='b', width=2), name='Z')
        self.gyro_plot.addLegend()

    def create_header(self):
        header = QWidget()
        header_layout = QHBoxLayout(header)
        
        # Logo
        logo_label = QLabel()
        try:
            logo_pixmap = QPixmap("logo1.jpg")
            scaled_logo = logo_pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(scaled_logo)
        except:
            logo_label.setText("Logo")  # Fallback if logo file is missing
        
        # Title
        title = QLabel("Parikshit Student Satellite \n \t \t \t \tCanSat Ground Station")
        title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: white;
            margin: 10px;
        """)
        
        header_layout.addWidget(logo_label)
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        return header

    def create_navigation(self):
        nav = QWidget()
        nav_layout = QHBoxLayout(nav)
        
        # Create navigation buttons with fallback for missing icons
        monitoring_btn = ModernButton("Monitoring")
        gps_btn = ModernButton("GPS Data")
        telemetry_btn = ModernButton("Telemetry")
        
        # Connect buttons
        monitoring_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        gps_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        telemetry_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(2))
        
        nav_layout.addWidget(monitoring_btn)
        nav_layout.addWidget(gps_btn)
        nav_layout.addWidget(telemetry_btn)
        
        return nav

    def create_monitoring_page(self):
        page = QWidget()
        layout = QGridLayout(page)
        
        # Create graph widgets using pyqtgraph
        altitude_card = self.create_graph_card("Altitude (m)", self.altitude_plot)
        speed_card = self.create_graph_card("Speed (m/s)", self.speed_plot)
        acceleration_card = self.create_graph_card("Acceleration (m/s²)", self.acceleration_plot)
        gyro_card = self.create_graph_card("Gyroscope", self.gyro_plot)
        
        # Add cards to layout in a grid
        layout.addWidget(altitude_card, 0, 0)
        layout.addWidget(speed_card, 0, 1)
        layout.addWidget(acceleration_card, 1, 0)
        layout.addWidget(gyro_card, 1, 1)
        
        return page

    def create_graph_card(self, title, plot_widget):
        card = DataCard(title)
        layout = QVBoxLayout(card)
        layout.addWidget(plot_widget)
        return card

    def create_gps_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        
        # GPS Status Card
        gps_status = DataCard("GPS Status")
        gps_layout = QGridLayout(gps_status)
        
        # Add GPS information
        self.lat_label = QLabel("Latitude: --")
        self.lon_label = QLabel("Longitude: --")
        self.alt_label = QLabel("GPS Altitude: --")
        
        gps_layout.addWidget(self.lat_label, 0, 0)
        gps_layout.addWidget(self.lon_label, 0, 1)
        gps_layout.addWidget(self.alt_label, 1, 0)
        
        layout.addWidget(gps_status)
        
        return page

    def create_telemetry_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        
        # Control Panel
        control_panel = DataCard("Control Panel")
        control_layout = QGridLayout(control_panel)
        
        # Add control buttons
        start_btn = ModernButton("Start Recording")
        stop_btn = ModernButton("Stop Recording")
        calibrate_btn = ModernButton("Calibrate Sensors")
        
        # Connect buttons
        start_btn.clicked.connect(self.db.start)
        stop_btn.clicked.connect(self.db.stop)
        calibrate_btn.clicked.connect(self.calibrate_sensors)
        
        control_layout.addWidget(start_btn, 0, 0)
        control_layout.addWidget(stop_btn, 0, 1)
        control_layout.addWidget(calibrate_btn, 1, 0, 1, 2)
        
        layout.addWidget(control_panel)
        
        return page

    def setup_timers(self):
        # Update timer for sensor data
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_data)
        self.update_timer.start(500)  # Update every 500ms

    def update_data(self):
        try:
            data = self.ser.getData()
            if data:
                # Update data buffers
                self.times = np.roll(self.times, -1)
                self.times[-1] = data[0]
                
                self.altitudes = np.roll(self.altitudes, -1)
                self.altitudes[-1] = data[1]
                
                self.speeds = np.roll(self.speeds, -1)
                self.speeds[-1] = data[8]  # Assuming speed is in data[8]
                
                self.accelerations = np.roll(self.accelerations, -1)
                self.accelerations[-1] = np.sqrt(data[8]**2 + data[9]**2 + data[10]**2)
                
                self.gyro_x = np.roll(self.gyro_x, -1)
                self.gyro_x[-1] = data[5]
                
                self.gyro_y = np.roll(self.gyro_y, -1)
                self.gyro_y[-1] = data[6]
                
                self.gyro_z = np.roll(self.gyro_z, -1)
                self.gyro_z[-1] = data[7]
                
                # Update plots
                self.update_plots()
                
                # Store data
                self.db.guardar(data)
        except Exception as e:
            print(f"Error updating data: {e}")

    def update_plots(self):
        # Update all plot lines with new data
        self.altitude_line.setData(self.times, self.altitudes)
        self.speed_line.setData(self.times, self.speeds)
        self.acceleration_line.setData(self.times, self.accelerations)
        self.gyro_x_line.setData(self.times, self.gyro_x)
        self.gyro_y_line.setData(self.times, self.gyro_y)
        self.gyro_z_line.setData(self.times, self.gyro_z)

    def calibrate_sensors(self):
        print("Calibrating sensors...")
        # Implement your calibration logic here

def main():
    # Enable High DPI scaling
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle(QStyleFactory.create("Fusion"))
    
    # Create dark palette
    dark_palette = QPalette()
    dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.WindowText, Qt.white)
    dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
    dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
    dark_palette.setColor(QPalette.ToolTipText, Qt.white)
    dark_palette.setColor(QPalette.Text, Qt.white)
    dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ButtonText, Qt.white)
    dark_palette.setColor(QPalette.BrightText, Qt.red)
    dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.HighlightedText, Qt.black)
    
    app.setPalette(dark_palette)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()