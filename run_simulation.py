"""
run_simulation.py

The main entry point for the Road IoT Simulator. Runs all roads defined in
config.ROADS in an infinite loop, redrawing a live color-coded table in the
terminal every tick using the 'rich' library.

Run it with:
    python3 run_simulation.py

Stop it with:
    Ctrl+C
"""

import time
from datetime import datetime, timezone

from rich.console import Console
from rich.live import Live
from rich.table import Table

from config import ROADS, PUBLISH_INTERVAL_SECONDS
from simulator import RoadSimulator


SEVERITY_COLOR = {
    "low": "yellow",
    "medium": "orange3",
    "high": "bold red",
}


def build_table(latest_readings: dict) -> Table:
    table = Table(title="Road IoT Simulator — Live Sensor Feed", expand=True)

    table.add_column("Road", style="cyan", no_wrap=True)
    table.add_column("Rainfall (mm/h)", justify="right")
    table.add_column("Water Lvl (cm)", justify="right")
    table.add_column("Vibration (g)", justify="right")
    table.add_column("Traffic (v/h)", justify="right")
    table.add_column("Temp (°C)", justify="right")
    table.add_column("Timestamp", style="dim")
    table.add_column("Events")

    for road_id, payload in latest_readings.items():
        events = payload["events"]
        if events:
            # Show the highest-severity event, colored accordingly
            top_event = max(events, key=lambda e: {"low": 0, "medium": 1, "high": 2}[e["severity"]])
            color = SEVERITY_COLOR[top_event["severity"]]
            events_str = f"[{color}]{top_event['event_type']} ({top_event['severity']})[/{color}]"
            if len(events) > 1:
                events_str += f" [dim]+{len(events) - 1} more[/dim]"
        else:
            events_str = "[green]—[/green]"

        table.add_row(
            payload["road_id"],
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
    console = Console()
    simulators = {road["road_id"]: RoadSimulator(road["road_id"]) for road in ROADS}
    latest_readings = {}

    with Live(build_table(latest_readings), console=console, refresh_per_second=4) as live:
        try:
            while True:
                now = datetime.now(timezone.utc)
                for road_id, sim in simulators.items():
                    latest_readings[road_id] = sim.tick(now=now)

                live.update(build_table(latest_readings))
                time.sleep(PUBLISH_INTERVAL_SECONDS)
        except KeyboardInterrupt:
            console.print("\n[bold yellow]Simulation stopped.[/bold yellow]")


if __name__ == "__main__":
    main()