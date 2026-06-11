import cv2
import time
from config import SOURCE, SHOW_DISPLAY
from core.detector import Detector
from core.tracker import Tracker
from core.zone_manager import ZoneManager
from core.loiter_engine import LoiterEngine
from alerts.alert_manager import AlertManager
from alerts.snapshot import save_snapshot
from database.db_handler import DBHandler
from utils.drawing import (
    draw_zone, draw_tracked_person,
    draw_feet_point, draw_alert_banner, draw_fps
)
from utils.geometry import get_three_feet_points


def main():
    print("\n=== Loitering Detection System Starting ===\n")

    # --- Init all modules ---
    detector     = Detector()
    tracker      = Tracker()
    zone_manager = ZoneManager()
    loiter_eng   = LoiterEngine()
    alert_mgr    = AlertManager()
    db           = DBHandler()

    if not zone_manager.zones:
        print("ERROR: No zones loaded. Run zone_setup.py first.")
        return

    # --- Open video source ---
    cap = cv2.VideoCapture(SOURCE)
    if not cap.isOpened():
        print(f"ERROR: Cannot open source: {SOURCE}")
        return

    print("\n[Main] Pipeline running. Press Q to quit.\n")

    # FPS tracking
    fps = 0
    frame_count = 0
    fps_timer = time.time()

    # DB log throttle — log to DB once per alert, not every frame
    db_logged_ids = set()

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[Main] Stream ended or frame read failed.")
            break

        # --- Detection ---
        detections = detector.detect(frame)

        # --- Tracking ---
        tracks = tracker.update(detections, frame)

        active_ids = [t[4] for t in tracks]
        alert_count = 0

        # --- Draw zones ---
        for zone_name, polygon in zone_manager.zones.items():
            draw_zone(frame, polygon, label=zone_name)

        # --- Per-track processing ---
        for (x1, y1, x2, y2, tid) in tracks:

            # Zone check
            zone_name = zone_manager.get_zone_for_person(x1, y1, x2, y2)

            # Loiter engine update
            elapsed, is_alerted = loiter_eng.update(tid, x1, y1, x2, y2, zone_name)

            # Draw person
            draw_tracked_person(frame, x1, y1, x2, y2, tid,
                                elapsed=elapsed,
                                threshold=30,
                                alerted=is_alerted)

            # Debug feet points (comment out if not needed)
            for pt in get_three_feet_points(x1, y1, x2, y2):
                draw_feet_point(frame, pt[0], pt[1])

            # Alert handling
            if is_alerted:
                alert_count += 1
                alert_mgr.handle_alert(frame, tid, zone_name, elapsed)

                # Log to DB once per alert ID
                if tid not in db_logged_ids:
                    db.log_event(tid, zone_name, elapsed)
                    db_logged_ids.add(tid)

            else:
                # If person left zone and timer reset, allow re-logging
                if tid in db_logged_ids and elapsed == 0:
                    db_logged_ids.discard(tid)
                    alert_mgr.reset_id(tid)

        # --- Cleanup lost tracks ---
        loiter_eng.cleanup_lost_tracks(active_ids)

        # --- UI overlays ---
        draw_alert_banner(frame, alert_count)

        # FPS calc
        frame_count += 1
        if time.time() - fps_timer >= 1.0:
            fps = frame_count
            frame_count = 0
            fps_timer = time.time()
        draw_fps(frame, fps)

        # --- Display ---
        if SHOW_DISPLAY:
            cv2.imshow("Loitering Detection", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("[Main] Quit by user.")
                break

    cap.release()
    db.close()
    cv2.destroyAllWindows()
    print("\n[Main] System stopped cleanly.")


if __name__ == "__main__":
    main()