import unittest
from sensor import Sensor
from sensor import SensorType


class TestSensorInterpolation(unittest.TestCase):
    """
    Test out some edge cases for the sensor curve interpolation
    """

    def setUp(self):
        self.sensor = Sensor(name="test-sensor", sensor_type=SensorType.PRESSURE)

    def test_sensor_insert_empty_curve(self):
        """
        Insert a point into an empty curve. Ensure that the insertion succeeds.
        """
        self.sensor.set_curve_point(1, 1)
        self.assertEqual(len(self.sensor._curve), 1)

    def test_sensor_insert_multiple(self):
        """
        Insert three points into the curve. Make sure they show up in the curve
        sorted by timestamp.
        """
        self.sensor.set_curve_point(2, 2)
        self.sensor.set_curve_point(1, 1)
        self.sensor.set_curve_point(3, 1)
        timestamps = [x[0] for x in self.sensor._curve]
        self.assertEqual(timestamps, [1, 2, 3])

    def test_get_curve_borders_valid(self):
        """
        Create a three-point curve. Try finding the middle point.
        """
        self.sensor.set_curve_point(1, 1)
        self.sensor.set_curve_point(3, 3)
        self.sensor.set_curve_point(5, 5)
        self.assertEqual(self.sensor.get_curve_borders(4), 1)

    def test_get_curve_borders_out_of_bounds(self):
        """
        Create a three-point curve. Try finding the middle point for a
        timestamp outside the range. Ensure that it returns None.
        """
        self.sensor.set_curve_point(1, 1)
        self.sensor.set_curve_point(3, 3)
        self.sensor.set_curve_point(5, 5)
        self.assertEqual(self.sensor.get_curve_borders(6), None)


class TestSensorSimulation(unittest.TestCase):
    """
    Create a sensor with some curve. Verify the values look OK.
    """

    def setUp(self):
        """
        Make the dt != 1 to test arithmetic
        """
        self.sensor = Sensor(
            name="test-sensor",
            sensor_type=SensorType.PRESSURE,
            dt=0.5
        )
        self.sensor.set_curve_point(1, 1)
        self.sensor.set_curve_point(2, 0.5)
        self.sensor.set_curve_point(3, 0.125)
        self.sensor.set_curve_point(13, 0)

    def test_left_bound(self):
        self.sensor.initialize()
        self.assertEqual(self.sensor.value, 1)

    def test_left_center_curve(self):
        self.sensor.initialize()
        self.sensor.step(3)
        self.assertEqual(self.sensor.value, 0.75)

    def test_center_curve(self):
        self.sensor.initialize()
        self.sensor.step(5)
        self.assertAlmostEqual(self.sensor.value, (0.5 + 0.125) / 2)

    def test_right_curve(self):
        self.sensor.initialize()
        self.sensor.step(10)
        self.assertAlmostEqual(self.sensor.value, (0.1))

    def test_right_bound(self):
        self.sensor.initialize()
        self.sensor.step(100)
        self.assertEqual(self.sensor.value, 0)


if __name__ == "__main__":
    unittest.main()
