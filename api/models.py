from pydantic import BaseModel
from typing import List, Optional


class AlertEvent(BaseModel):
    camera_id: str
    track_id: int
    zone_id: str
    dwell_seconds: float
    last_bbox: List[int]        # [x1, y1, x2, y2]
    snapshot_url: Optional[str]
    timestamp: str


class SystemStatus(BaseModel):
    camera_id: str
    running: bool
    fps: float
    active_tracks: int
    active_alerts: int