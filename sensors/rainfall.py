"""
Rainfall sensor.

Simulates rainfall intensity in mm/hour.
- Most of the time it's dry (0 mm/h) or light drizzle.
- Occasionally a rain event pushes intensity up using a gamma distribution,
  which naturally produces a skewed shape (lots of light rain, rare heavy rain).
- A "heavy_rainfall" scenario event forces a sustained heavy reading.
"""

import random
from .base import BaseSensor


class RainfallSensor(BaseSensor):
    sensor_type = "rainfall"
    unit = "mm/h"

    # Probability that it starts/continues raining on any given tick
    RAIN_CHANCE = 0.15
    MAX_NORMAL_MM_H = 15.0
    MAX_HEAVY_MM_H = 150.0

    def _initial_value(self) -> float:
        return 0.0

    def read(self, event_state: dict | None = None) -> float:
        if event_state and event_state.get("type") == "heavy_rainfall":
            intensity = event_state.get("intensity", 0.8)
            value = 40 + intensity * (self.MAX_HEAVY_MM_H - 40)
            value += random.uniform(-5, 5)
            self.last_value = max(0.0, value)
            return self.last_value

        if random.random() < self.RAIN_CHANCE:
            value = random.gammavariate(2.0, 2.0)  # skewed toward light rain
            value = min(value, self.MAX_NORMAL_MM_H)
        else:
            # dry, but don't drop to 0 instantly if it was already raining
            value = max(0.0, self.last_value * random.uniform(0.0, 0.5))

        self.last_value = value
        return value