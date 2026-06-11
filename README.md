# Loitering Detection System

Real-time loitering detection using YOLOv8 + ByteTrack.

## Features
- Zone-based loitering detection
- ByteTrack ID tracking with grace period and ID inheritance
- 3-point feet-based zone entry detection
- SQLite event logging
- Snapshot saving on alert

## Setup
pip install -r requirements.txt

## Usage
1. Draw zones: python zone_setup.py
2. Run system: python main.py

## Config
Copy .env.example to .env and edit values.
