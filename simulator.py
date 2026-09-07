"""
Core simulator: for each road, wraps all 5 sensors + the event engine and
produces ONE combined payload per tick, matching the format:

    {
      "road_id": "R001",
      "vibration": 0.73,
      "traffic": 1240,
      "temperature": 31.2,
      "rainfall": 0.0,
      "water_level": 3.2,
      "timestamp": "2026-09-06T10:32:14",
      "events": [...]
    }
"""

from datetime import datetime, timezone

from sensors import (
    RainfallSensor,
    WaterLevelSensor,
    VibrationSensor,
    TrafficSensor,
    TemperatureSensor,
)
from scenarios.events import RoadEventState, detect_events


class RoadSimulator:
    """Owns all sensors for a single road and produces combined readings."""

    def __init__(self, road_id: str):
        self.road_id = road_id
        self.rainfall = RainfallSensor(road_id)
        self.water_level = WaterLevelSensor(road_id)
        self.vibration = VibrationSensor(road_id)
        self.traffic = TrafficSensor(road_id)
        self.temperature = TemperatureSensor(road_id)
        self.event_state = RoadEventState(road_id=road_id)

    def tick(self, now: datetime | None = None) -> dict:
        now = now or datetime.now(timezone.utc)
        forced = self.event_state.forced_event

        rainfall_val = self.rainfall.read(event_state=forced)
        water_level_val = self.water_level.read(event_state=forced, rainfall_mm_h=rainfall_val)
        traffic_val = self.traffic.read(now=now)
        vibration_val = self.vibration.read(event_state=forced, traffic_vph=traffic_val)
        temperature_val = self.temperature.read(now=now)

        readings = {
            "rainfall": rainfall_val,
            "water_level": water_level_val,
            "vibration": vibration_val,
            "traffic": traffic_val,
            "temperature": temperature_val,
        }

        events = detect_events(self.event_state, readings)

        payload = {
            "road_id": self.road_id,
            "vibration": round(vibration_val, 2),
            "traffic": int(traffic_val),
            "temperature": round(temperature_val, 1),
            "rainfall": round(rainfall_val, 1),
            "water_level": round(water_level_val, 1),
            "timestamp": now.strftime("%Y-%m-%dT%H:%M:%S"),
            "events": events,
        }
        return payload