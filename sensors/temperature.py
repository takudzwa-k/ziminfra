"""
Temperature sensor.

Simulates ambient/road-surface temperature in degrees Celsius using a
diurnal sine wave (cool at night, hot in the afternoon) plus small random
noise. Range tuned for a Harare-like climate but easily adjustable.
"""

import math
import random
from datetime import datetime
from .base import BaseSensor


class TemperatureSensor(BaseSensor):
    sensor_type = "temperature"
    unit = "C"

    MIN_TEMP_C = 12.0
    MAX_TEMP_C = 34.0

    def _initial_value(self) -> float:
        return 20.0

    def read(self, event_state: dict | None = None, now: datetime | None = None) -> float:
        now = now or datetime.now()
        hour = now.hour + now.minute / 60.0

        mid = (self.MIN_TEMP_C + self.MAX_TEMP_C) / 2
        amplitude = (self.MAX_TEMP_C - self.MIN_TEMP_C) / 2
        # Peak temp around 15:00, trough around 03:00
        value = mid + amplitude * math.sin((hour - 9) / 24 * 2 * math.pi)
        value += random.uniform(-0.5, 0.5)

        self.last_value = value
        return value