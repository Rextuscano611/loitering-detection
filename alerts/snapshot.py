import cv2
import os
from datetime import datetime
from config import SNAPSHOTS_DIR, SAVE_SNAPSHOTS


def save_snapshot(frame, track_id, zone_name):
    """
    Save a cropped + full frame snapshot when loitering alert fires.
    Only saves once per alert (caller must control this).
    """
    if not SAVE_SNAPSHOTS:
        return None

    os.makedirs(SNAPSHOTS_DIR, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"loiter_id{track_id}_{zone_name}_{timestamp}.jpg"
    filepath = os.path.join(SNAPSHOTS_DIR, filename)

    cv2.imwrite(filepath, frame)
    print(f"[Snapshot] Saved: {filepath}")
    return filepath