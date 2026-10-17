"""Share radar readings with the web process without opening the serial port twice."""

import json
import os
import tempfile
import time


RADAR_STATUS_PATH = os.environ.get(
    "RADAR_STATUS_PATH", "/tmp/traffic-camera-radar.json"
)


class RadarPublisher:
    def __init__(self, path=RADAR_STATUS_PATH):
        self.path = path
        self.last_speed = None
        self.last_seen = None

    def reading(self, speed):
        self.last_speed = speed
        self.last_seen = time.time()
        self.heartbeat()

    def heartbeat(self):
        directory = os.path.dirname(self.path) or "."
        temporary_path = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", dir=directory, delete=False
            ) as temporary:
                temporary_path = temporary.name
                json.dump(
                    {
                        "heartbeat": time.time(),
                        "last_speed": self.last_speed,
                        "last_seen": self.last_seen,
                    },
                    temporary,
                )
            os.replace(temporary_path, self.path)
        except OSError as error:
            print(f"Could not publish radar status: {error}", flush=True)
            if temporary_path and os.path.exists(temporary_path):
                try:
                    os.unlink(temporary_path)
                except OSError:
                    pass
