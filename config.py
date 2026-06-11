from dotenv import load_dotenv
import os

load_dotenv()

# --- Camera ---
SOURCE = os.getenv("SOURCE", "0")
SOURCE = int(SOURCE) if SOURCE.isdigit() else SOURCE

# --- Model ---
MODEL_PATH = os.getenv("MODEL_PATH", "models/yolov8n.pt")
CONF_THRESHOLD = float(os.getenv("CONF_THRESHOLD", "0.4"))

# --- Loitering ---
LOITER_THRESHOLD = int(os.getenv("LOITER_THRESHOLD", "30"))
GRACE_PERIOD = int(os.getenv("GRACE_PERIOD", "5"))

# --- Alerts ---
SAVE_SNAPSHOTS = os.getenv("SAVE_SNAPSHOTS", "true").lower() == "true"
SHOW_DISPLAY = os.getenv("SHOW_DISPLAY", "true").lower() == "true"

# --- Paths ---
ZONES_FILE = "zones/zones.json"
SNAPSHOTS_DIR = "snapshots"
DB_PATH = "logs/loiter_events.db"