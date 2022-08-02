"""
Threads to run sensors
"""
from threading import Thread
import json
import time

from mqtt import MQTTClient
from sensor import Sensor


class SensorThread(Thread):
    """
    A thread that runs a sensor
    """

    def __init__(self, sensor: Sensor, client: MQTTClient, duration: float = 30.0):
        super().__init__()
        self.sensor = sensor
        self.client = client
        self.dt = sensor.dt

        # even if the sensor has data that runs past the requested duration, only
        # run for the requested duration
        self.duration = float(duration)

    def run(self):
        t_init = time.time()
        self.sensor.initialize()
        while time.time() - t_init < self.duration:
            payload = {
                "name": self.sensor.name,
                "value": self.sensor.value,
                "units": self.sensor.units
            }
            self.client.publish(self.sensor.topic, json.dumps(payload))
            print(f"Published {json.dumps(payload)} to {self.sensor.topic}")
            time.sleep(self.sensor.dt)
