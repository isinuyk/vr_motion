import argparse
import csv
import cv2
import tkinter as tk
from tkinter import filedialog

import config
from swing_analyzer import SwingAnalyzer
from loader import load_folder
from stats_overlay import draw_stats


def parse_args():
    parser = argparse.ArgumentParser(description="Run VR motion analysis.")
    parser.add_argument(
        "--profile",
        choices=["realtime", "scientific"],
        default=config.FILTER_PROFILE,
        help="Filtering profile. scientific=best offline quality, realtime=leaner/closer",
    )
    parser.add_argument(
        "--folder",
        default=None,
        help="Optional folder containing mediapipe_data_full.json and video_processed.mp4",
    )
    return parser.parse_args()


args = parse_args()
config.set_filter_profile(args.profile)

# ---- folder picker ----
if args.folder:
    folder = args.folder
else:
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


def build_analyzer_with_profile(profile_name):
    """Apply profile and create a fresh analyzer. No module reload needed — swing_analyzer reads config at runtime."""
    config.set_filter_profile(profile_name)
    return SwingAnalyzer(data, fps, (display_w, display_h))


PROFILE_TRAJECTORY_STYLE = {
    "realtime": {
        "raw_color": (0, 64, 255),
        "raw_thickness": 1,
        "smooth_color": (0, 255, 255),
        "smooth_thickness": 2,
    },
    "scientific": {
        "raw_color": (0, 0, 255),
        "raw_thickness": 1,
        "smooth_color": (0, 255, 0),
        "smooth_thickness": 3,
    },
}


def restart_run(profile_name):
    analyzer_local = build_analyzer_with_profile(profile_name)
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    state = {
        "idx": 0,
        "paused": False,
        "prev_msec": None,
        "t0_msec": None,
        "dt": (1.0 / fps) if fps and fps > 0 else (1.0 / 30.0),
    }
    return analyzer_local, state


analyzer, run_state = restart_run(config.FILTER_PROFILE)

try:
    while True:
        if not run_state["paused"]:
            ret, frame_img = cap.read()
            if not ret or run_state["idx"] >= len(data):
                break
            frame = data[run_state["idx"]]

            pos_msec = cap.get(cv2.CAP_PROP_POS_MSEC)
            if run_state["t0_msec"] is None:
                run_state["t0_msec"] = pos_msec

            if run_state["prev_msec"] is None:
                run_state["dt"] = (1.0 / fps) if fps and fps > 0 else (1.0 / 30.0)
            else:
                run_state["dt"] = (pos_msec - run_state["prev_msec"]) / 1000.0
                if run_state["dt"] <= 0 or run_state["dt"] > 1.0:
                    run_state["dt"] = (1.0 / fps) if fps and fps > 0 else (1.0 / 30.0)

            t = (pos_msec - run_state["t0_msec"]) / 1000.0

            frame_resized = cv2.resize(frame_img, (display_w, display_h))
            analyzer.process_frame(run_state["idx"], frame_resized, frame, dt=run_state["dt"], t=t)
            style = PROFILE_TRAJECTORY_STYLE.get(
                config.FILTER_PROFILE, PROFILE_TRAJECTORY_STYLE["scientific"]
            )
            analyzer.draw_trajectory(
                frame_resized,
                raw_color=style["raw_color"],
                raw_thickness=style["raw_thickness"],
                smooth_color=style["smooth_color"],
                smooth_thickness=style["smooth_thickness"],
            )

            # ---- build stats dict for overlay ----
            summ = analyzer.summary()
            stats = {
                "frame": run_state["idx"],
                "speed": analyzer.speeds[-1],
                "max_speed": summ.get("max_speed", 0),
                "max_ang_vel": summ.get("max_ang_vel", 0),
                "max_accel": summ.get("max_accel", 0),
                "swing_time": analyzer.times[run_state["idx"]],
                "video_fps": fps,
                "tempo": summ.get("swing_tempo"),
                "smoothness": summ.get("smoothness_index"),
                "path_efficiency": summ.get("path_efficiency"),
                "curvature_rms": summ.get("curvature_rms"),
                "profile": config.FILTER_PROFILE,
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
            run_state["idx"] += 1
            run_state["prev_msec"] = pos_msec

        wait_ms = int(max(1, run_state["dt"] * 1000.0)) if not run_state["paused"] else 30
        key = cv2.waitKey(wait_ms) & 0xFF
        if key == 27:
            break
        if key == 32:
            run_state["paused"] = not run_state["paused"]
        if key in (ord("r"), ord("R")):
            analyzer, run_state = restart_run("realtime")
        if key in (ord("s"), ord("S")):
            analyzer, run_state = restart_run("scientific")
finally:
    cap.release()
    cv2.destroyAllWindows()

# ---- finalize & export ----
rows = analyzer.finalize()
header = [
    "time", "stick_speed", "angular_velocity", "acceleration",
    "angular_acceleration", "energy_proxy", "jerk", "time_norm",
    "tip_x_m", "tip_y_m", "tip_x_m_raw", "tip_y_m_raw", "scale_m",
    "hip_angle_deg", "shoulder_angle_deg", "x_factor_deg",
    "wrist_angle_deg", "arc_radius_px", "curvature_1_m",
    "path_efficiency", "phase",
]

with open("swing_analysis.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(header)
    writer.writerows(rows)
