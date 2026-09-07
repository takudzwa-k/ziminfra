"""
Scripted scenarios for demos and testing.

Each scenario is a list of (tick_number, action) steps. `action` is either
None (no change), or a dict describing what to force. Use these to make a
live demo deterministic and interesting instead of waiting for random events
to occur naturally.

Usage (see simulator.py):
    scenario = SCENARIOS["storm_then_blocked_drain"]
    apply_scenario_step(event_state, scenario, tick)
"""

from .events import RoadEventState


SCENARIOS = {
    # Heavy rain starts at tick 10, and by tick 40 the drain is revealed to be
    # blocked (water level stays high even as rain tapers off).
    "storm_then_blocked_drain": [
        (0, None),
        (10, {"type": "heavy_rainfall", "intensity": 0.9}),
        (30, None),  # rain eases off
        (40, {"type": "blocked_drain"}),
        (90, None),  # scenario resolved / drain cleared
    ],

    # A pothole/surface issue that steadily worsens.
    "gradual_road_deterioration": [
        (0, None),
        (5, {"type": "road_deterioration", "rate": 0.015}),
    ],

    # Nothing forced -- pure background simulation, events only emerge
    # naturally from the auto-detection thresholds in events.py.
    "quiet_day": [
        (0, None),
    ],
}


def apply_scenario_step(state: RoadEventState, scenario: list, tick: int) -> None:
    """Apply whichever scripted action is scheduled at this tick, if any."""
    for scheduled_tick, action in scenario:
        if scheduled_tick == tick:
            if action is None:
                state.clear_forced_event()
            else:
                state.force_event(action["type"], **{k: v for k, v in action.items() if k != "type"})