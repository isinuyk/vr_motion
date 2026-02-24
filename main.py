import cv2
import tkinter as tk
from tkinter import filedialog
from loader import load_folder
from swing_analyzer import SwingAnalyzer
from stats_overlay import draw_stats
import csv

# ---- folder picker ----
root = tk.Tk()
root.withdraw()
folder = filedialog.askdirectory(title="Select swing folder")
if not folder:
    raise RuntimeError("No folder selected")
data, video_path = load_folder(folder)

# ---- video setup ----
cap = cv2.VideoCapture(video_path)
fps = cap.get(cv2.CAP_PROP_FPS)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

screen_w, screen_h = 1280, 720
scale = min(screen_w / width, screen_h / height)
display_w, display_h = int(width * scale), int(height * scale)

analyzer = SwingAnalyzer(data, fps, (display_w, display_h))

idx = 0
paused = False
prev_msec = None
t0_msec = None
dt = (1.0 / fps) if fps and fps > 0 else (1.0 / 30.0)

while True:
    if not paused:
        ret, frame_img = cap.read()
        if not ret or idx >= len(data):
            break
        frame = data[idx]

        pos_msec = cap.get(cv2.CAP_PROP_POS_MSEC)
        if t0_msec is None:
            t0_msec = pos_msec

        if prev_msec is None:
            dt = (1.0 / fps) if fps and fps > 0 else (1.0 / 30.0)
        else:
            dt = (pos_msec - prev_msec) / 1000.0
            if dt <= 0 or dt > 1.0:
                dt = (1.0 / fps) if fps and fps > 0 else (1.0 / 30.0)

        t = (pos_msec - t0_msec) / 1000.0

        frame_resized = cv2.resize(frame_img, (display_w, display_h))
        analyzer.process_frame(idx, frame_resized, frame, dt=dt, t=t)
        analyzer.draw_trajectory(frame_resized)

        # ---- build stats dict for overlay ----
        summ = analyzer.summary()
        stats = {
            "frame": idx,
            "speed": analyzer.speeds[-1],
            "max_speed": summ.get("max_speed", 0),
            "max_ang_vel": summ.get("max_ang_vel", 0),
            "max_accel": summ.get("max_accel", 0),
            "swing_time": analyzer.times[idx],
            "video_fps": fps,
            "tempo": summ.get("swing_tempo"),
            "smoothness": summ.get("smoothness_index"),
        }

        hip = analyzer.hip_angles[-1]
        sh = analyzer.shoulder_angles[-1]
        xf = analyzer.x_factors[-1]
        wa = analyzer.wrist_angles[-1]
        ar = analyzer.arc_radii[-1]

        if hip is not None:
            stats["hip_angle"] = hip
        if sh is not None:
            stats["shoulder_angle"] = sh
        if xf is not None:
            stats["x_factor"] = xf
        if wa is not None:
            stats["wrist_angle"] = wa
        if ar is not None and analyzer.scale_m:
            stats["arc_radius"] = ar * analyzer.scale_m

        draw_stats(frame_resized, stats)
        cv2.imshow("VR Motion Analysis", frame_resized)
        idx += 1
        prev_msec = pos_msec

    wait_ms = int(max(1, dt * 1000.0)) if not paused else 30
    key = cv2.waitKey(wait_ms) & 0xFF
    if key == 27:
        break
    if key == 32:
        paused = not paused

# ---- finalize & export ----
rows = analyzer.finalize()
header = [
    "time", "stick_speed", "angular_velocity", "acceleration",
    "angular_acceleration", "energy_proxy", "jerk", "time_norm",
    "tip_x_m", "tip_y_m", "tip_x_m_raw", "tip_y_m_raw",
    "hip_angle_deg", "shoulder_angle_deg", "x_factor_deg",
    "wrist_angle_deg", "arc_radius_px",
]

with open("swing_analysis.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(header)
    writer.writerows(rows)

cap.release()
cv2.destroyAllWindows()
