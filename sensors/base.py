"""
Base class for all simulated sensors.

Every sensor keeps a small amount of internal state (its last reading) so that
new readings drift realistically from the previous one instead of jumping to
unrelated random values every tick.
"""

from abc import ABC, abstractmethod


class BaseSensor(ABC):
    sensor_type: str = "base"
    unit: str = ""

    def __init__(self, road_id: str):
        self.road_id = road_id
        self.last_value = self._initial_value()

    @abstractmethod
    def _initial_value(self) -> float:
        """Starting value when the simulation boots up."""
        raise NotImplementedError

    @abstractmethod
    def read(self, event_state: dict | None = None) -> float:
        """
        Produce the next simulated reading.

        event_state: optional dict describing an active infrastructure event
        (e.g. {"type": "heavy_rainfall", "intensity": 0.8}) so sensors can
        react to scenarios injected by scenarios/events.py.
        """
        raise NotImplementedError

    def to_dict(self, value: float) -> dict:
        return {
            "sensor_type": self.sensor_type,
            "value": round(value, 2),
            "unit": self.unit,
        }