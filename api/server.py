from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from typing import List
import threading
from api.models import AlertEvent, SystemStatus
from config import SNAPSHOTS_DIR
import os

app = FastAPI(title="Loitering Detection API")

# --- Shared state (written by detection loop, read by API) ---
_lock = threading.Lock()

_recent_alerts: List[dict] = []       # last 50 alerts
_live_alerts: dict = {}               # { track_id: alert_dict } currently active
_system_status: dict = {
    "camera_id": "cam_01",
    "running": False,
    "fps": 0.0,
    "active_tracks": 0,
    "active_alerts": 0
}

# Serve snapshots as static files
if os.path.exists(SNAPSHOTS_DIR):
    app.mount("/snapshots", StaticFiles(directory=SNAPSHOTS_DIR), name="snapshots")


# --- Functions called by detection loop ---

def push_alert(camera_id, track_id, zone_id, dwell_seconds, last_bbox, snapshot_path=None, timestamp=""):
    """Called from main.py when loitering alert fires."""
    host = "http://localhost:8000"
    snap_url = None
    if snapshot_path:
        filename = os.path.basename(snapshot_path)
        snap_url = f"{host}/snapshots/{filename}"

    alert = {
        "camera_id": camera_id,
        "track_id": track_id,
        "zone_id": zone_id,
        "dwell_seconds": round(dwell_seconds, 2),
        "last_bbox": last_bbox,
        "snapshot_url": snap_url,
        "timestamp": timestamp
    }

    with _lock:
        _live_alerts[track_id] = alert
        _recent_alerts.insert(0, alert)
        if len(_recent_alerts) > 50:
            _recent_alerts.pop()


def clear_alert(track_id):
    """Called from main.py when person leaves zone."""
    with _lock:
        _live_alerts.pop(track_id, None)


def update_status(camera_id, running, fps, active_tracks, active_alerts):
    """Called from main.py every second to update status."""
    with _lock:
        _system_status.update({
            "camera_id": camera_id,
            "running": running,
            "fps": fps,
            "active_tracks": active_tracks,
            "active_alerts": active_alerts
        })


# --- API Endpoints ---

@app.get("/status", response_model=SystemStatus)
def get_status():
    with _lock:
        return _system_status.copy()


@app.get("/alerts", response_model=List[AlertEvent])
def get_recent_alerts():
    """Returns last 50 loitering alerts."""
    with _lock:
        return _recent_alerts.copy()


@app.get("/alerts/live", response_model=List[AlertEvent])
def get_live_alerts():
    """Returns currently active loitering alerts."""
    with _lock:
        return list(_live_alerts.values())


@app.get("/")
def root():
    return {"message": "Loitering Detection API running", "docs": "/docs"}