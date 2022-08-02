"""
AWS IoT MQTT Client
"""
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from collections import namedtuple
import logging
import os
import typing as T

from constants import ENDPOINT, GAS_SENSOR
from constants import MQTT_PORT
from constants import PRESSURE_SENSOR_A
from constants import PRESSURE_SENSOR_B
from constants import PRESSURE_SENSOR_C

logger = logging.getLogger("AWSIoTPythonSDK.core")
logger.setLevel(logging.INFO)
streamHandler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)

ConnectionCredentials = namedtuple(
    "ConnectionCredentials",
    [
        "endpoint",
        "client_id",
        "root_ca",
        "cert",
        "key",
        "port"
    ]
)


MQTT_CONNECTION_INFO = {
    x: ConnectionCredentials(
        endpoint=ENDPOINT,
        client_id=x,
        root_ca=os.path.join("data", "root-CA.crt"),
        key=os.path.join("data", f"{x}.private.key"),
        cert=os.path.join("data", f"{x}.cert.pem"),
        port=MQTT_PORT,
    )
    for x in (
        PRESSURE_SENSOR_A,
        PRESSURE_SENSOR_B,
        PRESSURE_SENSOR_C,
        GAS_SENSOR,
    )
}


class MQTTClient:
    """
    Wrapper around an AWSIoTMQTTClient object
    """

    def __init__(
        self,
        name,
        connection_info: ConnectionCredentials,
    ):
        self.name = name
        self.connection_info = connection_info

        self._client = AWSIoTMQTTClient(connection_info.client_id)
        self._client.configureEndpoint(connection_info.endpoint, connection_info.port)
        self._client.configureCredentials(
            connection_info.root_ca,
            KeyPath=connection_info.key,
            CertificatePath=connection_info.cert,
        )
        self._client.connect()

    @classmethod
    def create_from_device_name(cls, device_name: str):
        """
        Create an MQTTClient from a device name
        """
        if device_name not in MQTT_CONNECTION_INFO:
            raise ValueError(f"Could not find connection info for {device_name}")

        return cls(device_name, MQTT_CONNECTION_INFO[device_name])

    def publish(self, topic: str, message: str, qos: int = 0):
        """
        Publish a message to the specified channel
        """
        if qos not in (0, 1, 2):
            raise ValueError(f"Invalid QoS value {qos}")

        self._client.publish(topic, message, QoS=qos)
