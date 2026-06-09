import subprocess
import sys

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import (
    QApplication,
    QLabel,
    QMenu,
    QProgressBar,
    QPushButton,
    QSlider,
    QSystemTrayIcon,
    QVBoxLayout,
    QWidget,
)

import hyprx_batt_lvl as headphones

#config
icon = "./hpomen.png"

def set_fan_speed(value):
    if silent_action.isChecked():
        silent_action.blockSignals(True)
        silent_action.setChecked(False)
        silent_action.blockSignals(False)
        subprocess.run(["sudo", "systemctl", "start", "nbfc_service"])

    subprocess.run(["nbfc", "set", "-s", str(value)])

    if value < 20:
        subprocess.run(["powerprofilesctl", "set", "power-saver"])
    else:
        subprocess.run(["powerprofilesctl", "set", "performance"])


def set_auto():
    if silent_action.isChecked():
        silent_action.blockSignals(True)
        silent_action.setChecked(False)
        silent_action.blockSignals(False)

    subprocess.run(["sudo", "systemctl", "start", "nbfc_service"])
    subprocess.run(["nbfc", "set", "-a"])
    subprocess.run(["powerprofilesctl", "set", "balanced"])


def toggle_silent(checked):
    if checked:
        subprocess.run(["sudo", "systemctl", "stop", "nbfc_service"])
        subprocess.run(["powerprofilesctl", "set", "power-saver"])
        slider_window.label.setText("Speed: 0% (NBFC KILLED)")
        slider_window.slider.blockSignals(True)
        slider_window.slider.setValue(0)
        slider_window.slider.blockSignals(False)
    else:
        set_auto()


class FanControlWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Omen Fan Control")
        self.setFixedSize(250, 100)

        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)

        layout = QVBoxLayout()

        self.label = QLabel("Speed: 50% (2700 RPM)")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setMinimum(10)
        self.slider.setMaximum(100)
        self.slider.setSingleStep(10)
        self.slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.slider.setTickInterval(10)
        self.slider.setValue(50)

        self.slider.valueChanged.connect(self.update_label)
        self.slider.sliderReleased.connect(lambda: set_fan_speed(self.slider.value()))

        layout.addWidget(self.slider)
        self.setLayout(layout)

    def update_label(self, value):
        rpm = value * 54
        self.label.setText(f"Speed: {value}% ({rpm} RPM)")


class HyperXBatteryWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HyperX Cloud Stinger 2 Wireless")

        self.setFixedSize(250, 140)
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)

        layout = QVBoxLayout()
        layout.setSpacing(10)

        self.title_label = QLabel("<b>HyperX Cloud Stinger 2</b>")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("Checking...")
        layout.addWidget(self.progress_bar)

        self.refresh_btn = QPushButton("Refresh Battery")

        self.refresh_btn.setStyleSheet("""
            QPushButton {
                padding: 5px;
                border-radius: 4px;
                background-color: #333;
                color: white;
            }
            QPushButton:hover { background-color: #444; }
            QPushButton:pressed { background-color: #222; }
            QPushButton:disabled { background-color: #555; color: #888; }
        """)

        self.refresh_btn.clicked.connect(self.update_battery)
        layout.addWidget(self.refresh_btn)

        self.setLayout(layout)

        self.update_battery()

    def update_battery(self):
        self.refresh_btn.setEnabled(False)
        self.progress_bar.setFormat("Checking...")
        QApplication.processEvents()

        try:
            battery = headphones.get_battery()

            if battery is not None:
                val = int(battery)
                self.progress_bar.setValue(val)
                self.progress_bar.setFormat("%p%")

                if val > 50:
                    bar_color = "#4CAF50"
                elif val > 20:
                    bar_color = "#FF9800"
                else:
                    bar_color = "#F44336"
                self.progress_bar.setStyleSheet(f"""
                    QProgressBar {{
                        border: 2px solid #444;
                        border-radius: 5px;
                        background-color: #222;
                        color: white;
                        font-weight: bold;
                    }}
                    QProgressBar::chunk {{
                        background-color: {bar_color};
                        border-radius: 3px;
                    }}
                """)
            else:
                self.progress_bar.setValue(0)
                self.progress_bar.setFormat("Headset Not Found / Off")
                self.progress_bar.setStyleSheet("")

        except Exception as e:
            print(f"Error checking battery: {e}")
            self.progress_bar.setValue(0)
            self.progress_bar.setFormat("Error Reading Battery")
            self.progress_bar.setStyleSheet("")

        self.refresh_btn.setEnabled(True)


app = QApplication(sys.argv)
app.setQuitOnLastWindowClosed(False)

tray = QSystemTrayIcon()
tray.setIcon(QIcon(icon))
tray.setToolTip("Omen Granular Fan Control")

slider_window = FanControlWindow()
hx_batt_level = HyperXBatteryWindow()

menu = QMenu()

open_action = QAction("Open Slider Control", menu)
open_action.triggered.connect(slider_window.showNormal)
open_action.triggered.connect(slider_window.activateWindow)
menu.addAction(open_action)

auto_action = QAction("Auto Mode", menu)
auto_action.triggered.connect(set_auto)
menu.addAction(auto_action)

battery_action = QAction("HyperX Battery Level", menu)
battery_action.triggered.connect(hx_batt_level.showNormal)
battery_action.triggered.connect(hx_batt_level.activateWindow)
menu.addAction(battery_action)

menu.addSeparator()

silent_action = QAction("Completely Silent (Kill NBFC)", menu)
silent_action.setCheckable(True)
silent_action.toggled.connect(toggle_silent)
menu.addAction(silent_action)

quit_action = QAction("Quit", menu)
quit_action.triggered.connect(app.quit)
menu.addAction(quit_action)

tray.setContextMenu(menu)
tray.show()

sys.exit(app.exec())
