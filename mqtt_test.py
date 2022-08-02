"""
Test an MQTT connection.

Tests with pressure-sensor-a credentials in `data`:
* data/pressure-sensor-a.cert.pem
* data/pressure-sensor-a.private.key
* data/root-CA
"""
import json
import unittest

from constants import GAS_SENSOR
from constants import PRESSURE_SENSOR_A
from constants import PRESSURE_SENSOR_B
from constants import PRESSURE_SENSOR_C
from mqtt import MQTTClient


class TestMqttConnection(unittest.TestCase):

    TEST_TOPIC = "sdk/test/Python"

    def test_connection(self) -> None:
        """
        Connect as each sensor and publish a message
        """
        for dev in (PRESSURE_SENSOR_A, PRESSURE_SENSOR_B, PRESSURE_SENSOR_C, GAS_SENSOR):
            try:
                client = MQTTClient.create_from_device_name(dev)
                client.publish(self.TEST_TOPIC, json.dumps({"msg": "test message"}))
                print(f'Succeeded for device {dev}')
            except Exception:
                print(f'Failed for device {dev}')
                raise


if __name__ == "__main__":
    unittest.main()
