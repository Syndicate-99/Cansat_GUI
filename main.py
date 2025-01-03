import sys
from pyqtgraph.Qt import QtGui, QtCore, QtWidgets
import pyqtgraph as pg
from communication import Communication
from dataBase import data_base
from PyQt5.QtWidgets import (
    QPushButton, QLabel, QStackedWidget, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout
)
from PyQt5.QtGui import QPixmap
from graphs.graph_acceleration import graph_acceleration
from graphs.graph_altitude import graph_altitude
from graphs.graph_battery import graph_battery
from graphs.graph_free_fall import graph_free_fall
from graphs.graph_gyro import graph_gyro
from graphs.graph_pressure import graph_pressure
from graphs.graph_speed import graph_speed
from graphs.graph_temperature import graph_temperature
from graphs.graph_time import graph_time

pg.setConfigOption('background', (0, 0, 0))
pg.setConfigOption('foreground', (197, 198, 199))

# Interface variables
app = QtWidgets.QApplication(sys.argv)

# Create the main window
main_window = QtWidgets.QWidget()
main_layout = QtWidgets.QVBoxLayout(main_window)

# Create a stacked widget to hold multiple pages
stacked_widget = QStackedWidget()

# =======================
# Monitoring Page (Page 1)
# =======================

# Create monitoring page
page1 = QWidget()
page1_layout_widget = QVBoxLayout()
page1.setLayout(page1_layout_widget)

# Create GraphicsView and GraphicsLayout for graphs
view = pg.GraphicsView()
Layout = pg.GraphicsLayout()
view.setCentralItem(Layout)
page1_layout_widget.addWidget(view)

