import cv2
from config import COLOR_TEXT


def draw_stats(img, stats):
    """Draw live metrics on the video frame.

    *stats* is a dict with keys corresponding to the metrics to display.
    Missing keys are silently skipped.
    """
    lines = []

    def _add(label, key, fmt=".2f", suffix=""):
        val = stats.get(key)
        if val is not None:
            lines.append(f"{label}: {val:{fmt}}{suffix}")

    _add("Frame", "frame", "d")
    _add("Speed", "speed", ".2f", " m/s")
    _add("Max speed", "max_speed", ".2f", " m/s")
    _add("Max ang vel", "max_ang_vel", ".2f", " rad/s")
    _add("Max accel", "max_accel", ".1f", " m/s^2")
    _add("Swing time", "swing_time", ".3f", " s")
    _add("Hip angle", "hip_angle", ".1f", " deg")
    _add("Shoulder angle", "shoulder_angle", ".1f", " deg")
    _add("X-factor", "x_factor", ".1f", " deg")
    _add("Wrist angle", "wrist_angle", ".1f", " deg")
    _add("Arc radius", "arc_radius", ".2f", " m")
    _add("Tempo", "tempo", ".2f")
    _add("Smoothness", "smoothness", ".2f")
    _add("Path eff.", "path_efficiency", ".3f")
    _add("Curvature RMS", "curvature_rms", ".3f", " 1/m")
    _add("Video FPS", "video_fps", ".1f")
    if stats.get("profile"):
        lines.append(f"Profile: {stats['profile']}")

    lines.append("SPACE pause | R realtime | S scientific | ESC exit")

    y = 20
    font = cv2.FONT_HERSHEY_SIMPLEX
    scale = 0.45
    thickness = 1
    for line in lines:
        cv2.putText(img, line, (8, y), font, scale, (0, 0, 0), thickness + 2)
        cv2.putText(img, line, (8, y), font, scale, COLOR_TEXT, thickness)
        y += 18
