"""
Drain / water-level sensor.

Simulates water level inside a roadside drain, in cm.
- Rises when rainfall is high, drains slowly afterward (normal drain).
- If a "blocked_drain" event is active, the drain barely lowers even after
  rain stops -- this is the signal that lets a monitoring system flag a
  blockage.
"""

import random
from .base import BaseSensor


class WaterLevelSensor(BaseSensor):
    sensor_type = "water_level"
    unit = "cm"

    NORMAL_DRAIN_RATE = 0.35   # cm drained per tick when healthy
    BLOCKED_DRAIN_RATE = 0.03  # cm drained per tick when blocked
    MAX_LEVEL_CM = 100.0

    def _initial_value(self) -> float:
        return 2.0

    def read(self, event_state: dict | None = None, rainfall_mm_h: float = 0.0) -> float:
        blocked = bool(event_state and event_state.get("type") == "blocked_drain")
        drain_rate = self.BLOCKED_DRAIN_RATE if blocked else self.NORMAL_DRAIN_RATE

        # Rainfall raises the level; higher rainfall = faster rise
        inflow = rainfall_mm_h * random.uniform(0.03, 0.06)
        outflow = drain_rate

        value = self.last_value + inflow - outflow
        value = max(0.0, min(self.MAX_LEVEL_CM, value))

        self.last_value = value
        return value