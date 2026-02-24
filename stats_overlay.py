import cv2
from config import COLOR_TEXT

def draw_stats(img, frame_idx, v, vmax, wmax, amax, swing_time):
    lines = [
        f"Frame: {frame_idx}",
        f"Speed: {v:.2f} m/s",
        f"Max speed: {vmax:.2f} m/s",
        f"Max angular vel: {wmax:.2f} rad/s",
        f"Max accel: {amax:.2f} m/s²",
        f"Swing duration: {swing_time:.3f} s",
        "SPACE pause | ESC exit"
    ]
    y = 28
    for l in lines:
        cv2.putText(img, l, (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.65, COLOR_TEXT, 2)
        y += 26
