import cv2
import tkinter as tk
from tkinter import filedialog
from loader import load_folder
from swing_analyzer import SwingAnalyzer
from stats_overlay import draw_stats
import csv

# Window pick folder
root=tk.Tk(); root.withdraw()
folder=filedialog.askdirectory(title="Select swing folder")
if not folder: raise RuntimeError("No folder selected")
data, video_path = load_folder(folder)

# Video setup
cap=cv2.VideoCapture(video_path)
fps=cap.get(cv2.CAP_PROP_FPS)
width=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Fixed window size
screen_w, screen_h = 1280, 720
scale = min(screen_w/width, screen_h/height)
display_w, display_h = int(width*scale), int(height*scale)

analyzer=SwingAnalyzer(data, fps, (display_w, display_h))

idx=0
paused=False

while True:
    if not paused:
        ret, frame_img=cap.read()
        if not ret or idx>=len(data):
            break
        frame=data[idx]
        frame_resized=cv2.resize(frame_img,(display_w, display_h))
        analyzer.process_frame(idx, frame_resized, frame)

        # Draw trajectories
        analyzer.draw_trajectory(frame_resized)

        # Draw stats
        vmax=max(analyzer.speeds) if analyzer.speeds else 0
        wmax=max(analyzer.ang_vels) if analyzer.ang_vels else 0
        amax=max(analyzer.accels) if analyzer.accels else 0
        draw_stats(frame_resized, idx, analyzer.speeds[-1], vmax, wmax, amax,
                   analyzer.times[idx])

        cv2.imshow("VR Motion Analysis", frame_resized)
        idx+=1

    key=cv2.waitKey(int(1000/fps)) & 0xFF
    if key==27:  # ESC
        break
    if key==32:  # SPACE
        paused=not paused

rows=analyzer.finalize()
# Export CSV
header=["time","stick_speed","angular_velocity","acceleration",
        "angular_acceleration","energy_proxy","jerk","time_norm",
        "tip_x_m","tip_y_m","tip_x_m_raw","tip_y_m_raw"]

with open("swing_analysis.csv","w",newline="") as f:
    writer=csv.writer(f)
    writer.writerow(header)
    writer.writerows(rows)

cap.release()
cv2.destroyAllWindows()
