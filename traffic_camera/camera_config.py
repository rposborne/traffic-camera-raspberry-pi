# File name: camera_config.py
# Author: Christian Pedrigal (pedrigalchristian@gmail.com)
# Date created: 10/25/2021
# Date last modified: 10/25/2021
# Python Version: 1.1

import time
from picamera2 import Picamera2
from picamera2.job import Job


def capture_num_frames(send_queue, e1, receive_queue, path):
    """Create camera object and start background process for camera capture

    Parameters:
    - send_queue: puts pictures into queue for future access with Queue.get()
    - e1: an event that triggers the continuous camera capture, which runs
          indefinitely until e1 is cleared using the Event.clear()
          in data_array_any_amount() function.
    - receive_queue: receives max_speed data and parses value
                     into picture filename
    """

    # Camera Initializations
    camera = Picamera2()
    # Picamera2.set_logging(level=Picamera2.DEBUG, msg="%(levelname)s: %(message)s")
    camera.zoom = (0.35, 0.35, 0.30, 0.30)
    camera.resolution = (1920, 1080)
    # camera.color_effects = (128,128) # black and white
    camera.contrast = 13
    # camera.shutter_speed = 8000
    camera.exposure_mode = "sports"
    camera.iso = 400
    still_config = camera.create_still_configuration()
    camera.start()
    # Runs background process
    pending_writes = []

    while True:
        if e1.is_set():
            pic_array = []
            max_speed = receive_queue.get()
            i = 0
            while e1.is_set():
                filename = f"{path}/image{i:02d}_max_speed{int(max_speed):02d}.mph.jpg"

                def signal_function(job: Job):
                    pic_array.append(filename)

                    print(f"Captured {filename}!")

                    # Remove job from pending_writes list
                    pending_writes.remove(job)
                    if len(pending_writes) == 0:
                        # Puts array of images into queue after all images are captured
                        send_queue.put(pic_array)

                job = camera.switch_mode_and_capture_file(
                    still_config,
                    filename,
                    wait=None,
                    signal_function=signal_function,
                )
                pending_writes.append(job)
                i += 1

                if not e1.is_set():
                    break  # Ends camera capture process
                time.sleep(0.1)
        else:
            pass
