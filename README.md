# Omen Fan & HyperX Battery KDE Tray 

A lightweight, native PyQt6 system tray widget for KDE Plasma. Built specifically to control HP Omen laptop fans (via NBFC) and monitor the battery level of the HyperX Cloud Stinger 2 Wireless headset without relying on massive, bloated manufacturer apps.

I built this on Manjaro (Kernel 6.18) because I wanted a clean UI without opening a terminal every time my headset started beeping or my laptop got hot.

## Features
* **Fan Control:** Granular slider (10% to 100%) that interfaces with `nbfc`.
* **Power Profiles:** Automatically switches Linux power profiles (`powerprofilesctl`) based on fan speed.
* **One-Click Modes:** 'Auto Mode' and 'Completely Silent' (kills NBFC and forces power-saver).
* **Battery Monitor:** On-demand HID polling for the HyperX Cloud Stinger 2 Wireless headset with a dynamic, color-coded progress bar.

## Prerequisites
You will need the following installed on your system:
* `python3`
* `python-pyqt6`
* `python-hidapi`
* `nbfc` (NoteBook FanControl)
* `powerprofilesctl`

## Installation & Setup (The Workarounds)

Because this app runs in the background, it cannot prompt for a `sudo` password. To make the hardware calls work silently, you must configure the following permissions:

### 1. Headset Battery (`udev` rules)
To allow the script to read the headset's battery without root privileges:
1. Find your headset's Vendor ID using `lsusb`.
2. Create a new rule: `sudo nano /etc/udev/rules.d/99-hyperx-battery.rules`
3. Add the following line (replace `0951` with your actual vendor ID if different):
   ```text
    SUBSYSTEMS=="usb", ATTRS{idProduct}=="018b", ATTRS{idVendor}=="03f0", MODE="0666"
    SUBSYSTEMS=="usb", ATTRS{idProduct}=="0696", ATTRS{idVendor}=="03f0", MODE="0666"
    SUBSYSTEMS=="usb", ATTRS{idProduct}=="1718", ATTRS{idVendor}=="0951", MODE="0666"
    SUBSYSTEMS=="usb", ATTRS{idProduct}=="0d93", ATTRS{idVendor}=="03f0", MODE="0666"
    ```
4. Reload the rules: `sudo udevadm control --reload-rules && sudo udevadm trigger`

### 2. Fan Service (`sudoers` NOPASSWD)

To allow the widget to start and stop the `nbfc_service` without a password prompt:

1. Run `sudo visudo`
2. Add this line to the bottom, replacing `your_username` with your actual Linux user:
```text
your_username ALL=(ALL) NOPASSWD: /usr/bin/systemctl start nbfc_service, /usr/bin/systemctl stop nbfc_service

```

### 3. Running the App

Clone the repo and run the main script:

```bash
git clone https://github.com/gameocoder/omen-hyperx-kde-tray.git
cd omen-hyperx-kde-tray
python3 main.py
```

*(Tip: Add `main.py` to your KDE Autostart settings so it launches on boot!)*

## Credits & Acknowledgments

The core HID byte-array logic for reading the HyperX battery was adapted from https://github.com/deividgermano/gnome-hyperx-battery-indicator. Massive thanks to them for figuring out the hardware polling so I could wrap it for KDE Plasma!

## License

MIT License. Feel free to fork this, rip out the Omen stuff, or adapt the battery script for your own weird hardware combinations.
