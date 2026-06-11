"""
zone_setup.py — Run this ONCE per camera to draw and save zones.

Controls:
  Left click       → add point to current zone
  Right click      → undo last point
  ENTER            → save current zone (you can draw multiple zones)
  R                → reset current zone (start over)
  Q                → quit and save all zones to zones/zones.json
"""

import cv2
import json
import os
import numpy as np
from config import SOURCE, ZONES_FILE

# --- State ---
current_polygon = []
saved_zones = {}
zone_counter = 1
frame_copy = None


def mouse_callback(event, x, y, flags, param):
    global current_polygon, frame_copy

    if event == cv2.EVENT_LBUTTONDOWN:
        current_polygon.append((x, y))
        print(f"  Point added: ({x}, {y})")

    elif event == cv2.EVENT_RBUTTONDOWN:
        if current_polygon:
            removed = current_polygon.pop()
            print(f"  Point removed: {removed}")


def draw_current_state(frame):
    """Draw saved zones + current in-progress polygon on frame."""
    display = frame.copy()

    # Draw saved zones
    for name, pts in saved_zones.items():
        poly = np.array(pts, dtype=np.int32)
        overlay = display.copy()
        cv2.fillPoly(overlay, [poly], (255, 255, 0))
        cv2.addWeighted(overlay, 0.15, display, 0.85, 0, display)
        cv2.polylines(display, [poly], True, (255, 255, 0), 2)
        cx = int(np.mean([p[0] for p in pts]))
        cy = int(min([p[1] for p in pts])) - 8
        cv2.putText(display, name, (cx - 20, cy),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

    # Draw current in-progress polygon
    for i, pt in enumerate(current_polygon):
        cv2.circle(display, pt, 5, (0, 255, 0), -1)
        if i > 0:
            cv2.line(display, current_polygon[i - 1], pt, (0, 255, 0), 2)
    if len(current_polygon) > 2:
        cv2.line(display, current_polygon[-1], current_polygon[0], (0, 255, 0), 1)

    # Instructions
    instructions = [
        "Left Click: Add point",
        "Right Click: Undo point",
        "ENTER: Save zone",
        "R: Reset current zone",
        "Q: Quit & save all",
    ]
    for i, text in enumerate(instructions):
        cv2.putText(display, text, (10, 20 + i * 22),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200, 200, 200), 1)

    return display


def save_zones():
    os.makedirs(os.path.dirname(ZONES_FILE), exist_ok=True)
    with open(ZONES_FILE, "w") as f:
        json.dump(saved_zones, f, indent=4)
    print(f"\n Zones saved to {ZONES_FILE}")
    print(json.dumps(saved_zones, indent=4))


def main():
    global current_polygon, zone_counter, frame_copy

    cap = cv2.VideoCapture(SOURCE)
    if not cap.isOpened():
        print(f"ERROR: Cannot open source: {SOURCE}")
        return

    print("\n=== ZONE SETUP ===")
    print("Draw zones on the frame. Press Q when done.\n")

    cv2.namedWindow("Zone Setup")
    cv2.setMouseCallback("Zone Setup", mouse_callback)

    ret, frame = cap.read()
    if not ret:
        print("ERROR: Cannot read frame.")
        return

    frame_copy = frame.copy()   # static background frame

    while True:
        display = draw_current_state(frame_copy)
        cv2.imshow("Zone Setup", display)

        key = cv2.waitKey(1) & 0xFF

        if key == 13:   # ENTER — save current zone
            if len(current_polygon) >= 3:
                zone_name = f"zone_{zone_counter}"
                saved_zones[zone_name] = current_polygon.copy()
                print(f"\n Zone '{zone_name}' saved with {len(current_polygon)} points.")
                zone_counter += 1
                current_polygon = []
            else:
                print("  Need at least 3 points to save a zone.")

        elif key == ord('r'):   # R — reset current zone
            current_polygon = []
            print("  Current zone reset.")

        elif key == ord('q'):   # Q — quit and save
            if saved_zones:
                save_zones()
            else:
                print("  No zones saved.")
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()