from enum import Enum
from re import L
import typing as T

from constants import GAS_SENSOR_TOPIC, PRESSURE_SENSOR_TOPIC


class SensorType(Enum):

    UNKNOWN = 0
    PRESSURE = 1
    ARGON = 2


class Sensor:
    """
    Implements a simulated sensor

    For the sake of simplicity, all curves are interpolated linearly.

    Extrapolation is done beyond the curve by using flat values -- i.e the first value
    of the curve will be used
    """

    def __init__(self, name: str, sensor_type: SensorType, dt: float = 1.0) -> None:
        self.name = name
        self.sensor_type = sensor_type
        self.dt = dt  # [hz]
        self._time = 0.0 - self.dt  # start at zero time after init step
        self._value: T.Optional[float] = None
        self._curve: T.List[T.Tuple[float, float]] = list()

        self._curve_min_t: float = None
        self._curve_max_t: float = None

        self._configure()

    def _configure(self) -> str:
        if self.sensor_type == SensorType.PRESSURE:
            self.units = "atm"
            self.topic = PRESSURE_SENSOR_TOPIC
        elif self.sensor_type == SensorType.ARGON:
            self.units = "ppm"
            self.topic = GAS_SENSOR_TOPIC
        else:
            self.units = ""
            self.topic = ""

    def initialize(self):
        """
        Initialize to a starting value.

        This should be run after a curve is added to initialize the sensor.
        """
        self._time = 0.0 - self.dt
        self.step()

    def set_curve_point(self, _t: float, _value: float) -> None:
        for idx, _pt in enumerate(self._curve):
            if _pt[0] == _t:
                raise ValueError(f"A value for time={_t} already exists in the curve")
            if _pt[0] > _t:
                self._curve.insert(idx, (_t, _value))
                break
        else:
            self._curve.append((_t, _value))

        # update endpoints
        self._curve_min_t = min([x[0] for x in self._curve])
        self._curve_max_t = max([x[0] for x in self._curve])

    @property
    def curve_min_t(self) -> float:
        if self._curve_min_t is None:
            return float('nan')
        return self._curve_min_t

    @property
    def curve_max_t(self) -> float:
        """
        Get the current maximum timestamp.
        """
        if self._curve_max_t is None:
            return float('nan')
        return self._curve_max_t

    @property
    def value(self) -> float:
        """
        Return the current value of the sensor.
        """
        if self._value is not None:
            return self._value
        return float('nan')

    def step(self, steps: int = 1):
        """
        Advance sensor time.
        """
        if steps <= 0:
            return
        self._step()
        self.step(steps = steps - 1)

    def _step(self):
        """
        Single step
        """
        self._time += self.dt
        if self._time >= self.curve_max_t:
            self._value = self._curve[-1][1]
            return
        if self._time <= self.curve_min_t:
            self._value = self._curve[0][1]
            return

        lower_idx = self.get_curve_borders(self._time)
        if lower_idx is None:
            # this will just use the previously known value
            # TODO: there's a lot of room for this logic to go wrong, should probably
            # come up with a better solution for when the current value is 'nan'...
            return

        upper_idx = lower_idx + 1
        lower_pt = self._curve[lower_idx]
        upper_pt = self._curve[upper_idx]
        slope = (upper_pt[1] - lower_pt[1]) / (upper_pt[0] - lower_pt[0])

        self._value += slope * self.dt

    def get_curve_borders(self, _t: float) -> T.Optional[int]:
        """
        Get the index of the curve lower boundary. The upper boundary can be calculated
        as one plus the return of this method.
        """
        for idx, _pts in enumerate(zip(self._curve[:-1], self._curve[1:])):
            prev_, next_ = _pts
            if prev_[0] <= _t and next_[0] >= _t:
                return idx
        return None
