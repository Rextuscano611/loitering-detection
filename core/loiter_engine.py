import time
from utils.geometry import iou
from config import LOITER_THRESHOLD, GRACE_PERIOD


class LoiterEngine:
    def __init__(self):
        # { track_id: entry_timestamp }
        self.loiter_timers = {}

        # { track_id: last_seen_in_zone_timestamp } — grace period buffer
        self.grace_buffer = {}

        # { track_id: (x1,y1,x2,y2) } — last known bbox for ID inheritance
        self.last_known_bbox = {}

        # { track_id } — IDs that have already fired an alert
        self.alerted_ids = set()

        print("[LoiterEngine] Initialized.")

    def update(self, track_id, x1, y1, x2, y2, zone_name):
        """
        Call this every frame for every tracked person.
        zone_name: name of zone person is in, or None if outside all zones.
        Returns (elapsed_seconds, is_alerted)
        """
        now = time.time()

        # Store last known bbox for ID inheritance
        self.last_known_bbox[track_id] = (x1, y1, x2, y2)

        if zone_name is not None:
            # Person is inside a zone
            self.grace_buffer[track_id] = now

            if track_id not in self.loiter_timers:
                # Check if we can inherit timer from a recently lost ID
                inherited = self._try_inherit(track_id, (x1, y1, x2, y2))
                if not inherited:
                    self.loiter_timers[track_id] = now

            elapsed = now - self.loiter_timers[track_id]

            if elapsed >= LOITER_THRESHOLD:
                self.alerted_ids.add(track_id)
                return elapsed, True

            return elapsed, False

        else:
            # Person is outside zone — check grace period
            if track_id in self.grace_buffer:
                grace_elapsed = now - self.grace_buffer[track_id]
                if grace_elapsed > GRACE_PERIOD:
                    # Grace expired — reset timer
                    self.loiter_timers.pop(track_id, None)
                    self.grace_buffer.pop(track_id, None)
                    self.alerted_ids.discard(track_id)
                else:
                    # Still in grace period — keep timer running
                    if track_id in self.loiter_timers:
                        elapsed = now - self.loiter_timers[track_id]
                        return elapsed, track_id in self.alerted_ids

            return 0, False

    def _try_inherit(self, new_tid, new_bbox):
        """
        Check if new_tid's bbox overlaps a recently lost track.
        If IoU > 0.5, inherit that track's timer.
        """
        for old_tid, old_bbox in list(self.last_known_bbox.items()):
            if old_tid == new_tid:
                continue
            if old_tid in self.loiter_timers:
                if iou(new_bbox, old_bbox) > 0.5:
                    print(f"[LoiterEngine] ID {new_tid} inherited timer from ID {old_tid}")
                    self.loiter_timers[new_tid] = self.loiter_timers.pop(old_tid)
                    self.grace_buffer.pop(old_tid, None)
                    if old_tid in self.alerted_ids:
                        self.alerted_ids.discard(old_tid)
                        self.alerted_ids.add(new_tid)
                    return True
        return False

    def cleanup_lost_tracks(self, active_ids):
        """
        Remove data for track IDs no longer seen.
        Call once per frame after processing all tracks.
        """
        now = time.time()
        all_known = set(self.last_known_bbox.keys())
        lost = all_known - set(active_ids)

        for tid in lost:
            # Only clean up if grace period has fully expired
            if tid in self.grace_buffer:
                if now - self.grace_buffer[tid] > GRACE_PERIOD + 2:
                    self.loiter_timers.pop(tid, None)
                    self.grace_buffer.pop(tid, None)
                    self.last_known_bbox.pop(tid, None)
                    self.alerted_ids.discard(tid)
            else:
                self.last_known_bbox.pop(tid, None)