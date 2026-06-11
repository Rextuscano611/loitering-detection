from alerts.snapshot import save_snapshot


class AlertManager:
    def __init__(self):
        # Track which IDs have already had snapshot saved
        # so we don't spam snapshots every frame
        self.snapshot_taken = set()
        print("[AlertManager] Initialized.")

    def handle_alert(self, frame, track_id, zone_name, elapsed):
        """
        Called every frame a person is in loitering state.
        Saves snapshot only on first alert trigger per ID.
        """
        if track_id not in self.snapshot_taken:
            save_snapshot(frame, track_id, zone_name)
            self.snapshot_taken.add(track_id)
            print(f"[ALERT] Loitering detected! ID:{track_id} | Zone:{zone_name} | Duration:{int(elapsed)}s")

    def reset_id(self, track_id):
        """Call this when a track ID leaves zone and timer resets."""
        self.snapshot_taken.discard(track_id)