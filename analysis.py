import bisect
import math
from collections import deque

from config import IMPACT_DIST_PX


def wrap_angle(da):
    """Wrap angle difference into (-pi, pi]."""
    while da > math.pi:
        da -= 2 * math.pi
    while da < -math.pi:
        da += 2 * math.pi
    return da


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
    return wrap_angle(a1 - a0) / dt


def find_impact_idx(speeds, tip_ball_distances, threshold_px=IMPACT_DIST_PX):
    """Return frame index of impact: nearest-to-ball frame if detectable, else peak-speed frame."""
    impact_idx = max(range(len(speeds)), key=lambda i: speeds[i]) if speeds else 0
    for i, d in enumerate(tip_ball_distances):
        if d is not None and d < threshold_px:
            impact_idx = i
            break
    return impact_idx


# ---------------------------------------------------------------------------
# Biomechanics helpers
# ---------------------------------------------------------------------------

def segment_angle(p_left, p_right):
    """Angle (rad) of the line from p_left to p_right relative to horizontal."""
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
    """Running median over a fixed window using a sorted list for O(log n) updates."""
    def __init__(self, win=15):
        self._maxlen = win
        self._buf = deque()
        self._sorted = []

    def update(self, val):
        if val is None or val <= 0:
            return self._sorted[len(self._sorted) // 2] if self._sorted else None
        if len(self._buf) == self._maxlen:
            evicted = self._buf.popleft()
            idx = bisect.bisect_left(self._sorted, evicted)
            if idx < len(self._sorted):
                self._sorted.pop(idx)
        self._buf.append(val)
        bisect.insort(self._sorted, val)
        return self._sorted[len(self._sorted) // 2]
