import json
import os
from utils.geometry import point_in_polygon, get_three_feet_points
from config import ZONES_FILE


class ZoneManager:
    def __init__(self):
        self.zones = {}
        self.load_zones()

    def load_zones(self):
        if not os.path.exists(ZONES_FILE):
            print(f"[ZoneManager] WARNING: No zones file found at {ZONES_FILE}")
            print("  Run zone_setup.py first to draw zones.")
            return

        with open(ZONES_FILE, "r") as f:
            raw = json.load(f)

        # Convert lists back to tuples
        self.zones = {
            name: [tuple(pt) for pt in pts]
            for name, pts in raw.items()
        }
        print(f"[ZoneManager] Loaded {len(self.zones)} zone(s): {list(self.zones.keys())}")

    def get_zone_for_person(self, x1, y1, x2, y2):
        """
        Check all zones against person bbox.
        Uses 3-point feet check — 2 of 3 must be inside to confirm.
        Returns zone name if inside any zone, else None.
        """
        feet_points = get_three_feet_points(x1, y1, x2, y2)

        for zone_name, polygon in self.zones.items():
            inside_count = sum(
                1 for pt in feet_points
                if point_in_polygon(pt, polygon)
            )
            if inside_count >= 2:
                return zone_name

        return None