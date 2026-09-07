"""
demo_scenario.py

Runs a single road through a SCRIPTED event scenario (e.g. heavy rainfall
that later reveals a blocked drain) and shows it live on a dashboard, tick
by tick, using the same rich-based table as run_simulation.py.

This is useful for demos/presentations: instead of waiting for random events
to occur naturally, you get a repeatable, deterministic storyline.

Run it with:
    python3 demo_scenario.py

Optionally choose a different scenario or road:
    python3 demo_scenario.py --scenario gradual_road_deterioration --road R002

Stop early anytime with Ctrl+C.
"""

import argparse
import time
from datetime import datetime, timezone

from rich.console import Console
from rich.live import Live
from rich.table import Table

from simulator import RoadSimulator
from scenarios.scripted_scenarios import SCENARIOS, apply_scenario_step


SEVERITY_COLOR = {
    "low": "yellow",
    "medium": "orange3",
    "high": "bold red",
}

TICK_INTERVAL_SECONDS = 1.0  # faster than the main dashboard, for demo pacing
TOTAL_TICKS = 100


def build_table(road_id: str, tick: int, scenario_name: str, payload: dict) -> Table:
    table = Table(
        title=f"Scenario Demo — '{scenario_name}' on {road_id}  (tick {tick})",
        expand=True,
    )
    table.add_column("Rainfall (mm/h)", justify="right")
    table.add_column("Water Lvl (cm)", justify="right")
    table.add_column("Vibration (g)", justify="right")
    table.add_column("Traffic (v/h)", justify="right")
    table.add_column("Temp (°C)", justify="right")
    table.add_column("Timestamp", style="dim")
    table.add_column("Events")

    events = payload["events"]
    if events:
        top_event = max(events, key=lambda e: {"low": 0, "medium": 1, "high": 2}[e["severity"]])
        color = SEVERITY_COLOR[top_event["severity"]]
        events_str = f"[{color}]{top_event['event_type']} ({top_event['severity']})[/{color}]"
        if len(events) > 1:
            events_str += f" [dim]+{len(events) - 1} more[/dim]"
    else:
        events_str = "[green]—[/green]"

    table.add_row(
        f"{payload['rainfall']}",
        f"{payload['water_level']}",
        f"{payload['vibration']}",
        f"{payload['traffic']}",
        f"{payload['temperature']}",
        payload["timestamp"],
        events_str,
    )
    return table


def main():
    parser = argparse.ArgumentParser(description="Run a scripted infrastructure event scenario live.")
    parser.add_argument(
        "--scenario",
        default="storm_then_blocked_drain",
        choices=list(SCENARIOS.keys()),
        help="Which scripted scenario to run.",
    )
    parser.add_argument("--road", default="R001", help="Road ID to run the scenario on.")
    args = parser.parse_args()

    console = Console()
    sim = RoadSimulator(args.road)
    scenario = SCENARIOS[args.scenario]

    console.print(
        f"[bold cyan]Starting scenario '[white]{args.scenario}[/white]' on road "
        f"[white]{args.road}[/white]...[/bold cyan]\n"
    )

    payload = sim.tick()
    with Live(build_table(args.road, 0, args.scenario, payload), console=console, refresh_per_second=4) as live:
        try:
            for tick in range(TOTAL_TICKS):
                apply_scenario_step(sim.event_state, scenario, tick)
                now = datetime.now(timezone.utc)
                payload = sim.tick(now=now)
                live.update(build_table(args.road, tick, args.scenario, payload))
                time.sleep(TICK_INTERVAL_SECONDS)
        except KeyboardInterrupt:
            pass

    console.print("\n[bold yellow]Scenario demo finished.[/bold yellow]")


if __name__ == "__main__":
    main()
