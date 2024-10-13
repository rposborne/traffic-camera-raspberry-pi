# File name: serial_interface.py
# Author: Christian Pedrigal (pedrigalchristian@gmail.com)
# Date created: 10/25/2021
# Date last modified: 10/25/2021
# Python Version: 1.1

import serial.tools.list_ports
from time import sleep
import json


# Initializations
ports = serial.tools.list_ports.comports()
serialInst = serial.Serial()


def connect_USB():
    """Establishes a connection to a peripheral (radar)
    via serial interface."""

    portList = [str(onePort) for onePort in ports]

    portVar = portList[0][0:12]
    print("Connected to USB Port: " + portVar + "!")

    if "ACM" not in portVar:  # Connects OPS243 to ttyACM0 port
        raise Exception("Radar Sensor not detected!")

    serialInst.baudrate = 9600
    serialInst.port = portVar
    serialInst.open()


def send_config():
    """Sends configuration settings to OPS243 radar sensor."""
    # S1 (Set Doppler Sampling Rate to 10k Hz)
    # US (mph Speed Unit Setting)
    # BV (Do not output blanks)
    # R>10 (Reported Speed Minimum Filter Setting at 10 mph)
    # OJ (Turn on JSON format)
    # M>150 (Minimum Speed Magnitude at least 150)
    _set_config(b'OJ')
    _set_config(b'Oz')
    _set_config(b'S1')
    _set_config(b'US')
    _set_config(b'BV')
    _set_config(b'R>5')
    _set_config(b'M>150')

def persist_config():
    _set_config(b'A!')

def _set_config(value):
    """Sends configuration settings to OPS243 radar sensor."""
    serialInst.write(value + b"\r\n")
    sleep(0.1)

    serialInst.flush()

    if serialInst.in_waiting:
        packet = serialInst.readline()
        data = packet.decode("utf").rstrip("\n")
        print(data)


def _serial_read_json():
    """Reads data into JSON format."""
    if serialInst.in_waiting:
        packet = serialInst.readline()
        data = packet.decode("utf").rstrip("\n")

        print(data)


def data_array_any_amount(speed_limit, queue3, e):
    """Store the bytes into a list of variable size 'array_length'.

    With a timeout, the function will run until there is a timeout.

    Parameters:
    - speed_limit: float variable that puts data exceeding this value
                   into queue3.
    - queue3: Queue object that receives speed data.
    - e: Event object that triggers on and off the camera_capture process.
    """
    # This private function is a working improvement of data_array(),
    # which aims to return arrays of variable array sizes.
    serialInst.timeout = 0.3

    if serialInst.in_waiting:

        speed_data_list = []

        sw = 0
        maxVal = 0
        while sw == 0:  # Begin reading from serial interface.
            packet = serialInst.readline()
            data = packet.decode("utf").rstrip("\r\n")
            try:
                parsed_data = json.loads(data)
            except json.JSONDecodeError:
                print("Data is not in JSON format", data)

                continue
            if parsed_data.get("speed"):
                speed = abs(float(parsed_data["speed"]))  # Read value of key 'speed'.
                speed_data_list.append(speed)  # Append speed to list.

                maxVal = max(speed_data_list)
                if maxVal > speed_limit:
                    e.set()  # Set Event object on, triggering camera_capture.
                    queue3.put(maxVal)
            else:
                sw = 1  # End data reading from serial interface.
                e.clear()  # Set Event object off, ending camera_capture.

        return (speed_data_list, maxVal)
    else:
        return (None, None)
