import supervision as sv
import numpy as np


class Tracker:
    def __init__(self):
        self.tracker = sv.ByteTrack()
        print("[Tracker] ByteTrack initialized.")

    def update(self, detections, frame):
        """
        Feed detections into ByteTrack.
        Returns list of (x1, y1, x2, y2, track_id)
        """
        if not detections:
            return []

        # Convert to supervision Detections format
        xyxy = np.array([[d[0], d[1], d[2], d[3]] for d in detections], dtype=np.float32)
        conf = np.array([d[4] for d in detections], dtype=np.float32)
        class_id = np.zeros(len(detections), dtype=int)

        sv_dets = sv.Detections(
            xyxy=xyxy,
            confidence=conf,
            class_id=class_id
        )

        tracked = self.tracker.update_with_detections(sv_dets)

        results = []
        for i in range(len(tracked)):
            x1, y1, x2, y2 = map(int, tracked.xyxy[i])
            tid = int(tracked.tracker_id[i])
            results.append((x1, y1, x2, y2, tid))

        return results