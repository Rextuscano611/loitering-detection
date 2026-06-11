import cv2
import numpy as np


# --- Colors (BGR) ---
COLOR_NORMAL = (0, 255, 0)        # green — person detected, not loitering
COLOR_WARNING = (0, 165, 255)     # orange — approaching threshold
COLOR_ALERT = (0, 0, 255)         # red — loitering alert
COLOR_ZONE = (255, 255, 0)        # cyan — zone outline
COLOR_ZONE_FILL = (255, 255, 0)   # zone fill (low opacity)
COLOR_TEXT = (255, 255, 255)      # white text


def draw_zone(frame, polygon, label="Zone"):
    """Draw a semi-transparent filled zone polygon with border."""
    pts = np.array(polygon, dtype=np.int32)

    # Semi-transparent fill
    overlay = frame.copy()
    cv2.fillPoly(overlay, [pts], (255, 255, 0))
    cv2.addWeighted(overlay, 0.15, frame, 0.85, 0, frame)

    # Border
    cv2.polylines(frame, [pts], isClosed=True, color=COLOR_ZONE, thickness=2)

    # Label at top-left of zone
    cx = int(np.mean([p[0] for p in polygon]))
    cy = int(min([p[1] for p in polygon])) - 8
    cv2.putText(frame, label, (cx - 20, cy),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, COLOR_ZONE, 2)


def draw_tracked_person(frame, x1, y1, x2, y2, track_id, elapsed=0, threshold=30, alerted=False):
    """
    Draw bounding box with color based on loiter state.
    Shows a timer progress bar below the bbox.
    """
    # Pick color
    if alerted:
        color = COLOR_ALERT
    elif elapsed > threshold * 0.6:
        color = COLOR_WARNING
    else:
        color = COLOR_NORMAL

    # Bounding box
    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

    # Label
    label = f"ID:{track_id}"
    if elapsed > 0:
        label += f"  {int(elapsed)}s"
    if alerted:
        label += "  LOITERING"

    cv2.putText(frame, label, (x1, y1 - 8),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 2)

    # Timer bar (only when inside zone)
    if elapsed > 0:
        bar_w = x2 - x1
        filled = int(min(elapsed / threshold, 1.0) * bar_w)
        cv2.rectangle(frame, (x1, y2 + 4), (x2, y2 + 10), (50, 50, 50), -1)
        cv2.rectangle(frame, (x1, y2 + 4), (x1 + filled, y2 + 10), color, -1)


def draw_feet_point(frame, fx, fy):
    """Debug helper — draws the feet point used for zone check."""
    cv2.circle(frame, (fx, fy), 4, (0, 255, 255), -1)


def draw_alert_banner(frame, count):
    """Top banner when loitering is detected."""
    if count == 0:
        return
    h, w = frame.shape[:2]
    cv2.rectangle(frame, (0, 0), (w, 40), (0, 0, 200), -1)
    text = f"  LOITERING ALERT — {count} person(s) detected"
    cv2.putText(frame, text, (10, 28),
                cv2.FONT_HERSHEY_SIMPLEX, 0.75, COLOR_TEXT, 2)


def draw_fps(frame, fps):
    h, w = frame.shape[:2]
    cv2.putText(frame, f"FPS: {fps:.1f}", (w - 120, h - 15),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (180, 180, 180), 1)