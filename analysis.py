import math
from collections import deque
from config import IMPACT_DIST_PX


def linear_speed(p0, p1, dt):
    if not p0 or not p1 or dt <= 0:
        return 0.0
    return math.hypot(p1[0] - p0[0], p1[1] - p0[1]) / dt


def angle(p0, p1):
    if not p0 or not p1:
        return None
    return math.atan2(p1[1] - p0[1], p1[0] - p0[0])


def angular_velocity(a0, a1, dt):
    if a0 is None or a1 is None or dt <= 0:
        return 0.0
    da = a1 - a0
    while da > math.pi:
        da -= 2 * math.pi
    while da < -math.pi:
        da += 2 * math.pi
    return da / dt


def detect_impact(speeds, accels, tip_ball_distances, threshold_px=IMPACT_DIST_PX):
    impact_idx = speeds.index(max(speeds))
    for i, d in enumerate(tip_ball_distances):
        if d is not None and d < threshold_px:
            impact_idx = i
            break
    return impact_idx


# ---------------------------------------------------------------------------
# Biomechanics helpers
# ---------------------------------------------------------------------------

def segment_angle(p_left, p_right):
    """Angle (rad) of the line from p_left to p_right relative to horizontal.
    Useful for hip line and shoulder line in the frontal plane."""
    if not p_left or not p_right:
        return None
    return math.atan2(p_right[1] - p_left[1], p_right[0] - p_left[0])


def joint_angle_3pt(a, vertex, b):
    """Interior angle (degrees) at *vertex* formed by segments vertex→a and vertex→b."""
    if not a or not vertex or not b:
        return None
    va = (a[0] - vertex[0], a[1] - vertex[1])
    vb = (b[0] - vertex[0], b[1] - vertex[1])
    dot = va[0] * vb[0] + va[1] * vb[1]
    mag_a = math.hypot(*va)
    mag_b = math.hypot(*vb)
    if mag_a < 1e-9 or mag_b < 1e-9:
        return None
    cos_val = max(-1.0, min(1.0, dot / (mag_a * mag_b)))
    return math.degrees(math.acos(cos_val))


def midpoint(p1, p2):
    if not p1 or not p2:
        return None
    return ((p1[0] + p2[0]) / 2.0, (p1[1] + p2[1]) / 2.0)


class RunningMedian:
    """Running median over a fixed window (for stick-length calibration)."""
    def __init__(self, win=15):
        self.buf = deque(maxlen=win)

    def update(self, val):
        if val is not None and val > 0:
            self.buf.append(val)
        if not self.buf:
            return None
        s = sorted(self.buf)
        return s[len(s) // 2]