# Add "PARIKSHIT STUDENT SATELLITE" text and logo in the top left corner
proxy_logo = QtWidgets.QGraphicsProxyWidget()
logo_label = QLabel()
logo_pixmap = QPixmap("logo1.jpg")
scaled_logo = logo_pixmap.scaled(100, 100, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
logo_label.setPixmap(scaled_logo)
logo_label.setStyleSheet("background-color: black; color: white; font-size: 16px; padding: 5px;")
logo_label.setFixedWidth(200)
proxy_logo.setWidget(logo_label)
Layout.addItem(proxy_logo, row=0, col=0)

# Title at top
title_text = """Flight monitoring interface for cansats and OBC's developed by Parikshit Student Satellite."""
title_label = QLabel(title_text)
title_label.setStyleSheet("background-color: black; color: white; font-size: 28px; font-weight: bold;")
title_label.setAlignment(QtCore.Qt.AlignCenter)
proxy_title_label = QtWidgets.QGraphicsProxyWidget()
proxy_title_label.setWidget(title_label)
Layout.addItem(proxy_title_label, row=0, col=1, colspan=21)
Layout.nextRow()

# Vertical label
vertical_label = QLabel("P\nA\nR\nI\nK\nS\nH\nI\nT\n\nS\nT\nU\nD\nE\nN\nT\n\nS\nA\nT\nE\nL\nL\nI\nT\nE")
vertical_label.setStyleSheet("background-color: black; color: white; font-size: 24px;")
vertical_label.setAlignment(QtCore.Qt.AlignCenter)
proxy_vertical_label = QtWidgets.QGraphicsProxyWidget()
proxy_vertical_label.setWidget(vertical_label)
Layout.addItem(proxy_vertical_label, row=1, col=0, rowspan=5)

# Declare graphs
altitude = graph_altitude()
speed = graph_speed()
acceleration = graph_acceleration()
gyro = graph_gyro()
pressure = graph_pressure()
temperature = graph_temperature()
time = graph_time()
battery = graph_battery()
free_fall = graph_free_fall()

# Altitude and Speed Graphs Layout
l1 = Layout.addLayout(colspan=12, rowspan=2)
l11 = l1.addLayout(rowspan=1, border=(83, 83, 83))
l11.addItem(altitude)
l11.addItem(speed)
l1.nextRow()

# Acceleration, Gyro, Pressure, and Temperature Graphs
l12 = l1.addLayout(colspan=12, rowspan=4, border=(100, 100, 100))
l12.addItem(acceleration)
l12.addItem(gyro)
l12.addItem(pressure)
l12.addItem(temperature)

# Time, Battery, and Free Fall Graphs
l3 = Layout.addLayout(colspan=0, rowspan=0, border=(1, 1, 1))
l3.addItem(time)
l3.nextRow()

l4 = Layout.addLayout(colspan=0, rowspan=0, border=(1, 83, 83))
l4.addItem(battery)
l4.nextRow()

l5 = Layout.addLayout(colspan=0, rowspan=0, border=(83, 83, 83))
l5.addItem(free_fall)

# Add monitoring page to stacked widget
stacked_widget.addWidget(page1)

# =================================
# Second Page (Additional Settings)
# =================================

# =================================
# Second Page (Probable Landing Spot and GPS Data)
# =================================

page2 = QWidget()
page2_layout = QVBoxLayout()
page2.setLayout(page2_layout)

# Add title label for the second page
second_page_label = QLabel("GPS data and Landing Spot")
second_page_label.setStyleSheet("font-size: 24px; font-weight: bold; color: blue;")
second_page_label.setAlignment(QtCore.Qt.AlignCenter)
page2_layout.addWidget(second_page_label)

# Create GroupBox for Landing Spot
landing_spot_groupbox = QtWidgets.QGroupBox("Probable Landing Spot (Lat, Long)")
landing_spot_groupbox.setStyleSheet("""
    QGroupBox {
        font-size: 18px;
        font-weight: bold;
        color: black;
    }
    QLabel {
        font-size: 16px;
        padding: 10px;
    }
""")
landing_spot_layout = QVBoxLayout()

# Label to display landing spot coordinates
landing_spot_label = QLabel("Latitude: --, Longitude: --")
landing_spot_label.setStyleSheet("font-size: 18px; padding: 5px; border: 1px solid gray;")
landing_spot_layout.addWidget(landing_spot_label)
landing_spot_groupbox.setLayout(landing_spot_layout)

# Add the GroupBox for landing spot to the second page layout
page2_layout.addWidget(landing_spot_groupbox)

# Create GroupBox for GPS Data
gps_data_groupbox = QtWidgets.QGroupBox("GPS Data")
gps_data_groupbox.setStyleSheet("""
    QGroupBox {
        font-size: 18px;
        font-weight: bold;
        color: black;
    }
    QLabel {
        font-size: 16px;
        padding: 10px;
    }
""")
gps_data_layout = QVBoxLayout()

# Label to display GPS data
gps_data_label = QLabel("GPS Data: --")
gps_data_label.setStyleSheet("font-size: 18px; padding: 5px; border: 1px solid gray;")
gps_data_layout.addWidget(gps_data_label)
gps_data_groupbox.setLayout(gps_data_layout)

# Add the GroupBox for GPS data to the second page layout
page2_layout.addWidget(gps_data_groupbox)

# Add the second page to the stacked widget
stacked_widget.addWidget(page2)


# ========================
# Telemetry Data Page (Page 3)
# ========================

# Create telemetry data page
page3 = QWidget()
page3_layout = QVBoxLayout()
page3.setLayout(page3_layout)

# Add a label for the page
telemetry_label = QLabel("Telemetry Data")
telemetry_label.setStyleSheet("font-size: 24px; font-weight: bold; color: black;")
telemetry_label.setAlignment(QtCore.Qt.AlignCenter)
page3_layout.addWidget(telemetry_label)

# Define button style
button_style = """
    background-color: rgb(0, 102, 204);
    color: white;
    font-size: 18px;
    padding: 10px 20px;
    border-radius: 5px;
    border: 2px solid white;
"""

# Declare Communication and Database objects
ser = Communication()
data_base = data_base()

# Define buttons
start_storage_button = QPushButton('Start Storage')
start_storage_button.setStyleSheet(button_style)
start_storage_button.clicked.connect(data_base.start)

stop_storage_button = QPushButton('Stop Storage')
stop_storage_button.setStyleSheet(button_style)
stop_storage_button.clicked.connect(data_base.stop)

parachute_button = QPushButton('Parachute Release')
parachute_button.setStyleSheet(button_style)
parachute_button.clicked.connect(lambda: print("Parachute Released"))

calibrate_button = QPushButton('Calibrate')
calibrate_button.setStyleSheet(button_style)
calibrate_button.clicked.connect(lambda: print("Calibration started"))

# Arrange buttons in a grid layout
buttons_layout = QGridLayout()
buttons_layout.addWidget(start_storage_button, 0, 0)
buttons_layout.addWidget(stop_storage_button, 0, 1)
buttons_layout.addWidget(parachute_button, 1, 0)
buttons_layout.addWidget(calibrate_button, 1, 1)
page3_layout.addLayout(buttons_layout)

# Add telemetry data page to stacked widget
stacked_widget.addWidget(page3)

# ===========================
# Page Navigation Buttons
# ===========================

# Create buttons to switch between pages
switch_button_to_page1 = QPushButton('Go to Monitoring Page')
switch_button_to_page2 = QPushButton('Go to Second Page')
switch_button_to_page3 = QPushButton('Go to Telemetry Data')

# Connect buttons to switch between pages
switch_button_to_page1.clicked.connect(lambda: stacked_widget.setCurrentIndex(0))
switch_button_to_page2.clicked.connect(lambda: stacked_widget.setCurrentIndex(1))
switch_button_to_page3.clicked.connect(lambda: stacked_widget.setCurrentIndex(2))

# Arrange switch buttons in a horizontal layout
switch_buttons_layout = QHBoxLayout()
switch_buttons_layout.addWidget(switch_button_to_page1)
switch_buttons_layout.addWidget(switch_button_to_page2)
switch_buttons_layout.addWidget(switch_button_to_page3)

# Add switch buttons and stacked widget to the main layout
main_layout.addLayout(switch_buttons_layout)
main_layout.addWidget(stacked_widget)

# Show the main window
main_window.setWindowTitle('Flight Monitoring and Telemetry Data')
main_window.resize(1200, 700)
main_window.show()

# ======================================
# Update Functions and Timers
# ======================================

# Fonts for text items
font = QtGui.QFont()
font.setPixelSize(90)

# Initialize the update logic
start_time = QtCore.QTime.currentTime()  # Start the time as soon as the program starts

def update():
    try:
        value_chain = ser.getData()
        # Update all the graphs with new data
        altitude.update(value_chain[1])
        speed.update(value_chain[8], value_chain[9], value_chain[10])
        time.update(value_chain[0])
        acceleration.update(value_chain[8], value_chain[9], value_chain[10])
        gyro.update(value_chain[5], value_chain[6], value_chain[7])
        pressure.update(value_chain[4])
        temperature.update(value_chain[3])
        free_fall.update(value_chain[2])
        data_base.guardar(value_chain)
    except IndexError:
        print('Starting, please wait a moment')

# Function to track and update time immediately
def update_time():
    current_time = QtCore.QTime.currentTime()
    elapsed_time = start_time.secsTo(current_time)
    time.update(elapsed_time)

# Start the update and time timers
timer = pg.QtCore.QTimer()
timer.timeout.connect(update)
timer.start(500)  # Update every 500 ms

time_timer = pg.QtCore.QTimer()
time_timer.timeout.connect(update_time)
time_timer.start(1000)  # Update every second for the time

# Start Qt event loop
if __name__ == '__main__':
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        app.exec_()
