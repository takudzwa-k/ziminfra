"""
Infrastructure event engine.

NOT a sensor -- it's a small rules layer that looks at the current
sensor readings for a road and decides whether an "infrastructure event"
should be reported (blocked drain, heavy rainfall, increasing vibration,
road deterioration). It also supports manually forcing a scenario on, which
is how scenarios/scripted_scenarios.py drives demo runs.

Detected events feed back into the sensors on the *next* tick (see
simulator.py) so sensors can react realistically (e.g. a forced
"blocked_drain" event makes WaterLevelSensor drain much more slowly).
"""

from dataclasses import dataclass, field


# Thresholds used to auto-detect events from raw readings
HEAVY_RAINFALL_MM_H = 40.0
HIGH_WATER_LEVEL_CM = 70.0
HIGH_VIBRATION_G = 1.8
VIBRATION_TREND_WINDOW = 5  # readings to look back for a rising trend


@dataclass
class RoadEventState:
    """Tracks recent history + any manually forced event for one road."""
    road_id: str
    vibration_history: list = field(default_factory=list)
    forced_event: dict | None = None  # set/cleared by scripted scenarios

    def force_event(self, event_type: str, **params):
        self.forced_event = {"type": event_type, **params}

    def clear_forced_event(self):
        self.forced_event = None


def detect_events(state: RoadEventState, readings: dict) -> list[dict]:
    """
    readings: dict with keys rainfall, water_level, vibration, traffic, temperature
    Returns a list of event dicts, e.g.:
        [{"event_type": "heavy_rainfall", "severity": "high", "triggered_by": "rainfall"}]
    """
    events = []

    # 1. Forced/scripted event always takes priority and is always reported
    if state.forced_event:
        events.append({
            "event_type": state.forced_event["type"],
            "severity": "high",
            "triggered_by": "scripted_scenario",
        })

    # 2. Heavy rainfall (auto-detected from raw value)
    if readings["rainfall"] >= HEAVY_RAINFALL_MM_H:
        events.append({
            "event_type": "heavy_rainfall",
            "severity": "high" if readings["rainfall"] > 80 else "medium",
            "triggered_by": "rainfall",
        })

    # 3. Blocked drain (auto-detected: water level high despite low rainfall)
    if readings["water_level"] >= HIGH_WATER_LEVEL_CM and readings["rainfall"] < 5:
        events.append({
            "event_type": "blocked_drain",
            "severity": "high",
            "triggered_by": "water_level",
        })

    # 4. Increasing road vibration (trend-based, needs history)
    state.vibration_history.append(readings["vibration"])
    state.vibration_history = state.vibration_history[-VIBRATION_TREND_WINDOW:]
    if len(state.vibration_history) == VIBRATION_TREND_WINDOW:
        rising = all(
            state.vibration_history[i] <= state.vibration_history[i + 1] + 0.05
            for i in range(len(state.vibration_history) - 1)
        )
        if rising and state.vibration_history[-1] >= HIGH_VIBRATION_G:
            events.append({
                "event_type": "increasing_road_vibration",
                "severity": "medium",
                "triggered_by": "vibration",
            })

    # 5. Road deterioration (sustained very high vibration)
    if readings["vibration"] >= HIGH_VIBRATION_G * 1.3:
        events.append({
            "event_type": "road_deterioration",
            "severity": "high",
            "triggered_by": "vibration",
        })

    return events