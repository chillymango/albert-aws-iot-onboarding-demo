"""
Run this module to run the sim.

This should start the three pressure sensors, the gas sensor, and the listener.
"""
import argparse
import threading
import typing as T

from constants import GAS_SENSOR
from constants import PRESSURE_SENSOR_A
from constants import PRESSURE_SENSOR_B
from constants import PRESSURE_SENSOR_C

from mqtt import MQTTClient
from runner import SensorThread
from sensor import Sensor
from sensor import SensorType

SCENARIOS = {
    "nominal_all": {
        PRESSURE_SENSOR_A: [
            (0, 0),
            (2, 0),
            (3, 1),
            (5, 1),
        ],
        PRESSURE_SENSOR_B: [
            (0, 0),
            (2, 0),
            (3, 1),
            (5, 1),
        ],
        PRESSURE_SENSOR_C: [
            (0, 0),
            (2, 0),
            (3, 1),
            (5, 1),
        ],
        GAS_SENSOR: [
            (0, 0),
            (5, 0)
        ]
    },
}


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("scenario", choices=SCENARIOS, help="sensor scenario to simulate")
    parser.add_argument("--dt", type=float, default=1.0, help="update rate")
    parser.add_argument(
        "--duration",
        help="override duration. By default plots 3s longer than end of time specification"
    )
    return parser


def start_threads(scenario: str, dt: float, duration: float) -> T.List[threading.Thread]:
    sensor_curves = SCENARIOS[scenario]
    all_threads = list()
    for sensor_name, curve in sensor_curves.items():
        if "pressure" in sensor_name:
            sensor_type = SensorType.PRESSURE
        elif "gas" in sensor_name:
            sensor_type = SensorType.ARGON
        else:
            sensor_type = SensorType.UNKNOWN

        sensor = Sensor(
            name=sensor_name,
            sensor_type=sensor_type,
            dt=dt,
        )
        for _t, _val in curve:
            sensor.set_curve_point(_t, _val)
        
        mqtt_client = MQTTClient.create_from_device_name(sensor_name)

        all_threads.append(SensorThread(sensor, mqtt_client, duration))

    for thread in all_threads:
        thread.start()

    return all_threads


def get_scenario_duration(scenario_name: str) -> float:
    """
    Calculate default scenario length.
    """
    scenario = SCENARIOS[scenario_name]
    max_time = 0
    for pts in scenario.values():
        max_time = max(max_time, max([pt[0] for pt in pts]))
    return max_time + 3.0


def main() -> None:
    parser = get_parser()
    args = parser.parse_args()

    duration = args.duration or get_scenario_duration(args.scenario)

    all_threads = start_threads(args.scenario, dt=args.dt, duration=duration)
    for th in all_threads:
        th.join()


if __name__ == "__main__":
    main()
