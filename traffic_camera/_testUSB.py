"""Testing Serial Read for OPS with OY feature."""

import serial_interface

serial_interface.connect_USB()

if __name__ == "__main__":
    # serial_interface.send_config()
    # serial_interface.persist_config()
    serial_interface.read_config()
    while True:
        print(serial_interface.serialInst.readline().decode("utf-8").strip())
