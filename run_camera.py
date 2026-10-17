"""Wait for the USB radar before starting the camera application."""

import os
import sys
import time

from serial.tools import list_ports


if __name__ == "__main__":
    print("Waiting for USB radar (ttyACM device)...", flush=True)
    while not any("ACM" in port.device for port in list_ports.comports()):
        time.sleep(10)

    print("USB radar found; starting traffic camera.", flush=True)
    os.execv(sys.executable, [sys.executable, os.path.join(os.path.dirname(__file__), "main.py")])
