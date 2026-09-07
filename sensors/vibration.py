"""
Road vibration / accelerometer sensor.

Simulates a vibration index (arbitrary units, roughly g-force-like) caused by
vehicles passing over the road surface.
- Baseline vibration scales with traffic volume (more vehicles = more noise).
- A "road_deterioration" event gradually raises the baseline over time,
  modeling a pothole or surface damage getting worse.
"""

import random
from .base import BaseSensor


class VibrationSensor(BaseSensor):
    sensor_type = "vibration"
    unit = "g"

    def __init__(self, road_id: str):
        super().__init__(road_id)
        self.deterioration_offset = 0.0

    def _initial_value(self) -> float:
        return 0.3

    def read(self, event_state: dict | None = None, traffic_vph: int = 500) -> float:
        # Baseline scales with traffic: busier road -> more vibration
        traffic_factor = min(traffic_vph / 1500.0, 2.0)
        base = 0.15 + traffic_factor * 0.5

        if event_state and event_state.get("type") == "road_deterioration":
            self.deterioration_offset += event_state.get("rate", 0.02)
        else:
            # very slow natural decay if no active deterioration event
            self.deterioration_offset = max(0.0, self.deterioration_offset - 0.001)

        noise = random.uniform(-0.1, 0.1)
        value = base + self.deterioration_offset + noise
        value = max(0.0, value)

        self.last_value = value
        return value