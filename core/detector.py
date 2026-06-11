from ultralytics import YOLO
from config import MODEL_PATH, CONF_THRESHOLD


class Detector:
    def __init__(self):
        self.model = YOLO(MODEL_PATH)
        self.conf = CONF_THRESHOLD
        print(f"[Detector] Model loaded: {MODEL_PATH}")

    def detect(self, frame):
        """
        Run YOLO on frame, return only 'person' detections.
        Returns list of (x1, y1, x2, y2, confidence)
        """
        results = self.model(frame, conf=self.conf, classes=[0], verbose=False)[0]
        detections = []

        for box in results.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            conf = float(box.conf[0])
            detections.append((x1, y1, x2, y2, conf))

        return detections