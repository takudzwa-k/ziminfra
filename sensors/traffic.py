"""
Traffic counter sensor.

Simulates vehicle throughput in vehicles/hour using a diurnal (time-of-day)
pattern: low overnight, morning rush peak, midday lull, evening rush peak.
"""

import math
import random
from datetime import datetime
from .base import BaseSensor


class TrafficSensor(BaseSensor):
    sensor_type = "traffic"
    unit = "vehicles/hour"

    MAX_VPH = 3000

    def _initial_value(self) -> float:
        return 200

    def _time_of_day_factor(self, now: datetime) -> float:
        hour = now.hour + now.minute / 60.0
        # Two peaks: ~7-9am and ~4-6pm, modeled as sum of two gaussians
        morning_peak = math.exp(-((hour - 8) ** 2) / (2 * 1.2 ** 2))
        evening_peak = math.exp(-((hour - 17) ** 2) / (2 * 1.5 ** 2))
        overnight_floor = 0.05
        return min(1.0, overnight_floor + morning_peak + evening_peak)

    def read(self, event_state: dict | None = None, now: datetime | None = None) -> float:
        now = now or datetime.now()
        factor = self._time_of_day_factor(now)
        target = factor * self.MAX_VPH
        noise = random.uniform(-0.1, 0.1) * self.MAX_VPH

        # smooth toward target instead of jumping
        value = self.last_value + 0.3 * (target - self.last_value) + noise
        value = max(0, min(self.MAX_VPH, value))

        self.last_value = value
        return round(value)